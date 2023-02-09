from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel,VirtualInstance,
    setLogLevel,
)
from indy.indy import (IndyBasic)
setLogLevel('info')

exp = FogbedExperiment()
indy = IndyBasic(exp=exp, number_nodes=2)

def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)



if(__name__=='__main__'):

    cloud   = exp.add_virtual_instance('cloud')
    ledgers, nodes = indy.create_ledgers()
    exp.add_link(ledgers[0],ledgers[1])

    
    # create_links(cloud, ledgers)

    try:
        exp.start() 
        indy.start_network()
        print(nodes[0].cmd(f'ping -c 4 {nodes[1].ip}'))
        exp.start_cli()
        input('Press any key...')
    except Exception as ex: 
        print(ex)
    finally:
        exp.stop()
