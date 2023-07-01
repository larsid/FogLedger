## Test distributed network

This example shows how to create a distributed network of Indy nodes.

### Define Trustees

See [Test local network](./test-local-network.md).

### Experiment code

The code below shows how to create a distributed network of Indy nodes. The network is created in three hosts, using Docker containers. The network is composed of 4 nodes, 3 trustees.

- Define the hostname or IP address of the hosts where the emulation will run;

```py
from typing import List
from fogbed import (FogbedDistributedExperiment, Worker
)

from fogledger.indy import (IndyBasic)

if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()
    worker1 = exp.add_worker('HOST1')
    worker2 = exp.add_worker('HOST2')
    worker3 = exp.add_worker('HOST3')

    fog = exp.add_virtual_instance('fog')

    indyCloud = IndyBasic(exp=exp, trustees_path = 'PATH_TO_FILE_TRUSTEES.csv', config_nodes=[
            {'name': 'node1'},
            {'name': 'node2'},
            {'name': 'node3'},
            {'name': 'node4'},
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

```

### Save the experiment code

Save the code above in a file named `test-distributed-network.py`.

### Run the experiment

To run the experiment, you need to run the following command:

```bash
python3 test-distributed-network.py
```
