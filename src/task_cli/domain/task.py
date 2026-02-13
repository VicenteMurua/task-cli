from datetime import datetime, timezone
from functools import wraps
from enum import Enum
from colorama import Fore, Style, init
init(autoreset=True)
time_zone = timezone.utc


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
            status: TaskStatus,
            created_at: datetime|None = None,
            updated_at: datetime|None = None
            ):
        self._validate_description(description)
        self._validate_id(task_id)
        self._validate_status(status)
        self._validate_creation_date(created_at)
        self._validate_updated_date(updated_at)
        self._validate_dates_relation(new_created_at=created_at, new_updated_at=updated_at)

        self._description = description
        self._task_id = task_id
        self._status = status
        self._created_at = datetime.now(time_zone) if created_at is None\
            else created_at
        self._updated_at = self._created_at if updated_at is None\
            else updated_at

    @property
    def description(self) -> str:
        return self._description

    def _set_description(self, description: str) -> None:
        self._validate_description(description)
        self._description = description

    @property
    def status(self) -> TaskStatus:
        return self._status

    def _set_status(self, status: TaskStatus) -> None:
        self._validate_status(status)
        self._status = status

    @property
    def task_id(self) -> int:
        return self._task_id

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @staticmethod
    def _validate_description(new_description: str) -> None:
        if type(new_description) is not str:
            raise TypeError("Description must be a string")
        if not new_description.strip():
            raise ValueError("Description cannot be empty")

    @staticmethod
    def _validate_id(new_id: int) -> None:
        if type(new_id) is not int:
            raise TypeError("ID must be a integer")
        if new_id <= 0:
            raise ValueError("Task ID must be greater than 0")

    @staticmethod
    def _validate_status(new_status: TaskStatus) -> None:
        if type(new_status) is not TaskStatus:
            raise TypeError("Status must be a TaskStatus")

    @staticmethod
    def _validate_creation_date(new_date: datetime | None) -> None:
        if not isinstance(new_date, (datetime, type(None))):
            raise TypeError("CreatedAt must be a datetime or None")

    @staticmethod
    def _validate_updated_date(new_date: datetime | None) -> None:
        if not isinstance(new_date, (datetime, type(None))):
            raise TypeError("UpdatedAt must be a datetime or None")

    @staticmethod
    def _validate_dates_relation(new_created_at: datetime|None, new_updated_at: datetime|None) -> None:
        if (new_created_at is None) ^ (new_updated_at is None):
            raise ValueError("CreatedAt and updatedAt must both be None or defined at the same time")
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
        self._updated_at = datetime.now(time_zone)

    @update_time_stamp
    def update_description(self, new_description: str) -> None:
        self._set_description(new_description)

    @update_time_stamp
    def update_status(self, status: TaskStatus) -> None:
        self._set_status(status)