from datetime import datetime, timezone
from functools import wraps
from enum import Enum
import locale
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
from colorama import Fore, Style, init
init(autoreset=True)

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"
def actualizar(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        resultado = func(self, *args, **kwargs)
        self._actualizar()  # llama al method privado de la clase
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
        return (
            f"\n{'-' * 100}\n"
            f"Creación: {self._created_at.strftime('%d de %B del %Y')}"
            f" - {Fore.GREEN}Tarea #{self._id} [{self.status.value}] {Style.RESET_ALL}"
            f" - Última actualización: {self._updated_at.strftime('%d de %B del %Y')}"
            f"\n {self._description}"
        )

    def _actualizar(self):
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