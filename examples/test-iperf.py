from typing import List
from fogbed import (FogbedDistributedExperiment, Worker, Container
)

from fogledger.indy import (IndyBasic)

if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()
    worker1 = exp.add_worker('larsid02')
    worker2 = exp.add_worker('larsid03')

    fog1 = exp.add_virtual_instance('fog1')
    fog2 = exp.add_virtual_instance('fog2')
    
    exp.add_docker(container=Container(name='d1'),datacenter=fog1)
    exp.add_docker(container=Container(name='d2'), datacenter=fog2)

    worker1.add(fog1, reachable=True)
    worker2.add(fog2, reachable=True)

    exp.add_tunnel(worker1, worker2)
    try:
        exp.start()
        print(exp.get_docker('d1').cmd('apt-get update && apt-get install iperf -y'))
        print(exp.get_docker('d1').cmd('iperf -s -w 2m -D'))
        print(exp.get_docker('d2').cmd('apt-get update && apt-get install iperf -y'))
        print(exp.get_docker('d2').cmd(f'iperf -c {exp.get_docker("d1").ip} -w 2m -t 30s -i 1s'))
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
