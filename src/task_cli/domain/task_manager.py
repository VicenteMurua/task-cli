from task_cli.domain.task import Task, TaskStatus
from task_cli.domain.dtos import TaskDTO
from task_cli.repository.mappers import TaskMapper
from task_cli.repository.task_repository import IRepository


class TaskManager:
    """
    Application service responsible for orchestrating task operations.

    The TaskManager coordinates interactions between the domain layer
    (`Task` entities) and the persistence layer (`IRepository`). It
    handles creation, updates, deletion, and retrieval of tasks while
    performing the necessary transformations between domain entities
    and data transfer objects (DTOs).

    This class does not contain persistence logic itself; it delegates
    storage responsibilities to the provided repository implementation.
    """

    def __init__(self, repository: IRepository) -> None:
        """
        Initialize the TaskManager with a repository implementation.

        Parameters
        ----------
        repository : IRepository
            Repository responsible for storing and retrieving tasks.
        """
        self._repository: IRepository = repository

    def add(self, description: str) -> TaskDTO:
        """
        Create and persist a new task.

        A new identifier is generated using the maximum existing ID
        in the repository.

        Parameters
        ----------
        description : str
            Human-readable description of the task.

        Returns
        -------
        TaskDTO
            DTO representing the newly created task.

        Raises
        ------
        TaskValidationError
            If the provided description violates domain validation rules.
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

        The task is retrieved from the repository, converted to a domain
        entity, mutated, and then persisted again as a DTO.

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

        Raises
        ------
        TaskNotFoundError
            If the task does not exist in the repository.
        TaskValidationError
            If the new description violates domain validation rules.
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
        Remove a task from the repository.

        Parameters
        ----------
        task_id : int
            Identifier of the task to delete.

        Returns
        -------
        TaskDTO
            DTO representing the removed task.

        Raises
        ------
        TaskNotFoundError
            If the task does not exist.
        """
        with self._repository as repo:
            task: TaskDTO = repo.read(task_id)
            repo.delete(task_id)
            return task

    def read(self, task_id: int) -> TaskDTO:
        """
        Retrieve a task by its identifier.

        Parameters
        ----------
        task_id : int
            Identifier of the task.

        Returns
        -------
        TaskDTO
            DTO representing the requested task.

        Raises
        ------
        TaskNotFoundError
            If the task does not exist.
        """
        with self._repository as repo:
            return repo.read(task_id)

    def mark(self, status: TaskStatus, task_id: int) -> TaskDTO:
        """
        Change the status of a task.

        The task is retrieved, converted to a domain entity,
        updated, and then persisted again.

        Parameters
        ----------
        status : TaskStatus
            New status to assign to the task.
        task_id : int
            Identifier of the task to update.

        Returns
        -------
        TaskDTO
            DTO representing the updated task.

        Raises
        ------
        TaskNotFoundError
            If the task does not exist.
        TypeError
            If the provided status is not a valid `TaskStatus`.
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
        Retrieve tasks filtered by their status.

        Parameters
        ----------
        status_filter : TaskStatus | None
            Status used as filter. If None, all tasks are returned.

        Returns
        -------
        list[TaskDTO]
            List of DTOs matching the filter criteria.
        """
        with self._repository as repo:
            return repo.filter_by_status(status_filter)