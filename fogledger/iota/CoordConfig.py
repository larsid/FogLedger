from NodeConfig import (NodeConfig)
from typing import Dict

class CoordConfig(NodeConfig):
    def __init__(self, name: str, port_bindings: Dict[str, str],  ip:str, interval: str):
        super().__init__(name, port_bindings, ip)
        self.interval = interval