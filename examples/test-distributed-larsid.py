from typing import List
from fogbed import (
    Container,
    setLogLevel, FogbedDistributedExperiment
)
import time

from fogledger.indy import (IndyBasic)
setLogLevel('info')


if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()
    # Define Indy network
    indyCloud = IndyBasic(
        exp=exp, trustees_path='tmp/trustees.csv', prefix='ledger',  nodes_number=4)

    # Webserver to check metrics
    fog = exp.add_virtual_instance('fog')
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
            }
        ),
        datacenter=fog)

    workers = []

    # Add worker for cli
    workerDevice = exp.add_worker(f'larsid01')
    workerFog = exp.add_worker(f'larsid02')
    workers.append(workerFog)

    workerFog.add(fog, reachable=True)

    for i in range(2, len(indyCloud.ledgers)+2):
        worker = exp.add_worker(f'larsid{str(i+1).zfill(2)}')
        workers.append(worker)
        worker.add(indyCloud.ledgers[i-2], reachable=True)

    for i in range(len(workers)-1):
        exp.add_tunnel(workers[i], workers[i+1])

    edge = exp.add_virtual_instance('edge')
    exp.add_docker(
        container=Container(
            name='ariesAgent',
            dimage='mnplima/indy-test',
        ),
        datacenter=edge
    )
    workerDevice.add(edge, reachable=True)
    exp.add_tunnel(workerDevice, workerFog)
    try:
        exp.start()
        indyCloud.start_network()
        fog.containers['webserver'].cmd(
            f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        print('Starting Webserver')
        time.sleep(10)
        fog.containers['webserver'].cmd(
            './scripts/start_webserver.sh > output.log 2>&1 &')
        print('Starting aries agent')
        edge.containers['ariesAgent'].cmd(f"echo '{indyCloud.genesis_content}' > /indy-sdk/samples/python/src/genesis.txt")
        print('Making requests in background...')
        print(edge.containers['ariesAgent'].cmd(f"python -m src.test_transactions 2>&1 &"))
        # print(edge.containers['ariesAgent'].cmd(f"python -m src.parse_result"))
        input('Press any key to stop...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
