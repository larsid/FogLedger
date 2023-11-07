from .NodeConfig import (NodeConfig)
from typing import Dict
from fogbed import (
   VirtualInstance
)
class CoordConfig(NodeConfig):
    def __init__(self, name: str = None, port_bindings: Dict[str, str] = None,  ip:str=None, ledger: VirtualInstance = None, interval: str = '60s'):
        super().__init__(name, port_bindings, ip)
        self.interval = interval