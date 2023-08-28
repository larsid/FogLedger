from typing import Dict
from fogbed import (
   VirtualInstance
)
class NodeConfig:
    def __init__(self, name: str, port_bindings: Dict[str, str] =  {}, ip: str = None, ledger: VirtualInstance = None):
        self.name = name
        self.port_bindings = port_bindings
        self.ip = ip
        self.ledger = ledger