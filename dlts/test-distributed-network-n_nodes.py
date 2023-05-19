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
    worker1 = exp.add_worker('larsid01')
    worker2 = exp.add_worker('larsid02')
    worker3 = exp.add_worker('larsid03')
    worker4 = exp.add_worker('larsid04')

    # Define Indy network in cloud
    indyCloud = IndyBasic(exp=exp, trustees_path = 'indy/tmp/trustees.csv', prefix='cloud',  number_nodes=4)
    workers = []
    for i in range(len(indyCloud.ledgers)):
        worker = exp.add_worker(f'larsid{str(i+1).zfill(2)}')
        workers.append(worker)
        worker.add(indyCloud.ledgers[i], reachable=True)
        
    workers[0](worker1, [indyCloud.cli_instance])
    for i, worker in enumerate(workers):
        for j in range(i+1, len(workers)):
            exp.add_tunnel(worker, workers[j])

    try:
        exp.start()
        indyCloud.start_network()
        indyCloud.indy_cli.cmd(f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
