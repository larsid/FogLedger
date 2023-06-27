from typing import List
from fogbed import (
    Container, VirtualInstance,
    setLogLevel, FogbedDistributedExperiment, Worker, Controller
)
import time
import os

from fogledger.indy import (IndyBasic)
setLogLevel('info')


def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)


if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()

    # Webserver to check metrics
    cloud = exp.add_virtual_instance('cloud')

    # ACA-PY to make requests to the ledger
    exp.add_docker(
        container=Container(
            name='test',
            dimage='mnplima/indy-test',
        ),
        datacenter=cloud
    )

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='tmp/trustees.csv', prefix='ledger',  nodes_number=4)
    workers = []

    # Add worker for cli
    workerServer = exp.add_worker(f'larsid02')
    workers.append(workerServer)
    workers.append(exp.add_worker(f'35.197.175.222', port=80, controller= Controller('34.69.7.94', port=6633)))
    workers.append(exp.add_worker(f'34.163.250.239', port=80, controller= Controller('34.69.7.94', port=6633)))
    workers.append(exp.add_worker(f'35.199.100.104', port=80, controller= Controller('34.69.7.94', port=6633)))
    workers.append(exp.add_worker(f'35.200.43.131', port=80, controller= Controller('34.69.7.94', port=6633)))
    
    workerServer.add(cloud, reachable=True)
    for i in range(1, len(workers)):
        indyCloud.ledgers[i-1].containers[next(iter(indyCloud.ledgers[i-1].containers))].ip = workers[i].ip
        indyCloud.ledgers[i-1].containers[next(iter(indyCloud.ledgers[i-1].containers))].ports = [9701, 9702]
        indyCloud.ledgers[i-1].containers[next(iter(indyCloud.ledgers[i-1].containers))].bindings = {9701:9701, 9702:9702}
        indyCloud.ledgers[i-1].containers
        workers[i].add(indyCloud.ledgers[i-1], reachable=True)
    # for i in range(1, len(workers)):
    #     exp.add_tunnel(workerServer, workers[i])

    try:
        exp.start()
        indyCloud.start_network()
        time.sleep(10)
        cloud.containers['test'].cmd(f"echo '{indyCloud.genesis_content}' > /indy-sdk/samples/python/src/genesis.txt")
        cloud.containers['test'].cmd(f"python -m src.test_transactions")
        print(cloud.containers['test'].cmd(f"python -m src.parse_result"))

        
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
