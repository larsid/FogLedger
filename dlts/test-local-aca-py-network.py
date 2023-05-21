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
    indyCloud = IndyBasic(
        exp=exp, trustees_path='indy/tmp/trustees.csv', prefix='cloud',  number_nodes=3)
    edge1 = exp.add_virtual_instance('edge')
    edge2 = exp.add_virtual_instance('edge2')

    cloud = exp.add_virtual_instance('cloud')
    create_links(cloud, indyCloud.ledgers)
    exp.add_link(cloud, indyCloud.cli_instance)

    webserverContainer = Container(
        name='webserver',
        dimage='larsid/fogbed-indy-webserver:v1.0.2-beta',
        port_bindings={8000: 9000, 6543: 6543},
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
    exp.add_link(edge1, cloud)
    exp.add_link(edge2, cloud)

    acaPy1 = Container(
        name='aca-py1',
        dimage='aca-py',
        port_bindings={3002: 3002, 3001: 3001},
        ports=[3002, 3001],
        environment={
            'ACAPY_GENESIS_FILE': "/var/lib/indy/fogbed/pool_transactions_genesis",
            'ACAPY_LABEL': "Aries 1 Agent",
            'ACAPY_WALLET_KEY': "secret",
            'ACAPY_WALLET_SEED': "000000000000000000000000Trustee2",
            'ADMIN_PORT': 3001,
            'AGENT_PORT': 3002
        },
        volumes=[
            f'/tmp/indy/cloud:/var/lib/indy/'
        ]
    )
    acaPy2 = Container(
        name='aca-py2',
        dimage='aca-py',
        port_bindings={3002: 3004, 3001: 3003},
        ports=[3002, 3001],
        environment={
            'ACAPY_GENESIS_FILE': "/var/lib/indy/fogbed/pool_transactions_genesis",
            'ACAPY_LABEL': "Aries 2 Agent",
            'ACAPY_WALLET_KEY': "secret",
            'ACAPY_WALLET_SEED': "000000000000000000000000Trustee3",
            'ADMIN_PORT': 3001,
            'AGENT_PORT': 3002
        },
        volumes=[
            f'/tmp/indy/cloud:/var/lib/indy/'
        ]
    )

    agent1 = Container(
        name='agent1',
        dimage='app',
        port_bindings={5001:5001},
        ports=[5001],
        environment={
            'AGENT_ADDR': f"{acaPy1.ip}",
            'AGENT_PORT': 3001
        }
    )

    agent2 = Container(
        name='agent2',
        dimage='app',
        port_bindings={5001:5002},
        ports=[5001],
        environment={
            'AGENT_ADDR': f"{acaPy2.ip}",
            'AGENT_PORT': 3001
        }
    )

    exp.add_docker(
        container=acaPy1,
        datacenter=edge1)

    exp.add_docker(
        container=agent1,
        datacenter=edge1
    )

    exp.add_docker(
        container=acaPy2,
        datacenter=edge2)
    exp.add_docker(
        container=agent2,
        datacenter=edge1
    )
    try:
        exp.start()

        indyCloud.start_network()
        print(webserverContainer.cmd(
            './scripts/start_webserver.sh > output.log 2>&1 &'))
        time.sleep(2)
        acaPy1.cmd(f'aca-py start --endpoint http://{acaPy1.ip}:3002 --admin {acaPy1.ip} 3001 --admin-insecure-mode --auto-accept-intro-invitation-requests --auto-accept-invites --auto-accept-requests --auto-ping-connection --auto-provision --debug-connections --inbound-transport http 0.0.0.0 3002 --log-level INFO --outbound-transport http --public-invites --wallet-name fogbed --wallet-type indy --auto-accept-requests \
          --auto-respond-credential-proposal \
          --auto-respond-credential-offer \
          --auto-respond-credential-request \
          --auto-store-credential \
          --auto-respond-presentation-proposal \
          --auto-respond-presentation-request \
          --auto-verify-presentation > output.log 2>&1 &')
        
        acaPy2.cmd(f'aca-py start --endpoint http://{acaPy2.ip}:3002 --admin {acaPy2.ip} 3001 --admin-insecure-mode --auto-accept-intro-invitation-requests --auto-accept-invites --auto-accept-requests --auto-ping-connection --auto-provision --debug-connections --inbound-transport http 0.0.0.0 3002 --log-level INFO --outbound-transport http --public-invites --wallet-name fogbed --wallet-type indy --auto-accept-invites \
          --auto-respond-credential-proposal \
          --auto-respond-credential-offer \
          --auto-respond-credential-request \
          --auto-store-credential \
          --auto-respond-presentation-proposal \
          --auto-respond-presentation-request \
          --auto-verify-presentation > output.log 2>&1 &')
        exp.start_cli()
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
