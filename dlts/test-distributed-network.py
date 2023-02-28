from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel,VirtualInstance,
    setLogLevel, FogbedDistributedExperiment, Worker
)
import time
from indy.indy import (IndyBasic)
setLogLevel('info')


def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)

def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)


if(__name__=='__main__'):

    exp = FogbedDistributedExperiment(controller_ip='192.168.0.104', controller_port=6633)
    worker1 = exp.add_worker(ip='192.168.0.104')
    worker2 = exp.add_worker(ip='192.168.0.105')
    webserver = exp.add_virtual_instance('webserver')
    webserverContainer = Container(
            name='webserver', 
            dimage='webserver',
            port_bindings={9000: 9000},
            environment={
                'MAX_FETCH':50000,
                'RESYNC_TIME':120,
                'REGISTER_NEW_DIDS':True,
                'LEDGER_INSTANCE_NAME':"fogbed",
                'INFO_SITE_TEXT':"Node Container @ GitHub",
                'INFO_SITE_URL':"https://github.com/hyperledger/indy-node-container",
                'LEDGER_SEED':"000000000000000000000000Steward1"
                }
            )
    exp.add_docker(
            container=webserverContainer,
            datacenter=webserver)

     # Define Indy network in cloud
    indyCloud = IndyBasic(exp=exp, number_nodes=8)
    ledgersCloud, _ = indyCloud.create_ledgers('cloud')

    add_datacenters_to_worker(worker1, [indyCloud.cli_instance])
    add_datacenters_to_worker(worker1, ledgersCloud[:len(ledgersCloud)//2])
    add_datacenters_to_worker(worker2, ledgersCloud[len(ledgersCloud)//2:])
    add_datacenters_to_worker(worker2, [webserver])
    exp.add_tunnel(worker1, worker2)
    try:
        exp.start() 
        indyCloud.start_network()
        webserverContainer.cmd(f'echo "{indyCloud.request_genesis_file()}" >> /var/lib/indy/fogbed/pool_transactions_genesis')
        time.sleep(10)
        print(webserverContainer.cmd('./scripts/start_webserver.sh'))
        
        input('Press any key...')
    except Exception as ex: 
        print(ex)
    finally:
        exp.stop()
