from datetime import datetime, timezone
from functools import wraps
from enum import Enum

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

    def __init__(
            self,
            description: str,
            task_id: int,
            status: TaskStatus|None = None,
            created_at: datetime|None = None,
            updated_at: datetime|None = None
            ):
        self.validate_description(description)
        self.validate_id(task_id)
        self.validate_status(status)
        self.validate_dates(created_at, updated_at)

        self._description = description
        self._task_id = task_id
        self._status = TaskStatus.TODO if status is None else status
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

    def validate_description(self, new_description: str) -> None:
        if not isinstance(new_description, str):
            raise ValueError("Description must be a string")
        if not new_description.strip():
            raise ValueError("Description cannot be empty")
    def validate_id(self, new_id: int) -> None:
        if not isinstance(new_id, int):
            raise ValueError("ID must be a integer")
        if new_id <= 0:
            raise ValueError("Task ID must be greater than 0")
    def validate_status(self, new_status: TaskStatus) -> None:
        if not isinstance(new_status, (TaskStatus, type(None))):
            raise ValueError("Status must be a TaskStatus o None")
    def validate_dates(self, new_created_at: datetime, new_updated_at: datetime) -> None:
        if not isinstance(new_created_at, (datetime, type(None))):
            raise ValueError("CreatedAt must be a datetime or None")
        if not isinstance(new_updated_at, (datetime, type(None))):
            raise ValueError("UpdatedAt must be a datetime or None")

        if (new_created_at is None) ^ (new_updated_at is None):
            raise ValueError("CreatedAt and updatedAt must both be None or defined")
        if new_created_at is not None and new_updated_at is not None:
            if new_created_at > new_updated_at:
                raise ValueError("CreatedAt must not be greater than UpdatedAt")

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