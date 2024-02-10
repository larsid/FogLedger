from typing import Dict
from fogbed import (
   VirtualInstance
)
from typing import Union

class NodeConfig:
    def __init__(self, name: str, port_bindings: Dict[str, str] =  {}, ip: Union[str,None] = None):
        self.name = name
        self.port_bindings = port_bindings
        self.ip = ip
