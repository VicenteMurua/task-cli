from datetime import datetime
from task_cli.domain.task import Task, TaskStatus
from task_cli.domain.dtos import TaskDTO


class TaskMapper:
    @staticmethod
    def to_task_dto(task: Task) -> TaskDTO:
        return TaskDTO(
            task_id = task.task_id,
            description = task.description,
            status = task.status.value,
            created_at = task.created_at.isoformat(),
            updated_at = task.updated_at.isoformat(),
        )
    @staticmethod
    def from_task_dto(task_dto: TaskDTO) -> Task:
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
        return {
            "description": task_dto.description,
            "status": task_dto.status,
            "task_id": task_dto.task_id,
            "created_at": task_dto.created_at,
            "updated_at": task_dto.updated_at,
        }
    @staticmethod #TODO: Generar un typedict
    def from_dict(data: dict) -> TaskDTO:
        return TaskDTO(
            task_id=data["task_id"],
            description=data["description"],
            status=data["status"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )
