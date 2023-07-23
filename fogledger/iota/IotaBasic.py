from fogbed import (
    Container, VirtualInstance, FogbedExperiment
)
from .NodeConfig import NodeConfig
from .CoordConfig import CoordConfig
from .SpammerConfig import SpammerConfig
from typing import List
from typing import Dict
import os
import json
import time
import subprocess
import pkg_resources


class IotaBasic:
    def __init__(
        self,
        exp: FogbedExperiment,
        prefix: str = 'cloud',
        conf_nodes: List[NodeConfig] = [],
        conf_coord: CoordConfig = None,
        conf_spammer: SpammerConfig = None
    ) -> None:
        self.ledgers: List[VirtualInstance] = []
        self.nodes: Dict[str, Container] = {}
        self.exp = exp
        self.prefix = prefix
        self.conf_nodes = conf_nodes
        self.conf_coord = conf_coord
        self.conf_spammer = conf_spammer
        self.startScript()
        self.createContainers()

    def add_ledger(self, prefix: str, nodes: List[Container]):
        ledger = self.exp.add_virtual_instance(f'{prefix}')
        self._create_nodes(ledger, nodes)
        self.ledgers.append(ledger)
        return self.ledgers

    def _create_nodes(self, ledger: VirtualInstance, nodes: List[Container]):
        for node in nodes:
            self.exp.add_docker(
                container=node,
                datacenter=ledger)
            self.nodes[f'{self.prefix}_{ledger.label}_{node.name}'] = node
        return nodes

    @staticmethod
    def read_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    def startScript(self):
        print("starting script...")
        path_script = pkg_resources.resource_filename('fogledger', 'data')
        path_private_tangle = os.path.join(path_script, "private-tangle.sh")
        subprocess.run(["chmod", "+x", path_private_tangle])
        subprocess.run(["/bin/bash", path_private_tangle, "install"], check=True, cwd=path_script)
        print("finished script...")

    def createContainers(self):
        ### NODES ###
        for index, node_conf in enumerate(self.conf_nodes):
            name = node_conf.name
            ip = node_conf.ip
            port_bindings = node_conf.port_bindings
            
            node = Container(
                name=name,
                dimage='larsid/fogbed-iota-node:v3.0.0-beta',
                ip=ip,
                port_bindings=port_bindings,
                ports=['14265', '8081', '1883', '15600', '14626/udp']
            )
            self.add_ledger(f'ledger-{name}{index}', [node])

        ### COO ###
        coo = Container(
            name=self.conf_coord.name,
            ip = self.conf_coord.ip,
            port_bindings = self.conf_coord.port_bindings,
            dimage='larsid/fogbed-iota-node:v3.0.0-beta',
            environment={'COO_PRV_KEYS': ''},
            ports=['15600']
        )
        self.add_ledger(f'ledger-{coo.name}', [coo])

        ### spammer ###
        spammer = Container(
            name= self.conf_spammer.name,
            ip = self.conf_spammer.ip,
            port_bindings = self.conf_spammer.port_bindings,
            dimage='larsid/fogbed-iota-node:v3.0.0-beta',
            ports=['15600', '14626/udp']
        )
        self.add_ledger(f'ledger-{spammer.name}', [spammer])

    def searchNode(self, node_name: str):
        for node in self.nodes.values():
            if node.name == node_name:
                return node
    
    def configureNodes(self):
        print("\nConfiguring nodes...")
        file_path = os.path.join("/tmp", "iota")
        config_file_coor = json.loads(IotaBasic.read_file(f"{file_path}/config/config-coo.json"))
        config_file_spammer = json.loads(IotaBasic.read_file(f"{file_path}/config/config-spammer.json"))
        config_file_node = json.loads(IotaBasic.read_file(f"{file_path}/config/config-node.json"))
        for node in self.nodes.values():
            json_data = {}
            if(node.name == self.conf_coord.name):
                json_data = config_file_coor
                json_data["coordinator"]["interval"] = self.conf_coord.interval
            elif(node.name == self.conf_spammer.name):
                json_data = config_file_spammer
                json_data["spammer"]["message"] = self.conf_spammer.message
            else:
                json_data = config_file_node
            json_data["node"]["alias"] = node.name
            updated_data = json.dumps(json_data)
            node.cmd(f"echo \'{updated_data}\' | jq . > /app/config.json")
        print("Nodes configured! ✅")

    # P2P identities are generated for each node
    def setupIdentities(self):
        print("\nGenerating P2P identities for each node")
        for node in self.nodes.values():
            node.cmd(f'./hornet tool p2pidentity-gen > {node.name}.identity.txt')
        print("P2P identities generated! ✅")

    # Extracts the peerID from the identity file
    def extractPeerID(self):
        print("\nExtracting peerID from the identity file")
        for node_ext in self.nodes.values():
            peerID = node_ext.cmd(
                f'cat {node_ext.name}.identity.txt | awk -F : \'{{if ($1 ~ /PeerID/) print $2}}\' | sed "s/ \+//g" | tr -d "\n" | tr -d "\r"').strip("> >")
            for node_int in self.nodes.values():
                if node_int.name != node_ext.name:
                    json_data = node_int.cmd(f'cat /app/peering.json').strip("> >")
                    json_data = json.loads(json_data)
                    json_data["peers"].append({"alias": node_ext.name, "multiAddress": f"/dns/{node_ext.ip}/tcp/15600/p2p/{peerID}"})
                    updated_data = json.dumps(json_data)
                    node_int.cmd(f"echo \'{updated_data}\' | jq . > /app/peering.json")
        print("peerID extracted! ✅")

    # Sets the Coordinator up by creating a key pair
    def setupCoordinator(self):
        print("\nSetting up the Coordinator")
        coo_key_pair_file = "coo-milestones-key-pair.txt"
        coo = self.searchNode(self.conf_coord.name)
        if coo is not None:
            coo.cmd('mkdir -p /app/coo-state')
            coo.cmd(f'./hornet tool ed25519-key > {coo_key_pair_file}')
            COO_PRV_KEYS = coo.cmd(
                f'cat {coo_key_pair_file} | awk -F : \'{{if ($1 ~ /private key/) print $2}}\' | sed "s/ \+//g" | tr -d "\n" | tr -d "\r"').strip("> >")
            coo.cmd(f'export COO_PRV_KEYS={COO_PRV_KEYS}')
            coo_public_key = coo.cmd(
                f'cat {coo_key_pair_file} | awk -F : \'{{if ($1 ~ /public key/) print $2}}\' | sed "s/ \+//g" | tr -d "\n" | tr -d "\r"').strip("> >")
            file_path = os.path.join("/tmp", "iota")
            command = f'echo {coo_public_key} > {file_path}/coo-milestones-public-key.txt'
            os.system(command)
            for node in self.nodes.values():
                json_data = node.cmd(f'cat /app/config.json').strip("> >")
                json_data = json.loads(json_data)
                json_data["protocol"]["publicKeyRanges"][0]["key"] = coo_public_key
                updated_data = json.dumps(json_data)
                node.cmd(f"echo \'{updated_data}\' | jq . > /app/config.json")
            print("Coordinator set up! ✅")
        else:
            print("Coordinator not found! ❌")

    def copySnapshotToNodes(self):
        print("\nCopying snapshot to each node")
        # Executar o comando base64 no arquivo full_snapshot.bin e capturar a saída
        file_path = os.path.join("/tmp", "iota", "snapshots", "private-tangle","full_snapshot.bin")
        command = f"base64 {file_path}"
        output = subprocess.run(command, capture_output=True, text=True, shell=True).stdout
        # Salvar a saída em uma variável
        output_b64 = output.strip()
        for node in self.nodes.values():
            node.cmd("mkdir -p /app/snapshots/private-tangle")
            node.cmd(f"echo '{output_b64}' | base64 -d > /app/snapshots/private-tangle/full_snapshot.bin")

        print("Snapshot copied! ✅")

    # Bootstraps the coordinator
    def bootstrapCoordinator(self):
        print("Bootstrapping the Coordinator...")
        # Need to do it again otherwise the coo will not bootstrap
        coo = self.searchNode(self.conf_coord.name)
        if coo is not None:
            coo.cmd(
                f'./hornet --cooBootstrap --cooStartIndex 0 > coo.bootstrap.log &')
            print("Waiting for $bootstrap_tick seconds ... ⏳")
            time.sleep(30)
            bootstrapped = coo.cmd(
                'grep "milestone issued (1)" coo.bootstrap.log | cat')
            if (bootstrapped):
                print("Coordinator bootstrapped successfully! ✅")
                coo.cmd(f'pkill -f "hornet --cooBootstrap --cooStartIndex 0"')
                coo.cmd('rm ./coo.bootstrap.container')
                time.sleep(10)
            else:
                print("Error. Coordinator has not been boostrapped.")
        else:
            print("Coordinator not found! ❌")

    def startContainers(self):
        print("\nStarting the containers...")
        for node in self.nodes.values():
            node.cmd(f'./hornet > {node.name}.log &')
            print(f"\nStarting {node.name}... ⏳")
            time.sleep(3)
            print(f"{node.name} is up and running! ✅")

    def start_network(self):
        print("\nStarting the network...")
        self.configureNodes()
        self.setupIdentities()
        self.extractPeerID()
        self.copySnapshotToNodes()
        self.setupCoordinator()
        self.bootstrapCoordinator()
        self.startContainers()
        print("Network is up and running! ✅")
