from typing import List
from fogbed import (
    FogbedExperiment, Container, Resources, Services,
    CloudResourceModel, EdgeResourceModel, FogResourceModel,
    setLogLevel
)

setLogLevel('info')

exp = FogbedExperiment()


if(__name__=='__main__'):
    cloud   = exp.add_virtual_instance('cloud')
    fog   = exp.add_virtual_instance('fog',   FogResourceModel(max_cu=4, max_mu=512))
    d1 = Container('d1', ip='10.0.0.1', dimage='hyperledger/indy-core-baseci:0.0.4', resources=Resources.SMALL)
    d2 = Container('d2', ip='10.0.0.2', dimage='hyperledger/indy-core-baseci:0.0.4', resources=Resources.SMALL)
    d3 = Container('d3', ip='10.0.0.3', dimage='hyperledger/indy-core-baseci:0.0.4', resources=Resources.SMALL)
    d4 = Container('d4', ip='10.0.0.4', dimage='hyperledger/indy-core-baseci:0.0.4', resources=Resources.SMALL)
    exp.add_docker(d1, cloud)
    exp.add_docker(d2, cloud)
    exp.add_docker(d3, cloud)
    exp.add_docker(d4, cloud)



    try:
        exp.start() 
        print(d1.cmd('ifconfig'))
        print(d1.cmd(f'ping -c 4 {d2.ip}'))
        exp.start_cli()
        input('Press any key...')
    except Exception as ex: 
        print(ex)
    finally:
        exp.stop()
