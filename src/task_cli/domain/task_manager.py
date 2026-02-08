from task_cli.domain.task import Task, TaskStatus
from task_cli.repository.task_repository import ITaskRepository
from functools import wraps
from datetime import datetime

def guardar(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        resultado = func(self, *args, **kwargs)
        self._save()  # llama al method privado de la clase
        return resultado
    return wrapper

class TaskManager:
    def __init__(self, repository: ITaskRepository) -> None:
        self._repository: ITaskRepository = repository
        self._dict_tareas: dict[int, Task] = {}
        self._load()
        self._mayor_id: int = max(self._dict_tareas.keys(), default=0)

    def _load(self):
        for dato in self._repository.load():
            self.recomponer(dato)

    def _save(self):
        self._repository.save(list(self._dict_tareas.values()))

    @guardar
    def add(self, descripcion: str) -> None:
        self._mayor_id += 1
        nueva_tarea: Task = Task(descripcion, TaskStatus.TODO, self._mayor_id)
        self._dict_tareas[nueva_tarea.identificador] = nueva_tarea

    def recomponer(self, datos: tuple[str, str, int, datetime, datetime]) -> None:
        descripcion, estado, identificador, creado, actualizado = datos
        nueva_tarea: Task = Task(descripcion, TaskStatus(estado), identificador, creado, actualizado)
        self._dict_tareas[nueva_tarea.identificador] = nueva_tarea
    @guardar
    def update(self, identificador: int, descripcion_nueva: str) -> None:
        tarea_objetivo: Task = self._dict_tareas[identificador]
        tarea_objetivo.cambiar_descripcion(descripcion_nueva)
        self._dict_tareas.update({identificador: tarea_objetivo})
    @guardar
    def delete(self, identificador: int) -> None:
        del self._dict_tareas[identificador]
    @guardar
    def mark(self, estado: str, identificador: int) -> None:
        tarea_objetivo: Task = self._dict_tareas[identificador]
        tarea_objetivo.cambiar_estado(TaskStatus(estado))
        self._dict_tareas.update({identificador: tarea_objetivo})

    def filtrar(self, filtro: str) -> dict[int, Task]:
        tareas_filtradas: dict[int, Task] = {}
        if filtro == "":
            return self._dict_tareas
        for identificador, tarea in self._dict_tareas.items():
            if tarea.status is TaskStatus(filtro):
                tareas_filtradas.update({identificador: tarea})
        return tareas_filtradas