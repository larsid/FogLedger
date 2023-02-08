from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel,VirtualInstance,
    setLogLevel,
)
from fogbed.dlts import (IndyBasic)
setLogLevel('info')

exp = FogbedExperiment()
indy = IndyBasic(exp=exp, number_nodes=10)

def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)



if(__name__=='__main__'):

    cloud   = exp.add_virtual_instance('cloud')
    ledgers, nodes = indy.create_ledgers()
    
    create_links(cloud, ledgers)

    try:
        exp.start() 
        indy.start_network()
        
        exp.start_cli()
        input('Press any key...')
    except Exception as ex: 
        print(ex)
    finally:
        exp.stop()
