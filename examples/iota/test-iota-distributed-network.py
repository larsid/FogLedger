from fogledger.iota.IotaBasic import (IotaBasic)
from fogledger.iota.config.NodeConfig import (NodeConfig)
from fogledger.iota.config.CoordConfig import (CoordConfig)
from fogledger.iota.config.SpammerConfig import (SpammerConfig)
from fogledger.iota.config.ApiConfig import (ApiConfig)
from fogledger.iota.config.WebAppConfig import (WebAppConfig)
from typing import List
from fogbed import (
    VirtualInstance, setLogLevel, FogbedDistributedExperiment, Worker, Controller
)

setLogLevel('info')

def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)

if (__name__ == '__main__'):
    exp = FogbedDistributedExperiment(controller_ip='35.245.131.33', controller_port=6633)
    worker1 = exp.add_worker(ip = '35.231.54.58',  controller=Controller('35.245.131.33', 6633))
    worker2 = exp.add_worker(ip = '34.145.164.105',  controller=Controller('35.245.131.33', 6633))

    node1 = NodeConfig(name='node1', port_bindings={'8081':'8081', '14265':'14265'})
    node2 = NodeConfig(name='node2', port_bindings={'8081':'8082'})
    node3 = NodeConfig(name='node3', port_bindings={'8081':'8083'})
    node4 = NodeConfig(name='node4', port_bindings={'8081':'8084'})
    
    cord = CoordConfig(name='cord', port_bindings={'8081':'8085'}, interval='60s')
    
    spammer = SpammerConfig(name='spammer', port_bindings={'8081':'8086'}, message ='one-click-tangle.')
   
    api = ApiConfig(name='api', port_bindings={'4000':'4000'})    
    web_app = WebAppConfig(name='web_app', port_bindings={'80':'82'})
    
    iota = IotaBasic(exp=exp, prefix='iota1', conf_nodes=[node1, node2, node3, node4], conf_coord=cord, conf_spammer=spammer)

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
