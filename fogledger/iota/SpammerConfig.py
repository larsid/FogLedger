from .NodeConfig import (NodeConfig)
from typing import Dict

class SpammerConfig(NodeConfig):
    def __init__(self, name: str, port_bindings: Dict[str, str], ip:str=None, message: str="one-click-tangle."):
        super().__init__(name, port_bindings, ip)
        self.message = message