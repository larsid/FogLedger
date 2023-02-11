from fogbed import (
    Container, VirtualInstance, FogbedExperiment
)
from typing import List
import csv
import os

class IndyBasic:
    def __init__(
        self,
        exp: FogbedExperiment,
        number_nodes: int = 5
    ) -> None:
        self.ledgers: List[VirtualInstance] = []
        self.nodes: List[Container]  = []
        self.number_nodes: int = number_nodes
        self.exp = exp
        

    def create_ledgers(self):
        self.ledgers = self._create_ledgers(self.number_nodes)
        self.nodes = self._create_nodes()
        return self.ledgers, self.nodes

    def create_links(self,target: VirtualInstance, devices: List[VirtualInstance]):
        for device in devices:
            self.exp.add_link(device, target)

    def _create_ledgers(self, number: int) -> List[VirtualInstance]:
        return [self.exp.add_virtual_instance(f'edge{i+1}') for i in range(number)]


    def _create_nodes(self):
        nodes = []
        for i, ledger in enumerate(self.ledgers):
            name = f'node{i+1}'
            node = Container(
                    name=name, 
                    dimage='indy-node',
                    volumes=[f'{os.path.abspath("indy/tmp/")}:/tmp/indy/', f'{os.path.abspath("indy/scripts/")}:/opt/indy/scripts/']
                )
            nodes.append(node)
            self.exp.add_docker(
                container=node,
                datacenter=ledger)
        return nodes

        

    def start_network(self):
        with open('./indy/tmp/genesis-validators.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Steward name','Validator alias','Node IP address','Node port','Client IP address','Client port','Validator verkey','Validator BLS key'])
            for i, node in enumerate(self.nodes):
                aux = node.cmd(f'init_indy_node Node{i+1} {node.ip} 9701 {node.ip} 9702')
                lines = aux.splitlines()
                writer.writerow([node.name,node.name,node.ip,9701,node.ip,9702,lines[5].split(' ')[3], lines[9].split(' ')[4]])
        for i, node in enumerate(self.nodes):
                print(node.cmd(f'/opt/indy/scripts/genesis_from_files.py --stewards /tmp/indy/genesis-validators.csv --trustees /tmp/indy/trustees.csv'))