from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel, VirtualInstance,
    setLogLevel,
)
from indy.indy import (IndyBasic)
import time
import os

setLogLevel('info')


def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)


if (__name__ == '__main__'):

    exp = FogbedExperiment()

    # Define Indy network in cloud
    indyCloud = IndyBasic(exp=exp, trustees_path = 'indy/tmp/trustees.csv', prefix='cloud',  number_nodes=3)

    
    cloud = exp.add_virtual_instance('cloud')
    create_links(cloud, indyCloud.ledgers)
    exp.add_link(cloud, indyCloud.cli_instance)

    # Define Indy network in fog
    indyFog = IndyBasic(exp=exp, prefix='fog',  number_nodes=3)
    fog = exp.add_virtual_instance('fog')
    create_links(fog, indyFog.ledgers)

    webserverContainer = Container(
        name='webserver',
        dimage='mnplima/fogbed-indy-webserver:latest',
        port_bindings={8000: 9000, 6543:6543},
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
            'GENESIS_FILE': "/var/lib/indy/fogbed/pool_transactions_genesis"
        },
        volumes=[
            f'/tmp/indy/cloud:/var/lib/indy/'
        ]
    )
    instanceWebserver = exp.add_docker(
        container=webserverContainer,
        datacenter=cloud)

    try:
        exp.start()

        indyCloud.start_network()
        indyFog.start_network()

        time.sleep(10)
        print(webserverContainer.cmd('./scripts/start_webserver.sh > output.log 2>&1 &'))

        exp.start_cli()
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()


