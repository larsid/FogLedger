from iota.IotaBasic import IotaBasic
from typing import List
from fogbed import (
    FogbedExperiment, VirtualInstance,
    setLogLevel,
)
import os

setLogLevel('info')

def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)

if (__name__ == '__main__'):
    exp = FogbedExperiment()
    config_nodes=[
            {'name': 'node1'},
            {'name': 'node2'},
            {'name': 'node3'},
            {'name': 'node4'},
        ]
    iota = IotaBasic(exp=exp, prefix='fog', nodes=config_nodes)

    fog = exp.add_virtual_instance('fog')
    
    create_links(fog, iota.ledgers)

    try:
        exp.start()
        iota.start_network()
        print("Experiment started")
        input('Press any key...')

    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
