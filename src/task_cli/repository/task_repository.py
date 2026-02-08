from abc import ABC, abstractmethod
from pathlib import Path
from task_cli.domain.task import Task, TaskStatus
from datetime import datetime
import json

class ITaskRepository(ABC):

    @abstractmethod
    def load(self) -> list[tuple[str, str, int, datetime, datetime]]:
        pass

    @abstractmethod
    def save(self, lista_tareas: list[Task]) -> None:
        pass

class JSONTaskRepository(ITaskRepository):
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def load(self) -> list[tuple[str, TaskStatus, int, datetime, datetime]]:

        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")
        lista_datos_tareas: list[tuple[str, TaskStatus, int, datetime, datetime]] = []
        with open(self.path, 'r', encoding='utf-8') as archivo:
            datos_crudos = json.load(archivo)
            for datos in datos_crudos:
                descripcion: str = datos['description']
                estado: TaskStatus = TaskStatus(datos['status'])
                identificador: int = int(datos['id'])
                creacion: datetime = datetime.fromisoformat(datos['created_at'])
                actualizacion: datetime = datetime.fromisoformat(datos['updated_at'])
                argumento = descripcion, estado, identificador, creacion, actualizacion
                lista_datos_tareas.append(argumento)
        return  lista_datos_tareas

    def save(self, lista_tareas: list[Task]) -> None:
        lista_datos = []
        for tarea in lista_tareas:
            lista_datos.append(tarea.to_dict())

        with open(self.path, 'w', encoding='utf-8') as archivo:
            json.dump(lista_datos, archivo, ensure_ascii=False, indent=4)
