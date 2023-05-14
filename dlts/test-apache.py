from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel, VirtualInstance,
    setLogLevel, FogbedDistributedExperiment, Worker
)
import time
import os

from indy.indy import (IndyBasic)
setLogLevel('info')


if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()
    worker1 = exp.add_worker('fog1')
    worker2 = exp.add_worker('fog2')

    # Define apache
    apache = Container(
        name='apache',
        dimage='httpd',
        port_bindings={80: 80},
        ports=[80],
        dcmd='httpd-foreground'
    )
    edge1 = exp.add_virtual_instance('edge1')
    client1 = exp.add_virtual_instance('client1')
    client2 = exp.add_virtual_instance('client2')
    exp.add_docker(
        container=apache,
        datacenter=edge1
    )

    exp.add_docker(
        container=Container(
            name='cli1',
            dimage='ubuntu'
        ), 
        datacenter=client1
    )

    exp.add_docker(
        container=Container(
            name='cli2',
            dimage='ubuntu'
        ), 
        datacenter=client2
    )

    worker1.add(edge1, reachable=True)
    worker1.add(client1, reachable=True)
    worker2.add(client2, reachable=True)    
    
    exp.add_tunnel(worker1, worker2)
    try:
        exp.start()

        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()