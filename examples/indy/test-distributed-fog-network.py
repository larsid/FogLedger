from typing import List
from fogbed import (
    Container, VirtualInstance,
    setLogLevel, FogbedDistributedExperiment, Worker, Controller
)
import time
import os

from fogledger.indy import (IndyBasic, Node)
setLogLevel('info')


def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)


if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment(
        controller_ip='larsid01', controller_port=6633)

    # Webserver to check metrics
    fog = exp.add_virtual_instance('fog')

    cloud = exp.add_virtual_instance('cloud')
    instanceWebserver = exp.add_docker(
        container=Container(
            name='webserver',
            dimage='larsid/fogbed-indy-webserver:v1.0.2-beta',
            port_bindings={8000: 8080, 6543: 6543},
            ports=[8000, 6543],
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
            ]
        ),
        datacenter=cloud)
    # ACA-PY to make requests to the ledger
    exp.add_docker(
        container=Container(
            name='test',
            dimage='mnplima/indy-test',
        ),
        datacenter=fog
    )

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='tmp/trustees.csv', config_nodes=[
            Node(name = 'trustee1', ip= '34.18.59.64',
                port_bindings= {9701: 9701, 9702: 9702}),
            Node(name ='trustee2', ip= '34.78.188.172',
                port_bindings= {9701: 9701, 9702: 9702}),
            Node(name = 'trustee4', ip =  '35.197.175.222',
                port_bindings = {9701: 9701, 9702: 9702}),
            Node(name = 'trustee3', ip= '34.146.249.115',
                port_bindings = {9701: 9701, 9702: 9702}),

        ])
    workers = []

    # Add worker for cli
    workerCli = exp.add_worker(f'larsid02')
    workerWeb = exp.add_worker(f'34.95.142.126', port=80,
                               controller=Controller('34.69.7.94', port=80))
    workers.append(workerCli)
    workers.append(exp.add_worker(f'34.18.59.64', port=80,
                   controller=Controller('34.69.7.94', port=80)))
    workers.append(exp.add_worker(f'34.78.188.172', port=80,
                   controller=Controller('34.69.7.94', port=80)))
    workers.append(exp.add_worker(f'35.197.175.222', port=80,
                   controller=Controller('34.69.7.94', port=80)))
    workers.append(exp.add_worker(f'34.146.249.115', port=80,
                   controller=Controller('34.69.7.94', port=80)))

    workerWeb.add(cloud, reachable=True)
    workerCli.add(fog, reachable=True)

    for i in range(1, len(workers)):
        workers[i].add(indyCloud.ledgers[i-1], reachable=True)
    print(indyCloud.nodes)
    for i in range(1, len(workers)):
        exp.add_tunnel(workerWeb, workers[i])

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
