from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel,VirtualInstance,
    setLogLevel
)

setLogLevel('info')

exp = FogbedExperiment()

def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)

def create_devices(number: int) -> List[VirtualInstance]:
    return [exp.add_virtual_instance(f'edge{i+1}') for i in range(number)]

def create_nodes(legers: List[VirtualInstance]):
    nodes = []
    for i, ledger in enumerate(legers):
        name = f'node{i+1}'
        node = Container(
                name=name, 
                dimage='hyperledger/indy-core-baseci:0.0.4',
            )
        nodes.append(node)
        exp.add_docker(
            container=node,
            datacenter=ledger)
    return nodes

if(__name__=='__main__'):

    cloud   = exp.add_virtual_instance('cloud')
    ledgers = create_devices(5)

    nodes = create_nodes(ledgers)
    
    create_links(cloud, ledgers)
    print(nodes)


    try:
        exp.start() 
        
        nodes[0].cmd(f'generate_indy_pool_transactions --nodes 5 --clients 5 --nodeNum 1 --ips {nodes[0].ip},{nodes[1].ip},{nodes[2].ip},{nodes[3].ip},{nodes[4].ip}')
        nodes[1].cmd(f'generate_indy_pool_transactions --nodes 5 --clients 5 --nodeNum 2 --ips {nodes[0].ip},{nodes[1].ip},{nodes[2].ip},{nodes[3].ip},{nodes[4].ip}')
        nodes[2].cmd(f'generate_indy_pool_transactions --nodes 5 --clients 5 --nodeNum 3 --ips {nodes[0].ip},{nodes[1].ip},{nodes[2].ip},{nodes[3].ip},{nodes[4].ip}')
        nodes[3].cmd(f'generate_indy_pool_transactions --nodes 5 --clients 5 --nodeNum 4 --ips {nodes[0].ip},{nodes[1].ip},{nodes[2].ip},{nodes[3].ip},{nodes[4].ip}')
        nodes[4].cmd(f'generate_indy_pool_transactions --nodes 5 --clients 5 --nodeNum 5 --ips {nodes[0].ip},{nodes[1].ip},{nodes[2].ip},{nodes[3].ip},{nodes[4].ip}')
        
        
        nodes[0].cmd(f'start_indy_node Node1 {nodes[0].ip} 9701 {nodes[0].ip} 9702 > output.log 2>&1 &')
        nodes[1].cmd(f'start_indy_node Node2 {nodes[1].ip} 9703 {nodes[1].ip} 9704 > output.log 2>&1 &')
        nodes[2].cmd(f'start_indy_node Node3 {nodes[2].ip} 9705 {nodes[2].ip} 9706 > output.log 2>&1 &')
        nodes[3].cmd(f'start_indy_node Node4 {nodes[3].ip} 9707 {nodes[3].ip} 9708 > output.log 2>&1 &')
        nodes[4].cmd(f'start_indy_node Node5 {nodes[4].ip} 9709 {nodes[4].ip} 9710 > output.log 2>&1 &')
        exp.start_cli()
        input('Press any key...')
    except Exception as ex: 
        print(ex)
    finally:
        exp.stop()
