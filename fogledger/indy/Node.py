class Node (object):
    def __init__(self, name: str, ip: str = None, port_bindings: dict = {}) -> None:
        self.name = name
        self.ip = ip
        self.port_bindings = port_bindings

    def __str__(self):
        return f'Node(name={self.name}, dimage={self.dimage}, ip={self.ip}, port_bindings={self.port_bindings})'
