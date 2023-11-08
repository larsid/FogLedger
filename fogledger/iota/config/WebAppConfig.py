from .NodeConfig import (NodeConfig)
from typing import Dict
from fogbed import (
   VirtualInstance
)
class WebAppConfig(NodeConfig):
    def __init__(self, name: str = None, port_bindings: Dict[str, str] = None,  ip:str=None, api_ip:str = None, api_port: str = '4000'):
        super().__init__(name, port_bindings, ip)
        self.api_ip = api_ip
        self.api_port = api_port