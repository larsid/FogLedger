```
from fogbed import (
    setLogLevel, FogbedDistributedExperiment
)

from fogledger.indy import (IndyBasic)
setLogLevel('info')

if (__name__ == '__main__'):

    exp = FogbedDistributedExperiment()

    # Define Indy network in cloud
    indyCloud = IndyBasic(
        exp=exp, trustees_path='tmp/trustees.csv', prefix='ledger',  nodes_number=4)

    # Add worker for cli
    workerServer = exp.add_worker(f'host')
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