from .NodeConfig import (NodeConfig)
from typing import Dict
from fogbed import (
   VirtualInstance
)
class SpammerConfig(NodeConfig):
    def __init__(self, name: str = None, port_bindings: Dict[str, str] = None, ip:str=None, message: str="one-click-tangle."):
        super().__init__(name, port_bindings, ip)
        self.message = message