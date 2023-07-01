from fogbed import (
    Container, VirtualInstance, FogbedDistributedExperiment
)
from typing import List
import csv
import os
import uuid
import re
import numpy


class IndyBasic:
    def __init__(
        self,
        exp: FogbedDistributedExperiment,
        trustees_path='tmp/trustees.csv',
        config_nodes: List[dict] = []
    ) -> None:
        self.ledgers: List[VirtualInstance] = []
        self.nodes: List[Container] = []
        self.exp = exp
        self.genesis_content = ''
        self.trustees_path = trustees_path
        self._create_ledgers(config_nodes)
        self._create_dir()

    def _create_ledgers(self, config_nodes: List[dict] = []):
        self.ledgers = self._create_virtual_instances(config_nodes)
        self.nodes = self._create_nodes(config_nodes)
        return self.ledgers, self.nodes

    def create_links(self, target: VirtualInstance, devices: List[VirtualInstance]) -> None:
        for device in devices:
            self.exp.add_link(device, target)

    def _create_virtual_instances(self, config_nodes: List[dict] = []) -> List[VirtualInstance]:
        return [self.exp.add_virtual_instance(config['name']) for i, config in enumerate(config_nodes)]

    def _create_nodes(self, config_nodes: List[dict]) -> List[Container]:
        nodes = []
        for i, ledger in enumerate(self.ledgers):

            name = config_nodes[i]['name'] if (
                "name" in config_nodes[i]) else str(i)
            
            ip = config_nodes[i]['ip'] if ("ip" in config_nodes[i]) else None
            
            port_bindings = config_nodes[i]['port_bindings'] if ("port_bindings" in config_nodes[i]) else {}
            
            node = Container(
                name=name,
                dimage='larsid/fogbed-indy-node:v1.0.2-beta',
                ip=ip,
                port_bindings=port_bindings
            )
            nodes.append(node)
            self.exp.add_docker(
                container=node,
                datacenter=ledger)
        return nodes

    def _create_dir(self) -> None:
        if not os.path.exists("tmp/indy/"):
            os.makedirs("tmp/indy/")

    def _get_content_trustees(self) -> str:
        content = ''
        with open(self.trustees_path, newline='') as csvfile:
            # read csv file and save in a string
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                content += ','.join(row) + '\n'
        return content

    def start_network(self) -> None:
        print('Initializing Network... ⏳')

        genesis_file_name = uuid.uuid4()
        array_genesis = numpy.array([['Steward name', 'Validator alias', 'Node IP address', 'Node port', 'Client IP address',
                                    'Client port', 'Validator verkey', 'Validator BLS key', 'Validator BLS POP', 'Steward DID', 'Steward verkey']])
        for i, node in enumerate(self.nodes):
            print(f'Configuring {node.name}... ⏳')
            seed = node.cmd("pwgen -s 32 1")
            node.cmd(f"printf 'wallet create fogbed key=key \nexit\n' | indy-cli")
            info_cli = node.cmd(
                f"printf 'wallet open fogbed key=key\n did new seed={seed}\nexit\n' | indy-cli")
            print(info_cli)
            matches = re.findall(
                r'Did "(\S+)" has been created with "(\S+)" verkey', info_cli)
            did = ''
            verkey = ''
            print(matches)
            if matches:
                did = matches[0][0]
                verkey = matches[0][1]
            aux = node.cmd(
                f'init_indy_node {node.name} {node.ip} 9701 {node.ip} 9702')
            print(aux)
            lines = aux.splitlines()

            array_genesis = numpy.append(array_genesis, [[node.name, node.name, node.ip, 9701, node.ip, 9702, lines[5].split(
                ' ')[3], lines[9].split(' ')[4], lines[10].split(' ')[7], did, verkey]], axis=0)
            print(f'Configured {node.name} ✅')
        print('Configured Nodes ✅')
        # create a list of formatted rows
        rows = [','.join(str(field) for field in row) for row in array_genesis]

        # join the rows with a newline separator to create the CSV text
        text = '\n'.join(rows)
        trustees_content = self._get_content_trustees()

        for i, node in enumerate(self.nodes):
            print(f'Starting {node.name}... ⏳')
            node.cmd(f'echo "{text}" >> /tmp/indy/{genesis_file_name}.csv')
            node.cmd(f'echo "{trustees_content}" >> /tmp/indy/trustees.csv')
            node.cmd(
                f'/opt/indy/scripts/genesis_from_files.py --stewards /tmp/indy/{genesis_file_name}.csv --trustees /tmp/indy/trustees.csv')
            node.cmd(
                f'cp domain_transactions_genesis /var/lib/indy/$NETWORK_NAME/ && cp pool_transactions_genesis /var/lib/indy/$NETWORK_NAME/')
            node.cmd(
                f'start_indy_node {node.name} 0.0.0.0 9701 0.0.0.0 9702 > output.log 2>&1 &')
            print(f'Started {node.name} ✅')
        # save genesis content in memory
        self.genesis_content = self.nodes[0].cmd(
            'cat pool_transactions_genesis')
        print('Indy Network Started ✅')
