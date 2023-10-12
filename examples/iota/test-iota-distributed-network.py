from fogledger.iota.IotaBasic import (IotaBasic)
from fogledger.iota.NodeConfig import (NodeConfig)
from fogledger.iota.CoordConfig import (CoordConfig)
from fogledger.iota.SpammerConfig import (SpammerConfig)
from fogledger.iota.ApiConfig import (ApiConfig)
from fogledger.iota.WebAppConfig import (WebAppConfig)
from typing import List
from fogbed import (
    VirtualInstance, setLogLevel, FogbedDistributedExperiment, Worker, Controller
)

setLogLevel('info')

def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)

if (__name__ == '__main__'):
    exp = FogbedDistributedExperiment(controller_ip='35.245.6.178', controller_port=6633)
    worker1 = exp.add_worker(ip = '34.139.133.100',  controller=Controller('35.245.6.178', 6633))
    worker2 = exp.add_worker(ip = '35.245.6.178',  controller=Controller('35.245.6.178', 6633))
    
    edge1 = exp.add_virtual_instance('edge1')
    edge2 = exp.add_virtual_instance('edge2')
    edge3 = exp.add_virtual_instance('edge3')
    edge4 = exp.add_virtual_instance('edge4')

    node1 = NodeConfig(name='node1', port_bindings={'8081':'8081', '14265':'14265'}, ledger=edge1)
    node2 = NodeConfig(name='node2', port_bindings={'8081':'8082'}, ledger=edge2)
    node3 = NodeConfig(name='node3', port_bindings={'8081':'8083'}, ledger=edge3)
    node4 = NodeConfig(name='node4', port_bindings={'8081':'8084'}, ledger=edge4)
    
    edge5 = exp.add_virtual_instance('edge5')
    cord = CoordConfig(name='cord', port_bindings={'8081':'8085'}, ledger=edge5, interval='60s')
    
    edge6 = exp.add_virtual_instance('edge6')
    spammer = SpammerConfig(name='spammer', port_bindings={'8081':'8086'}, ledger=edge6, message ='one-click-tangle.')
    
    cloud1 = exp.add_virtual_instance('cloud1')
    cloud2 = exp.add_virtual_instance('cloud2')
    api = ApiConfig(name='api', port_bindings={'4000':'4000'}, ledger=cloud1)    
    web_app = WebAppConfig(name='web_app', port_bindings={'80':'82'}, ledger=cloud2)
    
    iota = IotaBasic(exp=exp, prefix='iota1', conf_nodes=[node1, node2, node3, node4], conf_coord=cord, conf_spammer=spammer, conf_api=api, conf_web_app=web_app)

    add_datacenters_to_worker(worker1, iota.ledgers[:len(iota.ledgers)//2])
    add_datacenters_to_worker(worker2, iota.ledgers[len(iota.ledgers)//2:])
    exp.add_tunnel(worker1, worker2)

    try:
        exp.start()
        iota.start_network()
        print("Experiment started")
        input('Press any key...')

    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
