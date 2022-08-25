from typing import Any, Dict


class Container:
    def __init__(self, name: str, **params) -> None:
        self.name   = name
        self.params = params
    
    def update_cpu(self, cpu_quota: int, cpu_period: int):
        self.params['cpu_quota'] = cpu_quota
        self.params['cpu_period'] = cpu_period

    def update_memory(self, memory_limit: int):
        self.params['mem_limit'] = memory_limit

    @property
    def cpu_period(self) -> int:
        cpu_period = self.params.get('cpu_period')
        return -1 if(cpu_period is None) else cpu_period

    @property
    def cpu_quota(self) -> int:
        cpu_quota = self.params.get('cpu_quota')
        return -1 if(cpu_quota is None) else cpu_quota

    @property
    def mem_limit(self) -> int:
        mem_limit = self.params.get('mem_limit')
        return -1 if(mem_limit is None) else mem_limit

    @property
    def resources(self) -> 'Dict[str, Any] | None':
        return self.params.get('resources')
    
    @property
    def compute_units(self) -> float:
        resources = self.resources
        return 0.0 if(resources is None) else resources['cu']
    
    @property
    def memory_units(self) -> int:
        resources = self.resources
        return 0 if(resources is None) else resources['mu']
    
    def __repr__(self) -> str:
        cpu_quota  = self.cpu_quota
        cpu_period = self.cpu_period
        return f'Container(name={self.name}, cpu_quota={cpu_quota}, cpu_period={cpu_period})'