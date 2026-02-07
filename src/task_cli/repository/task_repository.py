from abc import ABC, abstractmethod
from task_cli.domain.task import Task

class ITaskRepository(ABC):
    @abstractmethod
    def save(self, lista_tareas: list[Task]) -> None:
        pass
    @abstractmethod
    def load(self, direccion_archivo: str) -> list[Task]:
        pass

class JSONTaskRepository(ITaskRepository):
    pass