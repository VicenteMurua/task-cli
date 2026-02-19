from task_cli.domain.task import TaskStatus
from task_cli.repository.task_repository import ITaskRepository
from task_cli.domain.dtos import TaskDTO


class FakeRepo(ITaskRepository):
    def __init__(self):
        self.storage = {}

    def get_max_id(self) -> int:
        return max(self.storage.keys(), default=0)

    def add(self, new_task: TaskDTO) -> None:
        self.storage[new_task.task_id] = new_task

    def update(self, updated_task: TaskDTO) -> None:
        self.storage[updated_task.task_id] = updated_task

    def delete(self, task_id: int) -> None:
        del self.storage[task_id]

    def read(self, task_id: int) -> TaskDTO:
        return self.storage[task_id]

    def filter_by_status(self, status_filter: TaskStatus|None) -> list[TaskDTO]:
        if status_filter is None:
            return list(self.storage.values())
        return [
            data
            for data in self.storage.values()
            if data.status == status_filter.value
        ]