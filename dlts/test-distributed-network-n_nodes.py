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

    # Webserver to check metrics
    cloud = exp.add_virtual_instance('cloud')
    instanceWebserver = exp.add_docker(
        container=Container(
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
        ),
        datacenter=cloud)

    # ACA-PY to make requests to the ledger
    exp.add_docker(
        container=Container(
            name='aca-py',
            dimage='mnplima/fogbed-aca-py',
            port_bindings={3002: 3002, 3001: 8080},
            ports=[3002, 3001],
            environment={
                'ACAPY_GENESIS_FILE': "/pool_transactions_genesis",
                'ACAPY_LABEL': "Aries Agent FogLedger",
                'ACAPY_WALLET_KEY': "secret",
                'ACAPY_WALLET_SEED': "000000000000000000000000Trustee2",
                'ADMIN_PORT': 3001,
                'AGENT_PORT': 3002
            }
        ),
        datacenter=cloud
    )

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='indy/tmp/trustees.csv', prefix='ledger',  number_nodes=4)
    workers = []

    # Add worker for cli
    workerServer = exp.add_worker(f'larsid02')
    workers.append(workerServer)

    workerServer.add(indyCloud.cli_instance)
    workerServer.add(cloud, reachable=True)
    for i in range(2, len(indyCloud.ledgers)+2):
        worker = exp.add_worker(f'larsid{str(i+1).zfill(2)}')
        workers.append(worker)
        worker.add(indyCloud.ledgers[i-2], reachable=True)

    for i in range(1, len(workers)):
        exp.add_tunnel(workerServer, workers[i])
    try:
        exp.start()
        indyCloud.start_network()
        cloud.containers['webserver'].cmd(
            f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        print('Starting Webserver')
        cloud.containers['webserver'].cmd(
            './scripts/start_webserver.sh > output.log 2>&1 &')

        cloud.containers['aca-py'].cmd(
            f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        time.sleep(5)
        print('Starting ACA-PY')
        cloud.containers['aca-py'].cmd(f"aca-py start \
            --auto-provision \
            -ot http \
            -it http 0.0.0.0 3002 \
            --admin 0.0.0.0 3001 \
            -e http://{cloud.containers['aca-py'].ip}:3002 \
            --admin 0.0.0.0 3001 \
            --wallet-name fogbed  \
            --wallet-type indy \
            --admin-insecure-mode \
            --debug-credentials \
            --debug-presentations \
            --log-level info > output.log 2>&1 &"
                                       )
        time.sleep(10)
        print('Registering NYM')
        for i in (range(40)):
            cloud.containers['aca-py'].cmd(f"curl -X 'POST' \
                'http://{cloud.containers['aca-py'].ip}:3001/ledger/register-nym?did=LnXR1rPnncTPZvRdmJKhJQ&verkey=BnSWTUQmdYCewSGFrRUhT6LmKdcCcSzRGqWXMPnEP168&role=TRUSTEE' \
                -H 'accept: application/json'")
        status_ledgers = cloud.containers['webserver'].cmd(f"curl http://{cloud.containers['webserver'].ip}:8000/status/text")
        # Save status ledgers in text file
        with open('status_ledgers.txt', 'w') as f:
            f.write(status_ledgers)
        print('Status ledgers saved in status_ledgers.txt')

        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
