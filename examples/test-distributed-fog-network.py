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
        exp=exp, trustees_path='tmp/trustees.csv', prefix='ledger',  config_nodes=[
            {'name': 'trustee1', 'ip': '34.18.59.64'},
            {'name': 'trustee2', 'ip': '34.78.188.172'},
            {'name': 'trustee3', 'ip': '34.146.249.115'},
        ])
    workers = []

    # Add worker for cli
    workerServer = exp.add_worker(f'larsid02')
    workers.append(workerServer)
    workers.append(exp.add_worker(f'34.18.59.64', port=80,
                   controller=Controller('34.69.7.94', port=6633)))
    workers.append(exp.add_worker(f'34.78.188.172', port=80,
                   controller=Controller('34.69.7.94', port=6633)))
    workers.append(exp.add_worker(f'34.146.249.115', port=80,
                   controller=Controller('34.69.7.94', port=6633)))
    workers.append(exp.add_worker(f'35.197.175.222', port=80,
                   controller=Controller('34.69.7.94', port=6633)))

    workerServer.add(cloud, reachable=True)
    for i in range(1, len(workers)):
        indyCloud.nodes[i-1].ip = workers[i].ip
        indyCloud.nodes[i-1].ports = [9701, 9702]
        indyCloud.nodes[i-1].bindings = {9701: 9701, 9702: 9702}
        workers[i].add(indyCloud.ledgers[i-1], reachable=True)
    print(indyCloud.nodes)
    # for i in range(1, len(workers)):
    #     exp.add_tunnel(workerServer, workers[i])

    try:
        exp.start()
        indyCloud.start_network()
        time.sleep(10)
        cloud.containers['test'].cmd(
            f"echo '{indyCloud.genesis_content}' > /indy-sdk/samples/python/src/genesis.txt")
        cloud.containers['test'].cmd(f"python -m src.test_transactions")
        print(cloud.containers['test'].cmd(f"python -m src.parse_result"))

        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
