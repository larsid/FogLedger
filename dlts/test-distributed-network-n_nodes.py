from typing import List
from fogbed import (
    Container, VirtualInstance,
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

    webserverContainer = Container(
        name='webserver',
        dimage='larsid/fogbed-indy-webserver:v1.0.2-beta',
        port_bindings={8000: 80, 6543: 6543},
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
    )
    cloud = exp.add_virtual_instance('cloud')
    instanceWebserver = exp.add_docker(
        container=webserverContainer,
        datacenter=cloud)

    # Define Indy network in cloud
    indyCloud = IndyBasic(exp=exp, trustees_path = 'indy/tmp/trustees.csv', prefix='ledger',  number_nodes=2)
    workers = []

    # Add worker for cli
    workerServer = exp.add_worker(f'larsid02')
    workers.append(workerServer)

    workerServer.add(indyCloud.cli_instance)
    workerServer.add(cloud, reachable=True)
    for i in range(2,len(indyCloud.ledgers)+2):
        worker = exp.add_worker(f'larsid{str(i+1).zfill(2)}')
        workers.append(worker)
        worker.add(indyCloud.ledgers[i-2], reachable=True)
        
    for i, worker in enumerate(workers):
        for j in range(i+1, len(workers)):
            exp.add_tunnel(worker, workers[j])

    try:
        exp.start()
        indyCloud.start_network()
        webserverContainer.cmd(f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        print(webserverContainer.cmd('./scripts/start_webserver.sh > output.log 2>&1 &'))
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
