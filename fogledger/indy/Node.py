class Node:
    def __init__(self, name: str, ip: str = None, port_bindings: dict = {}) -> None:
        self.name = name
        self.ip = ip
        self.port_bindings = port_bindings