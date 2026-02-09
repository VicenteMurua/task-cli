from task_cli.domain.task_manager import TaskManager
from task_cli.domain.task import Task
import sys
from collections.abc import Callable
import argparse


class TaskCli:
    _manager: TaskManager

    def __init__(self, manager: TaskManager):
        self._manager = manager
        self._parser = argparse.ArgumentParser(prog="task-cli")
        subparsers = self._parser.add_subparsers(dest="command")
        # ------------------------ add ------------------------ #
        parser_add = subparsers.add_parser("add", help="Agrega una nueva tarea")
        parser_add.set_defaults(func =self._cmd_add)
        # ------------------------ update ------------------------ #
        parser_update = subparsers.add_parser("update", help="Cambia descripción de tarea")
        parser_update.set_defaults(func =self._cmd_update)
        # ------------------------ delete ------------------------ #
        parser_delete = subparsers.add_parser("delete", help="Elimina una tarea")
        parser_delete.set_defaults(func =self._cmd_delete)
        # ------------------------ mark-done ------------------------ #
        parser_mark = subparsers.add_parser("mark-done", help="Marca 'done' una tarea")
        parser_mark.set_defaults(func =self._cmd_mark)
        # ------------------------ mark-in-progress ------------------------ #
        parser_mark = subparsers.add_parser("mark-in-progress", help="Marca 'in-progress' una tarea")
        parser_mark.set_defaults(func=self._cmd_mark)
        # ------------------------ list ------------------------ #
        parser_list = subparsers.add_parser("list", help="Lista todas las tareas")
        parser_list.set_defaults(func =self._cmd_list)

    def run(self) -> None:
        args = self._parser.parse_args(sys.argv[1:])
        args.func(args)

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
        if elementos != 2:
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