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
    d1 = Container('d1', ip='10.0.0.1', dimage='alpine', resources=Resources.SMALL)
    d2 = Container('d2', ip='10.0.0.2', dimage='ubuntu:trusty', resources=Resources.SMALL)

    exp.add_docker(d1, cloud)
    exp.add_docker(d2, fog)

    exp.add_link(cloud, fog)
    try:
        exp.start() 
        print(d1.cmd('ifconfig'))
        print(d1.cmd(f'ping -c 4 {d2.ip}'))
        input('Press any key...')
    except Exception as ex: 
        print(ex)
    finally:
        exp.stop()
