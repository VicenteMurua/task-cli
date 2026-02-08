from task_cli.domain.task_manager import TaskManager
from task_cli.domain.task import Task
from collections.abc import Callable
class TaskCli:
    _manager: TaskManager

    def __init__(self, manager: TaskManager):
        self._manager = manager

    def run(self, command: list[str]) -> None:
        comandos:dict[str, Callable[[list[str]], None]] = {
            "add": self._cmd_add,
            "update": self._cmd_update,
            "delete": self._cmd_delete,
            "mark-in-progress": self._cmd_mark,
            "mark-done": self._cmd_mark,
            "mark-todo": self._cmd_mark,
            "list": self._cmd_list,
        }
        largo_comando_entrada = len(command)
        if largo_comando_entrada == 1:
            raise ValueError("Sin argumentos")

        comando: str = command[1]
        # TODO: quitar ese fix y habilitar todo el programa para que los typehints acepten null
        detalle: list[str] = command[2:] if largo_comando_entrada > 2 else [""]

        if comando not in comandos:
            raise ValueError("No se ingreso comando válido")

        funcion: str = comando
        argumento: list[str] = detalle

        if "-" in comando:
            funcion, estado = comando.split("-", 1)
            argumento = [estado] + argumento
        comandos[funcion](argumento)

    def _cmd_add(self, descripcion: list[str]) -> None:
        if descripcion[0] == "":
            raise ValueError("Sin argumentos, se esperaba un argumento para la descripción de la tarea")
        if len(descripcion) > 1:
            raise ValueError("Demasiados argumentos, se esperaba un solo argumento para la descripción, pruebe el uso de comillas")
        nueva_tarea = descripcion[0]
        self._manager.add(nueva_tarea)

    def _cmd_update(self, descripcion: list[str]) -> None:
        largo_descripcion = len(descripcion)
        if largo_descripcion != 2:
            raise ValueError(f"Se proporcionaron {largo_descripcion} argumentos, se esperaban solo 2 argumentos para el subcomando update"
                             f" el id de la tarea y la descripcion nueva")
        identificador: str = descripcion[0]
        descripcion: str = descripcion[1]
        try:
            _id: int = int(identificador)
        except ValueError:
            raise ValueError("El valor asignado al identificador no es un int")
        self._manager.update(_id, descripcion)

    def _cmd_delete(self, descripcion: list[str]) -> None:
        elementos = len(descripcion)
        if elementos != 1:
            raise ValueError(
                f"Se proporcionaron {elementos} argumentos, se esperaba 1 solo argumentos para el subcomando delete"
                f" el id de la tarea a eliminar")
        if descripcion[0] == "":
            raise ValueError(
                f"Se proporcionaron 0 argumentos, se esperaba 1 argumento para el subcomando delete"
                f" el id de la tarea a eliminar")
        identificador: str = descripcion[0]
        try:
            _id: int = int(identificador)
        except ValueError:
            raise ValueError("El valor asignado al identificador no es un int")
        self._manager.delete(_id)

    def _cmd_mark(self, descripcion: list[str]) -> None:
        elementos = len(descripcion)
        accion: str = descripcion[0]
        if elementos != 1:
            raise ValueError(
                f"Se proporcionaron {elementos} argumentos, se esperaba 1 solo argumentos para el subcomando mark-{accion}"
                f" el id de la tarea a marcar")
        if descripcion[0] == "":
            raise ValueError(
                f"Se proporcionaron 0 argumentos, se esperaba 1 solo argumentos para el subcomando mark-{accion}"
                f" el id de la tarea a marcar")

        descripcion: list[str] = descripcion[1:]
        identificador: str = descripcion[0]
        try:
            _id: int = int(identificador)
        except ValueError:
            raise ValueError("El valor asignado al identificador no es un int")
        self._manager.mark(accion, _id)

    def _cmd_list(self, descripcion: list[str]):
        cantidad_argumentos = len(descripcion)
        if cantidad_argumentos != 1:
            raise ValueError(
                f"Se esperaba 0 o 1 argumentos para el subcomando list"
                f" ninguno para listar todos, o para filtrar uno de los siguientes: done, todo, in-progress")
        lista_de_tareas: list[Task] = list(self._manager.filtrar(descripcion[0]).values())
        if not lista_de_tareas:
            print("No hay tareas agendadas, en este filtro. Agregue una nueva con 'add'.")
            return
        for tarea in lista_de_tareas:
            print(tarea)