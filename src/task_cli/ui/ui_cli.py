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
        parser_add.add_argument("descripcion", help="Descripción de la tarea")
        parser_add.set_defaults(func =self._cmd_add)

        # ------------------------ update ------------------------ #
        parser_update = subparsers.add_parser("update", help="Cambia descripción de tarea")
        parser_update.add_argument("id", type=int, help="id de la tarea")
        parser_update.add_argument("descripcion", help="Descripción de la tarea")
        parser_update.set_defaults(func =self._cmd_update)

        # ------------------------ delete ------------------------ #
        parser_delete = subparsers.add_parser("delete", help="Elimina una tarea")
        parser_delete.add_argument("id", type=int, help="id de la tarea")
        parser_delete.set_defaults(func =self._cmd_delete)

        # ------------------------ mark-done ------------------------ #
        parser_mark_done = subparsers.add_parser("mark-done", status="done", help="Marca 'done' una tarea")
        parser_mark_done.add_argument("id", type=int, help="id de la tarea")
        parser_mark_done.set_defaults(func =self._cmd_mark)
        # ------------------------ mark-in-progress ------------------------ #
        parser_mark_in_progress = subparsers.add_parser("mark-in-progress", status="in-progress", help="Marca 'in-progress' una tarea")
        parser_mark_in_progress.add_argument("id", type=int, help="id de la tarea")
        parser_mark_in_progress.set_defaults(func=self._cmd_mark)
        # ------------------------ list ------------------------ #
        parser_list = subparsers.add_parser("list", help="Lista todas las tareas")
        parser_list.set_defaults(func =self._cmd_list)

    def run(self) -> None:
        args = self._parser.parse_args(sys.argv[1:])
        args.func(args)

    def _cmd_add(self, args: argparse.Namespace) -> None:
        self._manager.add(args.descripcion)

    def _cmd_update(self, args: argparse.Namespace) -> None:
        self._manager.update(args.id, args.descripcion)

    def _cmd_delete(self, args: argparse.Namespace) -> None:
        self._manager.delete(args.id)

    def _cmd_mark(self, args: argparse.Namespace) -> None:
        self._manager.mark(args.status, args.id)

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