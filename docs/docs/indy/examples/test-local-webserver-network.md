## Test local network

This example shows how to create a local network of Indy nodes.

### Define Trustees

See [Test local network](./test-local-network.md).



### Experiment code

The code below shows how to create a local network of Indy nodes. The network is created in a single host, using Docker containers. The network is composed of 4 nodes, 3 trustees. The trustees are the nodes that validate the transactions. 

- You need to create a file with the trustees information;
- Define the hostname or IP address of the host where the emulation will run;

```py
from typing import List
from fogbed import (
    Container, VirtualInstance,
    setLogLevel, FogbedDistributedExperiment, Worker
)
import time

from fogledger.indy import (IndyBasic, Node)
setLogLevel('info')


def add_datacenters_to_worker(worker: Worker, datacenters: List[VirtualInstance]):
    for device in datacenters:
        worker.add(device, reachable=True)


if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()

    # Webserver to check metrics
    cloud = exp.add_virtual_instance('cloud')
    instanceWebserver = exp.add_docker(
        container=Container(
            name='webserver',
            dimage='larsid/fogbed-indy-webserver:v1.0.2-beta',
            port_bindings={8000: 80, 6543: 6543},
            ports=[8000, 6543],
            environment={
                'MAX_FETCH': 50000,
                'RESYNC_TIME': 120,
                'WEB_ANALYTICS': True,
                'REGISTER_NEW_DIDS': True,
                'LEDGER_INSTANCE_NAME': "fogbed",
                'LEDGER_SEED': "000000000000000000000000Trustee1",
                'GENESIS_FILE': "/pool_transactions_genesis"
            },
            volumes=[
                f'tmp:/var/log/indy',
            ]
        ),
        datacenter=cloud)

    # ACA-PY to make requests to the ledger
    exp.add_docker(
        container=Container(
            name='test',
            dimage='mnplima/indy-test',
        ),
        datacenter=cloud
    )

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='PATH_TO_FILE_TRUSTEES.csv', config_nodes=[
            Node(name='node1'),
            Node(name='node2'),
            Node(name='node3'),
            Node(name='node4'),
        ])

    # Add worker for cli
    workerServer = exp.add_worker(f'HOSTNAME_OR_IP_ADDRESS')
    workerServer.add(cloud, reachable=True)
    for i in range(2, len(indyCloud.ledgers)+2):
        workerServer.add(indyCloud.ledgers[i-2], reachable=True)

    try:
        exp.start()
        indyCloud.start_network()
        cloud.containers['webserver'].cmd(f"echo '{indyCloud.genesis_content}' > /pool_transactions_genesis")
        print('Starting Webserver')
        time.sleep(10)
        cloud.containers['webserver'].cmd('./scripts/start_webserver.sh > output.log 2>&1 &')

        
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()

```

### Save the experiment code

Save the code above in a file named `test-local-webserver-network.py`.

### Run the experiment

To run the experiment, you need to run the following command:

```bash
python3 test-local-webserver-network.py
```

### Check the results

The webserver is available at http://HOSTNAME_OR_IP_ADDRESS:80. It is provided by Von Network. Check more details at [BCGOV/von-network](https://github.com/bcgov/von-network)

![image](https://github.com/larsid/FogLedger/assets/32804625/270af4d9-1790-4c49-9571-590574751dd5)
