from fogbed import (
    Container, VirtualInstance, FogbedExperiment
)
from typing import List

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

    def _create_ledgers(self, number: int) -> List[VirtualInstance]:
        return [self.exp.add_virtual_instance(f'edge{i+1}') for i in range(number)]

    def _create_nodes(self):
        nodes = []
        for i, ledger in enumerate(self.ledgers):
            name = f'node{i+1}'
            node = Container(
                    name=name, 
                    dimage='hyperledger/indy-core-baseci:0.0.4',
                    ip=f'10.0.0.{i+2}'
                )
            nodes.append(node)
            self.exp.add_docker(
                container=node,
                datacenter=ledger)
        return nodes

        

    def start_network(self):
        ips = list(map(lambda node: node.ip, self.nodes))
        count_nodes = len(self.nodes)
        ips = ",".join(ips)
        for i, node in enumerate(self.nodes):
            node.cmd(f'generate_indy_pool_transactions --nodes {count_nodes} --clients {count_nodes} --nodeNum {i+1} --ips {ips}')
        for i, node in enumerate(self.nodes):
            node.cmd(f'start_indy_node Node{i+1} {node.ip} 9701 {node.ip} 9702 > output.log 2>&1 &')
        
