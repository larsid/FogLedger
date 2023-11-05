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

    edge1 = exp.add_virtual_instance('edge1')
    edge2 = exp.add_virtual_instance('edge2')
    edge3 = exp.add_virtual_instance('edge3')
    edge4 = exp.add_virtual_instance('edge4')

    node1 = NodeConfig(name='node1', port_bindings={'8081':'8081', '14265':'14265'}, ledger=edge1)
    node2 = NodeConfig(name='node2', port_bindings={'8081':'8082'}, ledger=edge2)
    #node3 = NodeConfig(name='node3', port_bindings={'8081':'8083'}, ledger=edge3)
    #node4 = NodeConfig(name='node4', port_bindings={'8081':'8084'}, ledger=edge4)
    
    edge5 = exp.add_virtual_instance('edge5')
    cord = CoordConfig(name='cord', port_bindings={'8081':'8085'}, ledger=edge5, interval='60s')
    
    edge6 = exp.add_virtual_instance('edge6')
    spammer = SpammerConfig(name='spammer', port_bindings={'8081':'8086'}, ledger=edge6, message ='one-click-tangle.')
    
    cloud = exp.add_virtual_instance('cloud1')

    api = ApiConfig(name='api', port_bindings={'4000':'4000'}, ledger=cloud)    
    web_app = WebAppConfig(name='web_app', port_bindings={'80':'82'}, ledger=cloud)
    
    iota = IotaBasic(exp=exp, prefix='iota1', conf_nodes=[node1, node2], conf_coord=cord, conf_spammer=spammer)

    fog = exp.add_virtual_instance('fog')
    create_links(fog, iota.ledgers)

    try:
        exp.start()
        iota.start_network()
        print("Experiment started")
        input('Press any key...')

    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
