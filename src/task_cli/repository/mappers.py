from datetime import datetime
from task_cli.domain.task import Task, TaskStatus
from task_cli.domain.dtos import TaskDTO


class TaskMapper:
    """
    Utility class responsible for converting task representations
    between different architectural layers.

    This mapper handles transformations between:

    - Domain entities (`Task`)
    - Data Transfer Objects (`TaskDTO`)
    - Persistence representations (`dict`)

    It ensures that the domain layer remains isolated from
    persistence and serialization concerns.
    """
    @staticmethod
    def to_dto(task: Task) -> TaskDTO:
        """
        Convert a domain `Task` entity into a `TaskDTO`.

        This transformation serializes domain values such as
        `TaskStatus` and `datetime` into DTO-friendly formats.

        Parameters
        ----------
        task : Task
            Domain task entity.

        Returns
        -------
        TaskDTO
            Data transfer object representing the task.
        """
        return TaskDTO(
            task_id = task.task_id,
            description = task.description,
            status = task.status.value,
            created_at = task.created_at.isoformat(),
            updated_at = task.updated_at.isoformat(),
        )
    @staticmethod
    def from_dto(task_dto: TaskDTO) -> Task:
        """
        Convert a `TaskDTO` into a domain `Task` entity.

        This method reconstructs domain-specific types such as
        `TaskStatus` and `datetime` from their serialized forms.

        Parameters
        ----------
        task_dto : TaskDTO
            Data transfer object representing a task.

        Returns
        -------
        Task
            Domain task entity reconstructed from the DTO.
        """
        status = TaskStatus(task_dto.status)
        created_at = datetime.fromisoformat(task_dto.created_at)
        updated_at = datetime.fromisoformat(task_dto.updated_at)
        return Task(
            description=task_dto.description,
            task_id=task_dto.task_id,
            status=status,
            created_at=created_at,
            updated_at=updated_at
        )
    @staticmethod
    def to_dict(task_dto: TaskDTO) -> dict:
        """
        Convert a `TaskDTO` into a dictionary representation.

        This representation is suitable for serialization
        (e.g., JSON storage).

        Parameters
        ----------
        task_dto : TaskDTO
            Task data transfer object.

        Returns
        -------
        dict
            Dictionary containing the serialized task data.
        """
        return {
            "task_id": task_dto.task_id,
            "description": task_dto.description,
            "status": task_dto.status,
            "created_at": task_dto.created_at,
            "updated_at": task_dto.updated_at,
        }
    @staticmethod
    def from_dict(data: dict) -> TaskDTO:
        """
        Construct a `TaskDTO` from a dictionary representation.

        This method is typically used when loading tasks from
        serialized storage formats such as JSON files.

        Parameters
        ----------
        data : dict
            Dictionary containing task data.

        Returns
        -------
        TaskDTO
            DTO instance reconstructed from the dictionary.
        """
        return TaskDTO(
            task_id=int(data["task_id"]),
            description=str(data["description"]),
            status=str(data["status"]),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
        )
