from task_cli.domain.task_manager import TaskManager
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
            "list": self._cmd_list,

        }

        if len(command) == 1:
            raise ValueError("Sin argumentos")

        comando: str = command[1]
        detalle: list[str] = command[2:]
        if comando not in comandos:
            raise ValueError("No se ingreso comando válido")

        funcion: str = comando
        argumento: list[str] = detalle

        if "-" in comando:
            funcion, estado = comando.split("-", 1)
            argumento = [estado] + argumento
        comandos[funcion](argumento)

    def _cmd_add(self, descripcion: list[str]) -> None:
        if len(descripcion) == 0:
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
        identificador: str = descripcion[0]
        try:
            _id: int = int(identificador)
        except ValueError:
            raise ValueError("El valor asignado al identificador no es un int")
        self._manager.delete(_id)


    def _cmd_mark(self, descripcion: list[str]) -> None:
        accion: str = descripcion[0]
        descripcion: list[str] = descripcion[1:]
        elementos = len(descripcion)
        if elementos != 1:
            raise ValueError(
                f"Se proporcionaron {elementos} argumentos, se esperaba 1 solo argumentos para el subcomando {accion}"
                f" el id de la tarea a marcar")
        identificador: str = descripcion[0]
        try:
            _id: int = int(identificador)
        except ValueError:
            raise ValueError("El valor asignado al identificador no es un int")
        self._manager.mark(accion, _id)

    def _cmd_list(self, descripcion: list[str]):
        pass

