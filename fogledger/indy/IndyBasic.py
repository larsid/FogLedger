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
        number_nodes: int = 4,
        prefix: str = 'node',
        trustees_path='tmp/trustees.csv'
    ) -> None:
        self.ledgers: List[VirtualInstance] = []
        self.nodes: List[Container] = []
        self.exp = exp
        self.genesis_content = ''
        self.genesis_file_path = ''
        self.trustees_path = trustees_path
        self._create_ledgers(prefix, number_nodes)
        self._create_dir()

    def _create_ledgers(self, prefix: str = 'node', number_nodes: int = 4):
        self.ledgers = self._create_virtual_instances(number_nodes, prefix)
        self.nodes = self._create_nodes(prefix)
        return self.ledgers, self.nodes

    def create_links(self, target: VirtualInstance, devices: List[VirtualInstance]) -> None:
        for device in devices:
            self.exp.add_link(device, target)

    def _create_virtual_instances(self, number: int, prefix: str) -> List[VirtualInstance]:
        return [self.exp.add_virtual_instance(f'{prefix}{i+1}') for i in range(number)]

    def _create_nodes(self, prefix: str) -> List[Container]:
        nodes = []

        # Cli to create seeds to nodes
        self.cli_instance = self.exp.add_virtual_instance(f'{prefix}_cli')
        self.indy_cli = Container(
            name=f'{prefix}_cli',
            dimage='larsid/fogbed-indy-cli:v1.0.2-beta'
        )
        self.exp.add_docker(
            container=self.indy_cli,
            datacenter=self.cli_instance)
        for i, ledger in enumerate(self.ledgers):
            name = f'{prefix}{i+1}'
            node = Container(
                name=name,
                dimage='larsid/fogbed-indy-node:v1.0.2-beta',
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
        print('Starting indy network...')
        # Remove old files
        for i, node in enumerate(self.nodes):
            node.cmd("rm -rf /var/lib/indy/$NETWORK_NAME")

        self.indy_cli.cmd(
            f"printf 'wallet create fogbed key=key \nexit\n' | indy-cli")
        genesis_file_name = uuid.uuid4()
        array_genesis = numpy.array([['Steward name', 'Validator alias', 'Node IP address', 'Node port', 'Client IP address',
                                    'Client port', 'Validator verkey', 'Validator BLS key', 'Validator BLS POP', 'Steward DID', 'Steward verkey']])
        for i, node in enumerate(self.nodes):
            seed = self.indy_cli.cmd("pwgen -s 32 1")
            info_cli = self.indy_cli.cmd(
                f"printf 'wallet open fogbed key=key\n did new seed={seed}\nexit\n' | indy-cli")
            matches = re.findall(
                r'Did "(\S+)" has been created with "(\S+)" verkey', info_cli)
            did = ''
            verkey = ''
            if matches:
                did = matches[0][0]
                verkey = matches[0][1]
            aux = node.cmd(
                f'init_indy_node {node.name} {node.ip} 9701 {node.ip} 9702')
            lines = aux.splitlines()
            array_genesis = numpy.append(array_genesis, [[node.name, node.name, node.ip, 9701, node.ip, 9702, lines[5].split(
                ' ')[3], lines[9].split(' ')[4], lines[10].split(' ')[7], did, verkey]], axis=0)

        # create a list of formatted rows
        rows = [','.join(str(field) for field in row) for row in array_genesis]

        # join the rows with a newline separator to create the CSV text
        text = '\n'.join(rows)
        trustees_content = self._get_content_trustees()
        self.genesis_file_path = f'tmp/indy/{genesis_file_name}.csv'
        numpy.savetxt(self.genesis_file_path, array_genesis,
                      delimiter=',', fmt='%s')

        for i, node in enumerate(self.nodes):
            node.cmd(f'echo "{text}" >> /tmp/indy/{genesis_file_name}.csv')
            node.cmd(f'echo "{trustees_content}" >> /tmp/indy/trustees.csv')
            node.cmd(
                f'/opt/indy/scripts/genesis_from_files.py --stewards /tmp/indy/{genesis_file_name}.csv --trustees /tmp/indy/trustees.csv')
            node.cmd(
                f'cp domain_transactions_genesis /var/lib/indy/$NETWORK_NAME/ && cp pool_transactions_genesis /var/lib/indy/$NETWORK_NAME/')
            node.cmd(
                f'start_indy_node {node.name} {node.ip} 9701 {node.ip} 9702 > output.log 2>&1 &')

        # save genesis content in memory
        self.genesis_content = self.nodes[0].cmd('cat pool_transactions_genesis')
