from .NodeConfig import (NodeConfig)
from typing import Dict
from fogbed import (
   VirtualInstance
)
class CoordConfig(NodeConfig):
    def __init__(self, name: str, port_bindings: Dict[str, str],  ip:str=None, ledger: VirtualInstance = None, interval: str = '60s'):
        super().__init__(name, port_bindings, ip, ledger)
        self.interval = interval