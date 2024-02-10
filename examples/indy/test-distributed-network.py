from typing import List
from fogbed import (FogbedDistributedExperiment, Worker
)

from fogledger.indy import (IndyBasic, Node)

if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()
    worker1 = exp.add_worker('fog1')
    worker2 = exp.add_worker('edge1')
    worker3 = exp.add_worker('edge2')

    fog = exp.add_virtual_instance('fog')
    
    indyCloud = IndyBasic(exp=exp, trustees_path = 'tmp/trustees.csv', config_nodes= [
            Node(name='node1'),
            Node(name='node2'),
            Node(name='node3'),
            Node(name='node4'),
        ])

    worker1.add(fog, reachable=True)
    
    for i in range(len(indyCloud.ledgers)/2):
        worker2.add(indyCloud.ledgers[2*i], reachable=True)
        worker3.add(indyCloud.ledgers[2*i +1], reachable=True)

    exp.add_tunnel(worker1, worker2)
    exp.add_tunnel(worker1, worker3)
    try:
        exp.start()
        indyCloud.start_network()
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
