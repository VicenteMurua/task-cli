from task_cli.domain.task import Task, TaskStatus
from task_cli.domain.dtos import TaskDTO
from task_cli.repository.mappers import TaskMapper
from task_cli.repository.task_repository import ITaskRepository


class TaskManager:
    def __init__(self, repository: ITaskRepository) -> None:
        self._repository: ITaskRepository = repository
        self._dict_tasks: dict[int, Task] = {}

    def add(self, description: str) -> None:
        new_id: int = self._repository.get_max_id() + 1
        new_task: Task = Task(
            description=description,
            task_id=new_id,
            status=TaskStatus.TODO
        )
        new_task_dto: TaskDTO = TaskMapper.to_task_dto(new_task)
        self._repository.add(new_task_dto)

    def update(self, task_id: int, new_description: str) -> None:
        target_dto: TaskDTO = self._repository.read(task_id)
        target_task: Task = TaskMapper.from_task_dto(target_dto)
        target_task.update_description(new_description)
        self._repository.update(TaskMapper.to_task_dto(target_task))


    def delete(self, task_id: int) -> None:
        self._repository.delete(task_id)

    def mark(self, status: str, task_id: int) -> None:
        target_dto: TaskDTO = self._repository.read(task_id)
        target_task: Task = TaskMapper.from_task_dto(target_dto)
        target_task.update_status(TaskStatus(status))
        self._repository.update(TaskMapper.to_task_dto(target_task))

    def filter_tasks(self, status_filter: str | None) -> list[TaskDTO]:
        return self._repository.filter_by_status(TaskStatus(status_filter))