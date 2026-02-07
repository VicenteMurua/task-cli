from typing import List

from task_cli.domain.task import Task
from task_cli.repository.task_repository import ITaskRepository


class TaskManager:
    def __init__(self, repository: ITaskRepository) -> None:
        self._repository: ITaskRepository = repository
        self._lista_tareas: List[Task] = self._repository.load()

    def add(self, descripcion: str) -> None:
        pass

    def update(self, identificador: int, descripcion_nueva: str) -> None:
        pass

    def delete(self, identificador: int) -> None:
        pass

    def mark(self, estado: str, identificador: int) -> None:
        pass

