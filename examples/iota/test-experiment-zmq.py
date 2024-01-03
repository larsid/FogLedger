from fogledger.iota.IotaBasic import (IotaBasic)
from fogledger.iota.config.NodeConfig import (NodeConfig)
from fogledger.iota.config.CoordConfig import (CoordConfig)
from fogledger.iota.config.SpammerConfig import (SpammerConfig)
from fogledger.iota.config.ApiConfig import (ApiConfig)
from fogledger.iota.config.WebAppConfig import (WebAppConfig)
from typing import List
from fogbed import (
    VirtualInstance, setLogLevel, FogbedDistributedExperiment, Worker, Container, Controller
)

setLogLevel('info')

if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment(controller_ip='192.168.0.102', controller_port=6633)

    iota_worker = exp.add_worker(ip = '192.168.0.102', controller=Controller('192.168.0.102', 6633))

    node1 = NodeConfig(name='node1', port_bindings={'8081':'8081', '14265':'14265','1883':'1883'})
    node2 = NodeConfig(name='node2', port_bindings={'8081':'8082'})
    node3 = NodeConfig(name='node3', port_bindings={'8081':'8083'})
    node4 = NodeConfig(name='node4', port_bindings={'8081':'8084'})

    cord = CoordConfig(name='cord', port_bindings={'8081':'8085'}, interval='60s')
    spammer = SpammerConfig(name='spammer', port_bindings={'8081':'8086'}, message ='one-click-tangle.')

    api = ApiConfig(name='api', port_bindings={'4000':'4000'})
    web_app = WebAppConfig(name='web_app', port_bindings={'80':'82'})

    #iota = IotaBasic(exp=exp, prefix='iota1', conf_nodes=[node1, node2, node3, node4], conf_coord=cord, conf_spammer=spammer)
    iota = IotaBasic(exp=exp, prefix='iota1', conf_nodes=[node1, node2, node3, node4])
    #iota = IotaBasic(exp=exp, prefix='iota1', nodes_number=4)

    for iota_node in iota.ledgers:
        iota_worker.add(iota_node, reachable=True)

    zmq = Container(
       name='zmq',
       dimage='larsid/iota-zmq-bridge:1.0.0',
       dcmd=f'/entrypoint.sh',
       port_bindings={'5556':'5556'},
       environment={
          'MQTT_IP': iota.containers['node1'].ip,
          'INDEXES': 'LB_*'
       }
    )

    zmq_bridge = exp.add_virtual_instance('zmq_bridge')

    exp.add_docker(zmq, zmq_bridge)

    iota_worker.add(zmq_bridge, reachable=True)

    try:
        exp.start()
        iota.start_network()
        print("Experiment started")
        input('Press any key...')

    except Exception as ex:
        print(ex)
    finally:
        exp.stop()