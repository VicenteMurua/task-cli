from task_cli.domain.task import Task, TaskStatus, TaskDTO, TaskMapper
from task_cli.repository.task_repository import ITaskRepository
from functools import wraps

def save_after(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        resultado = func(self, *args, **kwargs)
        self._save()  # llama al method privado de la clase
        return resultado
    return wrapper
def load_before(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self._load()   # llama al method privado de la clase
        resultado = func(self, *args, **kwargs)
        return resultado
    return wrapper

class TaskManager:
    def __init__(self, repository: ITaskRepository) -> None:
        self._repository: ITaskRepository = repository
        self._dict_tasks: dict[int, Task] = {}
        self._greatest_task_id: int = 0

    def _load(self):
        for data in self._repository.load():
            self._add_existing_task(data)
        self._greatest_task_id: int = max(self._dict_tasks.keys(), default=0)

    def _save(self):
        self._repository.save([TaskMapper.to_task_dto(task) for task  in list(self._dict_tasks.values())])
    def _add_existing_task(self, data: TaskDTO) -> None:
        new_task: Task = TaskMapper.from_task_dto(data)
        self._dict_tasks[new_task.task_id] = new_task
    @save_after
    @load_before
    def add(self, description: str) -> None:
        self._greatest_task_id += 1
        new_task: Task = Task(description, TaskStatus.TODO, self._greatest_task_id)
        self._dict_tasks[new_task.task_id] = new_task
    @save_after
    @load_before
    def update(self, task_id: int, new_description: str) -> None:
        target_task: Task = self._dict_tasks[task_id]
        target_task.update_description(new_description)
        self._dict_tasks.update({task_id: target_task})
    @save_after
    @load_before
    def delete(self, task_id: int) -> None:
        del self._dict_tasks[task_id]
    @save_after
    @load_before
    def mark(self, status: str, task_id: int) -> None:
        target_task: Task = self._dict_tasks[task_id]
        target_task.update_status(TaskStatus(status))
        self._dict_tasks.update({task_id: target_task})

    @load_before
    def filter_tasks(self, status_filter: str | None) -> dict[int, Task]:
        filtered_tasks: dict[int, Task] = {}
        if status_filter is None:
            return self._dict_tasks
        for task_id, task in self._dict_tasks.items():
            if task.status is TaskStatus(status_filter):
                filtered_tasks.update({task_id: task})
        return filtered_tasks