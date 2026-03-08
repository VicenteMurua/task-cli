from task_cli.domain.task import Task, TaskStatus
from task_cli.domain.dtos import TaskDTO
from task_cli.repository.mappers import TaskMapper
from task_cli.repository.task_repository import IRepository


class TaskManager:
    """
    Application service responsible for coordinating task operations.

    This class acts as the bridge between the domain layer (Task entity)
    and the persistence layer (repository). It orchestrates the creation,
    modification, deletion, and retrieval of tasks while ensuring proper
    transformations between domain entities and DTOs.
    """

    def __init__(self, repository: IRepository) -> None:
        """
        Initialize the TaskManager with a repository implementation.

        Parameters
        ----------
        repository : IRepository
            Repository used for persistence operations.
        """
        self._repository: IRepository = repository

    def add(self, description: str) -> TaskDTO:
        """
        Create a new task.

        A new task ID is generated based on the current maximum ID stored
        in the repository.

        Parameters
        ----------
        description : str
            Description of the new task.

        Returns
        -------
        TaskDTO
            Data transfer object representing the newly created task.
        """
        with self._repository as repo:
            new_id: int = repo.get_max_id() + 1
            new_task = Task(
                description=description,
                task_id=new_id,
                status=TaskStatus.TODO
            )
            new_task_dto: TaskDTO = TaskMapper.to_dto(new_task)
            repo.add(new_task_dto)
            return new_task_dto

    def update(self, task_id: int, new_description: str) -> TaskDTO:
        """
        Update the description of an existing task.

        Parameters
        ----------
        task_id : int
            Identifier of the task to update.
        new_description : str
            New description to assign to the task.

        Returns
        -------
        TaskDTO
            DTO representing the updated task.
        """
        with self._repository as repo:
            target_dto: TaskDTO = repo.read(task_id)
            target_task: Task = TaskMapper.from_dto(target_dto)
            target_task.update_description(new_description)
            updated_target_dto: TaskDTO = TaskMapper.to_dto(target_task)
            repo.update(updated_target_dto)
            return updated_target_dto

    def delete(self, task_id: int) -> TaskDTO:
        """
        Delete a task from the repository.

        Parameters
        ----------
        task_id : int
            Identifier of the task to delete.

        Returns
        -------
        TaskDTO
            DTO of the deleted task.
        """
        with self._repository as repo:
            task: TaskDTO = repo.read(task_id)
            repo.delete(task_id)
            return task

    def read(self, task_id: int) -> TaskDTO:
        """
        Retrieve a task by its ID.

        Parameters
        ----------
        task_id : int
            Identifier of the task to retrieve.

        Returns
        -------
        TaskDTO
            DTO representing the requested task.
        """
        with self._repository as repo:
            return repo.read(task_id)

    def mark(self, status: TaskStatus, task_id: int) -> TaskDTO:
        """
        Change the status of a task.

        Parameters
        ----------
        status : str
            New status value (must correspond to a TaskStatus value).
        task_id : int
            Identifier of the task to update.

        Returns
        -------
        TaskDTO
            DTO representing the updated task.
        """
        with self._repository as repo:
            target_dto: TaskDTO = repo.read(task_id)
            target_task: Task = TaskMapper.from_dto(target_dto)
            target_task.update_status(status)
            updated_target_dto: TaskDTO = TaskMapper.to_dto(target_task)
            repo.update(updated_target_dto)
            return updated_target_dto

    def filter_by_status(self, status_filter: TaskStatus | None) -> list[TaskDTO]:
        """
        Retrieve tasks filtered by status.

        Parameters
        ----------
        status_filter : str | None
            Status value used as filter. If None, all tasks are returned.

        Returns
        -------
        list[TaskDTO]
            List of tasks matching the filter.
        """
        with self._repository as repo:
            if status_filter is None:
                return repo.filter_by_status(None)
            return repo.filter_by_status(status_filter)