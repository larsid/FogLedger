from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel,VirtualInstance,
    setLogLevel,
)
from indy.indy import (IndyBasic)
import time
import os

setLogLevel('info')

def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)



if(__name__=='__main__'):

    exp = FogbedExperiment()

     # Define Indy network in cloud
    indyCloud = IndyBasic(exp=exp, number_nodes=3)
    cloud = exp.add_virtual_instance('cloud')
    ledgers, nodes = indyCloud.create_ledgers('cloud')
    create_links(cloud, ledgers)
    exp.add_link(cloud, indyCloud.cli_instance)


    # Define Indy network in fog
    indyFog = IndyBasic(exp=exp, number_nodes=3)
    fog = exp.add_virtual_instance('fog')
    ledgers, nodes = indyFog.create_ledgers('fog')
    create_links(fog, ledgers)

    webserverContainer = Container(
            name='webserver', 
            dimage='webserver',
            port_bindings={8000: 8000},
            ports=[8000],
            environment={
                'MAX_FETCH':50000,
                'RESYNC_TIME':120,
                'WEB_ANALYTICS': True,
                'REGISTER_NEW_DIDS':True,
                'LEDGER_INSTANCE_NAME':"fogbed",
                'INFO_SITE_TEXT':"Node Container @ GitHub",
                'INFO_SITE_URL':"https://github.com/hyperledger/indy-node-container",
                'LEDGER_SEED':"000000000000000000000000Steward1",
                'GENESIS_FILE': "/var/lib/indy/fogbed/pool_transactions_genesis" 
            },
            volumes=[
                f'{os.path.abspath(f"indy/tmp/cloud/")}:/var/lib/indy/'
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
        print(webserverContainer.cmd('./scripts/start_webserver.sh'))

        exp.start_cli()
        input('Press any key...')
    except Exception as ex: 
        print(ex)
    finally:
        exp.stop()
