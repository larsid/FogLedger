from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel,VirtualInstance,
    setLogLevel, FogbedDistributedExperiment, Worker
)

from indy.indy import (IndyBasic)
setLogLevel('info')


def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)

def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)


if(__name__=='__main__'):

    exp = FogbedDistributedExperiment(controller_ip='192.168.0.103', controller_port=6633)
    worker1 = exp.add_worker(ip='192.168.0.103')
    worker2 = exp.add_worker(ip='192.168.0.101')

     # Define Indy network in cloud
    indyCloud = IndyBasic(exp=exp, number_nodes=8)
    cloud = exp.add_virtual_instance('cloud')
    ledgers, nodes = indyCloud.create_ledgers('cloud')
    # create_links(cloud, ledgers)
    # exp.add_link(cloud, indyCloud.cli_instance)

    # Define Indy network in fog
    # indyFog = IndyBasic(exp=exp, number_nodes=3)
    # fog = exp.add_virtual_instance('fog')
    # ledgers, nodes = indyFog.create_ledgers('fog')
    # create_links(fog, ledgers)

    add_datacenters_to_worker(worker1, [cloud])
    add_datacenters_to_worker(worker2, ledgers)
    add_datacenters_to_worker(worker1, [indyCloud.cli_instance])
    exp.add_tunnel(worker1, worker2)

    try:
        exp.start() 

        indyCloud.start_network()
        # indyFog.start_network()
        input('Press any key...')
    except Exception as ex: 
        print(ex)
    finally:
        exp.stop()
