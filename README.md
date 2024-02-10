![](https://img.shields.io/badge/python-3.8+-blue.svg)

# FogLedger

FogLedger is a plugin for Fogbed. It is a framework and toolset integration for the rapid prototyping of fog components in virtualized environments using a desktop approach for DLTs. Its design meets the postulated requirements of low cost, flexible setup, and compatibility with real-world technologies. The components are based on a Mininet network emulator with Docker container instances as fog virtual nodes.

## Install

Before installing Fogbed it is necessary to install some dependencies and Containernet, as shown in the steps below:

#### 1. Install Containernet

```
sudo apt-get install ansible
```

```
git clone https://github.com/containernet/containernet.git
```

```
sudo ansible-playbook -i "localhost," -c local containernet/ansible/install.yml
```

#### 2. Install Fogbed

```
sudo pip install -U git+https://github.com/EsauM10/fogbed.git
```

#### 3. Install FogLedger

```
sudo pip install -U git+https://github.com/larsid/FogLedger.git
```

## Get Started

## Preparing Blockchain Test

## Run example

```
cd examples
```

## Run local network test

```
sudo python3 test-local-network.py
```

## Run distributed network test

```
sudo python3 examples/indy/test-distributed-network.py
sudo python3 examples/indy/test-iota-distributed-network.py
```

## Example: A local network with four nodes

```python
from typing import List
from fogbed import (setLogLevel, FogbedDistributedExperiment)
import time
import os

from fogledger.indy import (IndyBasic, Node)
setLogLevel('info')


if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()
    worker1 = exp.add_worker('YOUR_HOST_IP or HOST_NAME')

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='examples/tmp/trustees.csv',  config_nodes=[
            Node(name='ledger1'),
            Node(name='ledger2'),
            Node(name='ledger3'),
            Node(name='ledger4'),
        ])

    for ledger in indyCloud.ledgers:
        worker1.add(ledger)
        worker1.add_link(edge1, ledger)

    try:
        exp.start()
        indyCloud.start_network()
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()


```

## Example: A local network with four nodes

```python
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
    exp = FogbedDistributedExperiment()
    worker = exp.add_worker('YOUR_HOST_IP or HOST_NAME')

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

    try:
        exp.start()
        iota.start_network()
        print("Experiment started")
        input('Press any key...')

    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
```

