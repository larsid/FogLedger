from typing import Dict
from fogbed import (
   VirtualInstance
)
from typing import Union

class NodeConfig:
    def __init__(self, name: str, port_bindings: Dict[int, int] =  {}, ip: Union[str,None] = None, ledger: VirtualInstance = None):
        self.name = name
        self.port_bindings = port_bindings
        self.ip = ip
        self.ledger = ledger