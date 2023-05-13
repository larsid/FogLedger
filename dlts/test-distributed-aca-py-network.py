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
    worker1 = exp.add_worker('192.168.0.104')
    worker2 = exp.add_worker('192.168.0.105')

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='indy/tmp/trustees.csv', prefix='cloud',  number_nodes=4)

    acaPy1 = Container(
        name='aca-py1',
        dimage='aca-py',
        port_bindings={3002: 3002, 3001: 3001},
        ports=[3002, 3001],
        environment={
            'ACAPY_GENESIS_FILE': "/pool_transactions_genesis",
            'ACAPY_LABEL': "Aries 1 Agent",
            'ACAPY_WALLET_KEY': "secret",
            'ACAPY_WALLET_SEED': "000000000000000000000000Trustee1",
            'ADMIN_PORT': 3001,
            'AGENT_PORT': 3002
        }
    )
    acaPy2 = Container(
        name='aca-py2',
        dimage='aca-py',
        port_bindings={3002: 3004, 3001: 3003},
        ports=[3002, 3001],
        environment={
            'ACAPY_GENESIS_FILE': "/pool_transactions_genesis",
            'ACAPY_LABEL': "Aries 2 Agent",
            'ACAPY_WALLET_KEY': "secret",
            'ACAPY_WALLET_SEED': "000000000000000000000000Trustee2",
            'ADMIN_PORT': 3001,
            'AGENT_PORT': 3002
        }
    )
    edge1 = exp.add_virtual_instance('edge1')
    edge2 = exp.add_virtual_instance('edge2')


    exp.add_docker(
        container=acaPy2,
        datacenter=edge2)

    agent1 = exp.add_virtual_instance('agent1')
    agent2 = exp.add_virtual_instance('agent2')
    exp.add_docker(
        container=acaPy1,
        datacenter=edge1)
    exp.add_docker(
        container=Container(
            name='agent1',
            dimage='app',
            environment={
                'AGENT_ADDR': acaPy1.ip,
                'AGENT_PORT': 3001
            }
        ),
        datacenter=agent1)
    
    exp.add_docker(
        container=Container(
            name='agent2',
            dimage='app',
            environment={
                'AGENT_ADDR': acaPy2.ip,
                'AGENT_PORT': 3001
            }
        ),
        datacenter=agent2)
    
    add_datacenters_to_worker(worker1, [indyCloud.cli_instance])

    add_datacenters_to_worker(
        worker1, indyCloud.ledgers)
    # add_datacenters_to_worker(
    #     worker2, indyCloud.ledgers[len(indyCloud.ledgers)//2:])
    add_datacenters_to_worker(worker1, [edge1, agent1])
    add_datacenters_to_worker(worker2, [edge2, agent2])
    exp.add_tunnel(worker1, worker2)
    try:
        exp.start()
        indyCloud.start_network()
        time.sleep(10)
        acaPy1.cmd(f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        acaPy1.cmd(f'aca-py start \
        --auto-provision \
        -it http 0.0.0.0 3002 \
        -ot http \
        --admin 0.0.0.0 3001 \
        -e http://{acaPy1.ip}:3002 \
        --wallet-name fogbed  \
        --wallet-type indy \
        --auto-accept-invites \
        --auto-accept-requests \
        --admin-insecure-mode \
        --auto-store-credential \
        --auto-ping-connection \
        --debug-credentials \
        --preserve-exchange-records \
        --auto-respond-credential-proposal \
        --auto-respond-credential-offer \
        --auto-respond-credential-request \
        --auto-store-credential \
        --auto-respond-presentation-proposal \
        --auto-respond-presentation-request \
        --auto-verify-presentation \
        --debug-presentations \
        --log-level info > output.log 2>&1 &')
        
        acaPy2.cmd(f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        acaPy2.cmd(f'aca-py start \
        --auto-provision \
        -it http 0.0.0.0 3002 \
        -ot http \
        --admin 0.0.0.0 3001 \
        -e http://{acaPy2.ip}:3002 \
        --wallet-name fogbed  \
        --wallet-type indy \
        --auto-accept-invites \
        --auto-accept-requests \
        --admin-insecure-mode \
        --auto-store-credential \
        --auto-ping-connection \
        --debug-credentials \
        --preserve-exchange-records \
        --auto-respond-credential-proposal \
        --auto-respond-credential-offer \
        --auto-respond-credential-request \
        --auto-store-credential \
        --auto-respond-presentation-proposal \
        --auto-respond-presentation-request \
        --auto-verify-presentation \
        --debug-presentations \
        --log-level info > output.log 2>&1 &')
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
