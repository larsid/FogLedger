from typing import Dict

class NodeConfig:
    def __init__(self, name: str, port_bindings: Dict[str, str] =  {}, ip: str = None):
        self.name = name
        self.port_bindings = port_bindings
        self.ip = ip