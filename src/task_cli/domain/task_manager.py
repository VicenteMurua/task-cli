from task_cli.domain.task import Task, TaskStatus
from task_cli.repository.task_repository import ITaskRepository
from functools import wraps
from datetime import datetime

def save_after(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        resultado = func(self, *args, **kwargs)
        self._save()  # llama al method privado de la clase
        return resultado
    return wrapper

class TaskManager:
    def __init__(self, repository: ITaskRepository) -> None:
        self._repository: ITaskRepository = repository
        self._dict_tasks: dict[int, Task] = {}
        self._load()
        self._greatest_task_id: int = max(self._dict_tasks.keys(), default=0)

    def _load(self):
        for data in self._repository.load():
            self._add_existing_task(data)

    def _save(self):
        self._repository.save(list(self._dict_tasks.values()))

    @save_after
    def add(self, description: str) -> None:
        self._greatest_task_id += 1
        new_task: Task = Task(description, TaskStatus.TODO, self._greatest_task_id)
        self._dict_tasks[new_task.task_id] = new_task

    def _add_existing_task(self, data: tuple[str, str, int, datetime, datetime]) -> None:
        description, status, task_id, creation, last_actualization = data
        new_task: Task = Task(description, TaskStatus(status), task_id, creation, last_actualization)
        self._dict_tasks[new_task.task_id] = new_task

    @save_after
    def update(self, task_id: int, new_description: str) -> None:
        target_task: Task = self._dict_tasks[task_id]
        target_task.update_description(new_description)
        self._dict_tasks.update({task_id: target_task})
    @save_after
    def delete(self, task_id: int) -> None:
        del self._dict_tasks[task_id]
    @save_after
    def mark(self, status: str, task_id: int) -> None:
        target_task: Task = self._dict_tasks[task_id]
        target_task.update_status(TaskStatus(status))
        self._dict_tasks.update({task_id: target_task})

    def filter_tasks(self, status_filter: str | None) -> dict[int, Task]:
        filtered_tasks: dict[int, Task] = {}
        if status_filter is None:
            return self._dict_tasks
        for task_id, task in self._dict_tasks.items():
            if task.status is TaskStatus(status_filter):
                filtered_tasks.update({task_id: task})
        return filtered_tasks