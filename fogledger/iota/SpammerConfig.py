from .NodeConfig import (NodeConfig)
from typing import Dict
from fogbed import (
   VirtualInstance
)
class SpammerConfig(NodeConfig):
    def __init__(self, name: str, port_bindings: Dict[str, str], ip:str=None, ledger: VirtualInstance = None, message: str="one-click-tangle."):
        super().__init__(name, port_bindings, ip, ledger)
        self.message = message