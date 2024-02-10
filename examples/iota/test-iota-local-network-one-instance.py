from fogledger.iota.IotaBasic import (IotaBasic)
from fogledger.iota.config.NodeConfig import (NodeConfig)
from fogledger.iota.config.CoordConfig import (CoordConfig)
from fogledger.iota.config.SpammerConfig import (SpammerConfig)
from fogledger.iota.config.ApiConfig import (ApiConfig)
from fogledger.iota.config.WebAppConfig import (WebAppConfig)
from typing import List
from fogbed import (
    FogbedExperiment,
    CloudResourceModel, EdgeResourceModel, FogResourceModel, VirtualInstance,
    setLogLevel,
)

setLogLevel('info')

def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)

if (__name__ == '__main__'):
    exp = FogbedExperiment()

    node1 = NodeConfig(name='node1', port_bindings={'8081':'8081', '14265':'14265'})
    node2 = NodeConfig(name='node2', port_bindings={'8081':'8082'})
    #node3 = NodeConfig(name='node3', port_bindings={'8081':'8083'})
    #node4 = NodeConfig(name='node4', port_bindings={'8081':'8084'})
    
    cord = CoordConfig(name='cord', port_bindings={'8081':'8085'}, interval='60s')
    
    spammer = SpammerConfig(name='spammer', port_bindings={'8081':'8086'}, message ='one-click-tangle.')
    
    api = ApiConfig(name='api', port_bindings={'4000':'4000'})    
    web_app = WebAppConfig(name='web_app', port_bindings={'80':'82'})

    fog = exp.add_virtual_instance('fog')
    iota = IotaBasic(exp=exp, prefix='iota1', virtual_instance=fog, nodes_number=4)

    try:
        exp.start()
        iota.start_network()
        print("Experiment started")
        input('Press any key...')

    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
