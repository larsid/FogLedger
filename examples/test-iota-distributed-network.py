from fogledger.iota.IotaBasic import (IotaBasic)
from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel, VirtualInstance,
    setLogLevel, FogbedDistributedExperiment, Worker
)

setLogLevel('info')

def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)

if (__name__ == '__main__'):
    exp = FogbedDistributedExperiment()
    worker1 = exp.add_worker('fog1')
    worker2 = exp.add_worker('fog2')
    nodes = ['node1', 'node2', 'node3', 'node4']
    
    iota = IotaBasic(exp=exp, prefix='fog', nodes=nodes)

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
