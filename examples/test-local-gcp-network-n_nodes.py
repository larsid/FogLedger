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
    instanceWebserver = exp.add_docker(
        container=Container(
            name='webserver',
            dimage='larsid/fogbed-indy-webserver:v1.0.2-beta',
            port_bindings={8000: 8080, 6543: 6543},
            environment={
                'MAX_FETCH': 50000,
                'RESYNC_TIME': 120,
                'WEB_ANALYTICS': True,
                'REGISTER_NEW_DIDS': True,
                'LEDGER_INSTANCE_NAME': "fogbed",
                'INFO_SITE_TEXT': "Node Container @ GitHub",
                'INFO_SITE_URL': "https://github.com/hyperledger/indy-node-container",
                'LEDGER_SEED': "000000000000000000000000Trustee1",
                'GENESIS_FILE': "/pool_transactions_genesis"
            },
            volumes=[
                f'tmp:/var/log/indy',
            ]),
        datacenter=cloud)

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='examples/tmp/trustees.csv', config_nodes=[
            {'name': 'node1'},
            {'name': 'node2'},
            {'name': 'node3'},
            {'name': 'node4'},
        ])

    exp.add_docker(
        container=Container(
            name='test',
            dimage='mnplima/indy-test',
        ),
        datacenter=cloud
    )
    workers = []

    # Add worker for cli
    workerServer = exp.add_worker(f'10.132.0.3')
    workers.append(exp.add_worker(f'10.132.0.4'))
    workers.append(exp.add_worker(f'10.132.0.5'))
    workers.append(exp.add_worker(f'10.132.0.6'))
    workers.append(exp.add_worker(f'10.132.0.7'))

    workerServer.add(cloud, reachable=True)
    for i in range(0, len(workers)):
        workers[i].add(indyCloud.ledgers[i], reachable=True)
    for i in range(0, len(workers)):
        exp.add_tunnel(workerServer, workers[i])

    try:
        exp.start()
        indyCloud.start_network()
        cloud.containers['webserver'].cmd(
            f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        print('Starting Webserver')
        time.sleep(10)
        cloud.containers['webserver'].cmd(
            './scripts/start_webserver.sh > output.log 2>&1 &')
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
