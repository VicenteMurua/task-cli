from task_cli.domain.task import Task, TaskStatus
from task_cli.domain.dtos import TaskDTO
from task_cli.repository.mappers import TaskMapper
from task_cli.repository.task_repository import ITaskRepository


class TaskManager:
    def __init__(self, repository: ITaskRepository) -> None:
        self._repository: ITaskRepository = repository

    def add(self, description: str) -> TaskDTO:
        with self._repository as repo:
            new_id: int = repo.get_max_id() + 1
            new_task: Task = Task(
                description=description,
                task_id=new_id,
                status=TaskStatus.TODO
            )
            new_task_dto: TaskDTO = TaskMapper.to_task_dto(new_task)
            repo.add(new_task_dto)
            return new_task_dto

    def update(self, task_id: int, new_description: str) -> TaskDTO:
        with self._repository as repo:
            target_dto: TaskDTO = repo.read(task_id)
            target_task: Task = TaskMapper.from_task_dto(target_dto)
            target_task.update_description(new_description)
            updated_target_dto: TaskDTO = TaskMapper.to_task_dto(target_task)
            repo.update(updated_target_dto)
            return updated_target_dto


    def delete(self, task_id: int) -> TaskDTO:
        with self._repository as repo:
            task: TaskDTO = repo.read(task_id)
            repo.delete(task_id)
            return task

    def read(self, task_id: int) -> TaskDTO:
        with self._repository as repo:
            return repo.read(task_id)

    def mark(self, status: str, task_id: int) -> TaskDTO:
        with self._repository as repo:
            target_dto: TaskDTO = repo.read(task_id)
            target_task: Task = TaskMapper.from_task_dto(target_dto)
            target_task.update_status(TaskStatus(status))
            updated_target_dto: TaskDTO = TaskMapper.to_task_dto(target_task)
            repo.update(updated_target_dto)
            return updated_target_dto

    def filter_tasks(self, status_filter: str | None) -> list[TaskDTO]:
        with self._repository as repo:
            if status_filter is None:
                return repo.filter_by_status(None)
            return repo.filter_by_status(TaskStatus(status_filter))