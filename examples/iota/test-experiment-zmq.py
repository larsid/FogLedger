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
import signal


setLogLevel('info')

if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment(controller_ip='localhost', controller_port=6633)

    iota_worker = exp.add_worker(ip = 'localhost', controller=Controller('localhost', 6633))

    node0 = NodeConfig(name='node0', port_bindings={'8081':'8081', '14265':'14265','1883':'1883'})
    node1 = NodeConfig(name='node1', port_bindings={'8081':'8082', '14265':'14201'})
    node2 = NodeConfig(name='node2', port_bindings={'8081':'8083', '14265':'14202'})
    node3 = NodeConfig(name='node3', port_bindings={'8081':'8084', '14265':'14203'})
    node4 = NodeConfig(name='node4', port_bindings={'8081':'8085', '14265':'14204'})
    node5 = NodeConfig(name='node5', port_bindings={'8081':'8086', '14265':'14205'})
    node6 = NodeConfig(name='node6', port_bindings={'8081':'8087', '14265':'14206'})
    node7 = NodeConfig(name='node7', port_bindings={'8081':'8088', '14265':'14207'})
    node8 = NodeConfig(name='node8', port_bindings={'8081':'8089', '14265':'14208'})

    cord = CoordConfig(name='cord', port_bindings={'8081':'8085'}, interval='60s')
    spammer = SpammerConfig(name='spammer', port_bindings={'8081':'8086'}, message ='one-click-tangle.')

    api = ApiConfig(name='api', port_bindings={'4000':'4000'})
    web_app = WebAppConfig(name='web_app', port_bindings={'80':'82'})

    #iota = IotaBasic(exp=exp, prefix='iota1', conf_nodes=[node1, node2, node3, node4], conf_coord=cord, conf_spammer=spammer)
    iota = IotaBasic(exp=exp, prefix='iota1', conf_nodes=[node0 ,node1, node2, node3, node4, node5, node6, node7, node8])
    #iota = IotaBasic(exp=exp, prefix='iota1', nodes_number=4)

    for iota_node in iota.ledgers:
        iota_worker.add(iota_node, reachable=True)

    zmq = Container(
       name='zmq',
       dimage='larsid/iota-zmq-bridge:1.0.0',
       dcmd=f'/entrypoint.sh',
       port_bindings={'5556':'5556'},
       environment={
          'MQTT_IP': iota.containers['node0'].ip,
          'INDEXES': 'LB_*',
          'NUM_WORKERS':20
       }
    )

    zmq_bridge = exp.add_virtual_instance('zmq_bridge')

    exp.add_docker(zmq, zmq_bridge)

    iota_worker.add(zmq_bridge, reachable=True)

    try:
        exp.start()
        iota.start_network()
        print("Experiment started")
        while True:
            key = input("\nPress 'p' to stop the experiment: ")
            if key.lower() == 'p':
                print("Stopping the experiment...")
                exp.stop()
                break
            else:
                print(f"Ignoring key: {key}")
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()