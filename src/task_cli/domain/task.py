from datetime import datetime, timezone
from functools import wraps
from enum import Enum
from dataclasses import dataclass
from colorama import Fore, Style, init
init(autoreset=True)

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"

def update_time_stamp(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        resultado = func(self, *args, **kwargs)
        self._refresh_updated_at()  # llama al method privado de la clase
        return resultado
    return wrapper

class Task:
    _description: str
    _status: TaskStatus
    _task_id: int
    _created_at: datetime
    _updated_at: datetime

    def __init__(self,
                 description: str,
                 status: TaskStatus,
                 task_id: int,
                 created_at: datetime | None = None,
                 updated_at: datetime | None = None,
                 ):
        if (created_at is None) ^ (updated_at is None):
            raise ValueError("CreatedAt and updatedAt must both be None or defined")
        self._description = description
        self._status = status
        self._task_id = task_id
        self._created_at = datetime.now(timezone.utc) if created_at is None\
            else created_at
        self._updated_at = self._created_at if updated_at is None\
            else updated_at

    @property
    def description(self) -> str:
        return self._description

    @property
    def status(self):
        return self._status

    @property
    def task_id(self) -> int:
        return self._task_id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at

    def __str__(self):
        return (
            f"\n{'-' * 100}\n"
            f"Created: {self.created_at.strftime('%B %d, %Y')}"
            f" - {Fore.GREEN}Task #{self.task_id} [{self.status.value}] {Style.RESET_ALL}"
            f" - Updated: {self.updated_at.strftime('%B %d, %Y')}"
            f"\n {self.description}"
        )

    def _refresh_updated_at(self):
        self._updated_at = datetime.now(timezone.utc)

    @update_time_stamp
    def update_description(self, new_description: str) -> None:
        self._description = new_description

    @update_time_stamp
    def update_status(self, status: TaskStatus) -> None:
        self._status = status

@dataclass(frozen=True)
class TaskDTO:
    task_id: int
    description: str
    status: str
    created_at: str
    updated_at: str

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
            description = task_dto.description,
            status = status,
            task_id = task_dto.task_id,
            created_at = created_at,
            updated_at = updated_at,
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