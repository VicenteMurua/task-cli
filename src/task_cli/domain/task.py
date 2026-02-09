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
    def task_id(self) -> int:
        return self._task_id

    @property
    def status(self):
        return self._status

    def __str__(self):
        return (
            f"\n{'-' * 100}\n"
            f"Created: {self._created_at.strftime('%B %d, %Y')}"
            f" - {Fore.GREEN}Task #{self._task_id} [{self.status.value}] {Style.RESET_ALL}"
            f" - Updated: {self._updated_at.strftime('%B %d, %Y')}"
            f"\n {self._description}"
        )

    def _refresh_updated_at(self):
        self._updated_at = datetime.now(timezone.utc)

    @update_time_stamp
    def update_description(self, new_description: str) -> None:
        self._description = new_description

    @update_time_stamp
    def update_status(self, status: TaskStatus) -> None:
        self._status = status

    def to_dict(self) -> dict:
        return {
            "description": self._description,
            "status": self._status.value,
            "id": self._task_id,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }