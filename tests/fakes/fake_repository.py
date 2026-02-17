from src.task_cli.repository.task_repository import ITaskRepository
from src.task_cli.domain.dtos import TaskDTO


class FakeTaskRepository(ITaskRepository):
    def __init__(self, initial_data: list[TaskDTO]|None =None):
        self.storage = initial_data if initial_data else []
        self.saved = False

    def load(self) -> list[TaskDTO]:
        return list(self.storage)

    def save(self, tasks: list[TaskDTO]) -> None:
        self.storage = list(tasks)
        self.saved = True


