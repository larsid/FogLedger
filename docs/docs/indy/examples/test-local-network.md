## Test local network

This example shows how to create a local network of Indy nodes.

### Define Trustees
First you need to create a file with the trustees information. The file must have the following format:

```csv	
Trustee name,Trustee DID,Trustee verkey
Trustee1,V4SGRU86Z58d6TV7PBUe6f,~CoRER63DVYnWZtK8uAzNbx
Trustee2,LnXR1rPnncTPZvRdmJKhJQ,~RTBtVN3iwcFhbWZzohFTMi
Trustee3,PNQm3CwyXbN5e39Rw3dXYx,~AHtGeRXtGjVfXALtXP9WiX
```

This example is for register clients that have a SEED defined as `000000000000000000000000TrusteeX`. The SEED is used to generate the DID and verkey. The file is used to create the trustees in the network. The file is passed to the `IndyBasic` class as `trustees_path` parameter.


### Experiment code

The code below shows how to create a local network of Indy nodes. The network is created in a single host, using Docker containers. The network is composed of 4 nodes, 3 trustees. The trustees are the nodes that validate the transactions. 

- You need to create a file with the trustees information;
- Define the hostname or IP address of the host where the emulation will run;

```py



from fogbed import (
    setLogLevel, FogbedDistributedExperiment
)

from fogledger.indy import (IndyBasic)
setLogLevel('info')

if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='PATH_TO_FILE_TRUSTEES.csv', config_nodes=[
            {'name': 'node1'},
            {'name': 'node2'},
            {'name': 'node3'},
            {'name': 'node4'},
        ])

    # Add worker for cli
    workerServer = exp.add_worker(f'HOSTNAME_OR_IP_ADDRESS')
    for i in range(len(indyCloud.ledgers)):
        workerServer.add(indyCloud.ledgers[i], reachable=True)

    try:
        exp.start()
        indyCloud.start_network()
        input('Press any key...')
    except Exception as ex:
        print(ex)
    finally:
        exp.stop()
```

### Save the experiment code

Save the code above in a file named `test-local-network.py`.

### Run the experiment

To run the experiment, you need to run the following command:

```bash
python3 test-local-network.py
```