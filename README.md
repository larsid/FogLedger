![](https://img.shields.io/badge/python-3.8+-blue.svg)

# FogLedger

FogLedger is plugin to Fogbed. It is framework and toolset integration for rapid prototyping of fog components in virtual-ized environments using a desktop approach for DLTs. Its design meets the postulated requirements of low cost, flexible setup and compatibility with real world technologies. The components are based on Mininet network emulator with Docker container instances as fog virtual nodes.

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

## Example: A local network with 4 nodes indy

```python
from typing import List
from fogbed import (setLogLevel, FogbedDistributedExperiment)
import time
import os

from fogledger.indy import (IndyBasic)
setLogLevel('info')


if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()
    worker1 = exp.add_worker('YOUR_HOST_IP or HOST_NAME')

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='examples/tmp/trustees.csv', config_nodes=[
            {'name': 'node1'},
            {'name': 'node2'},
            {'name': 'node3'},
            {'name': 'node4'},
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

## Example: A local network with 4 nodes iota

```python
from fogledger.iota.IotaBasic import (IotaBasic)
from fogledger.iota.config.NodeConfig import (NodeConfig)
from fogledger.iota.config.CoordConfig import (CoordConfig)
from fogledger.iota.config.SpammerConfig import (SpammerConfig)
from fogledger.iota.config.ApiConfig import (ApiConfig)
from fogledger.iota.config.WebAppConfig import (WebAppConfig)
from typing import List
from fogbed import (
    FogbedExperiment,
    CloudResourceModel, EdgeResourceModel, FogResourceModel, VirtualInstance,
    setLogLevel,
)

setLogLevel('info')

def create_links(cloud: VirtualInstance, devices: List[VirtualInstance]):
    for device in devices:
        exp.add_link(device, cloud)

if (__name__ == '__main__'):
    exp = FogbedExperiment()

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
    
    cloud = exp.add_virtual_instance('cloud1')

    api = ApiConfig(name='api', port_bindings={'4000':'4000'}, ledger=cloud)    
    web_app = WebAppConfig(name='web_app', port_bindings={'80':'82'}, ledger=cloud)
    
    iota = IotaBasic(exp=exp, prefix='iota1', conf_nodes=[node1, node2], conf_coord=cord, conf_spammer=spammer, conf_api=api, conf_web_app=web_app)

    fog = exp.add_virtual_instance('fog')
    create_links(fog, iota.ledgers)

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

