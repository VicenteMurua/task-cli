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
    _description: str
    _status: TaskStatus
    _id: int
    _created_at: datetime
    _updated_at: datetime

    def __init__(self,
                 description: str,
                 status: TaskStatus,
                 _id: int,
                 created_at: datetime | None = None,
                 updated_at: datetime | None = None,
                 ):
        if (created_at is None) ^ (updated_at is None):
            raise ValueError("CreatedAt and updatedAt must both be None or defined")
        self._description = description
        self._status = status
        self._id = _id
        self._created_at = datetime.now(timezone.utc) if created_at is None\
            else created_at
        self._updated_at = self._created_at if updated_at is None\
            else updated_at
    @property
    def identificador(self) -> int:
        return self._id

    @property
    def status(self):
        return self._status

    def __str__(self):
        return f"id: {self._id}, status: {self.status}\n"\
               f"tarea: {self._description} \n"\
               f"created_at: {self._created_at}, updated_at: {self._updated_at}"

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
            "description": self._description,
            "status": self._status.value,
            "id": self._id,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }