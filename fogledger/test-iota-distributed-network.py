from iota.IotaBasic import (IotaBasic)
from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources,
    CloudResourceModel, EdgeResourceModel, FogResourceModel, VirtualInstance,
    setLogLevel, FogbedDistributedExperiment, Worker, Controller
)

setLogLevel('info')

def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)

if (__name__ == '__main__'):
    exp = FogbedDistributedExperiment()
    worker1 = exp.add_worker('18.116.147.71', controller=Controller('18.116.147.71', 6633))
    worker2 = exp.add_worker('3.130.81.242',  controller=Controller('18.116.147.71', 6633))
    
    config_nodes=[
            {'name': 'node1'},
            {'name': 'node2'},
            {'name': 'node3'},
            {'name': 'node4'},
        ]
    iota = IotaBasic(exp=exp, prefix='fog', nodes=config_nodes)

    add_datacenters_to_worker(worker1, iota.ledgers[:len(iota.ledgers)//2])
    add_datacenters_to_worker(worker2, iota.ledgers[len(iota.ledgers)//2:])
    exp.add_tunnel(worker1, worker2)

    try:
        exp.start()
        iota.start_network()
        print("Experiment started")
        input('Press any key...')

    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
