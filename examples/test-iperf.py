from typing import List
from fogbed import (FogbedDistributedExperiment, Worker, Container, Controller
)

from fogledger.indy import (IndyBasic)

if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment(controller_ip='34.69.7.94', controller_port=80)
    worker1 = exp.add_worker('34.78.188.172',port=80,
                   controller=Controller('34.69.7.94', port=80))
    worker2 = exp.add_worker('34.146.249.115',port=80,
                   controller=Controller('34.69.7.94', port=80))

    fog1 = exp.add_virtual_instance('fog1')
    fog2 = exp.add_virtual_instance('fog2')
    
    exp.add_docker(container=Container(name='d1', ip='34.78.188.172'),datacenter=fog1)
    exp.add_docker(container=Container(name='d2', ip='34.146.249.115'), datacenter=fog2)

    worker1.add(fog1, reachable=True)
    worker2.add(fog2, reachable=True)

    exp.add_tunnel(worker1, worker2)
    try:
        exp.start()
        print(exp.get_docker('d2').cmd(f'ping -c 10 {exp.get_docker("d1").ip} '))
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
