from datetime import datetime, timezone
from functools import wraps
from enum import Enum

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"
def actualizar(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        resultado = func(self, *args, **kwargs)
        self.__actualizar()  # llama al method privado de la clase
        return resultado
    return wrapper

class Task:
    _id: int
    _description: str
    _status: TaskStatus
    _created_at: datetime
    _updated_at: datetime

    def __init__(self,
                 description: str,
                 status: TaskStatus,
                 _id: int | None = None,
                 created_at: datetime | None = None,
                 updated_at: datetime | None = None,
                 ):
        if (created_at is None) ^ (updated_at is None):
            raise ValueError("CreatedAt and updatedAt must both be None or defined")
        self._description = description
        self._status = status
        self._id = new_id() if _id is None\
            else _id
        self._created_at = datetime.now(timezone.utc) if created_at is None\
            else created_at
        self._updated_at = self._created_at if updated_at is None\
            else updated_at

    def __actualizar(self):
        self._updated_at = datetime.now(timezone.utc)

    @actualizar
    def cambiar_descripcion(self, nueva_descripcion: str) -> None:
        self._description = nueva_descripcion

    @actualizar
    def cambiar_estado(self, estado: TaskStatus) -> None:
        self._status = estado

    def to_dict(self) -> dict:
        return {
            "id": self._id,
            "description": self._description,
            "status": self._status.value,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }