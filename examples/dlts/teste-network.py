from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel,VirtualInstance,
    setLogLevel,
)
from indy.indy import (IndyBasic)
setLogLevel('info')


def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)



if(__name__=='__main__'):

    exp = FogbedExperiment()

     # Define Indy network in cloud
    indyCloud = IndyBasic(exp=exp, number_nodes=4)
    cloud = exp.add_virtual_instance('cloud')
    ledgers, nodes = indyCloud.create_ledgers('cloud')
    create_links(cloud, ledgers)

    # Define Indy network in fog
    indyFog = IndyBasic(exp=exp, number_nodes=4)
    fog = exp.add_virtual_instance('fog')
    ledgers, nodes = indyFog.create_ledgers('fog')
    create_links(fog, ledgers)

    try:
        exp.start() 

        indyCloud.start_network()
        indyFog.start_network()

        exp.start_cli()
        input('Press any key...')
    except Exception as ex: 
        print(ex)
    finally:
        exp.stop()
