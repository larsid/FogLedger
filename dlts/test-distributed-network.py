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



def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)


if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()
    worker1 = exp.add_worker('fog1')
    worker2 = exp.add_worker('fog2')

    # Define Indy network in cloud
    indyCloud = IndyBasic(exp=exp, trustees_path = 'indy/tmp/trustees.csv', prefix='cloud',  number_nodes=3)

    add_datacenters_to_worker(worker1, [indyCloud.cli_instance])


    add_datacenters_to_worker(worker1, indyCloud.ledgers[:len(indyCloud.ledgers)//2])
    add_datacenters_to_worker(worker2, indyCloud.ledgers[len(indyCloud.ledgers)//2:])
    exp.add_tunnel(worker1, worker2)
    try:
        exp.start()
        indyCloud.start_network()
        indyCloud.indy_cli.cmd(f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
