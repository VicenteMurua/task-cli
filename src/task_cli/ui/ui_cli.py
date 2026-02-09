from task_cli.domain.task_manager import TaskManager
from task_cli.domain.task import Task
import sys
import argparse


class TaskCli:
    _manager: TaskManager

    def __init__(self, manager: TaskManager):
        self._manager = manager
        self._parser = argparse.ArgumentParser(prog="task-cli")
        self._setup_all_commands()

    def run(self) -> None:
        args = self._parser.parse_args(sys.argv[1:])
        args.func(args)

    def _cmd_add(self, args: argparse.Namespace) -> None:
        self._manager.add(args.description)

    def _cmd_update(self, args: argparse.Namespace) -> None:
        self._manager.update(args.task_id, args.description)

    def _cmd_delete(self, args: argparse.Namespace) -> None:
        self._manager.delete(args.task_id)

    def _cmd_mark(self, args: argparse.Namespace) -> None:
        self._manager.mark(args.status, args.task_id)

    def _cmd_list(self, args: argparse.Namespace) -> None:
        task_list: list[Task] = list(self._manager.filtrar(args.filter).values())
        if not task_list:
            print(
                "No tasks are scheduled under this filter. "
                "You can add a new task with 'add' or change the filter to see other tasks."
            )
            return
        for task in task_list:
            print(task)

    def _setup_all_commands(self):
        command_registry: argparse._SubParsersAction = self._parser.add_subparsers(dest="command", required=True)
        self._setup_add_command(command_registry)
        self._setup_update_command(command_registry)
        self._setup_delete_command(command_registry)
        self._setup_mark_done_command(command_registry)
        self._setup_mark_in_progress_command(command_registry)
        self._setup_list_command(command_registry)

    def _setup_add_command(self, command_registry: argparse._SubParsersAction):
        parser_add = command_registry.add_parser(
            "add",
            help = "Add a new task to the tracker"
        )
        parser_add.add_argument(
            "description",
            help = "The description text of the task"
        )
        parser_add.set_defaults(func = self._cmd_add)

    def _setup_update_command(self, command_registry: argparse._SubParsersAction):
        parser_update = command_registry.add_parser(
            "update",
            help = "Change the description of an existing task"
        )
        parser_update.add_argument(
            "task_id",
            type = int,
            help = "Unique identifier of the task to update"
        )
        parser_update.add_argument(
            "description",
            help = "New description text"
        )
        parser_update.set_defaults(func = self._cmd_update)

    def _setup_delete_command(self, command_registry: argparse._SubParsersAction):
        parser_delete = command_registry.add_parser(
            "delete",
            help = "Permanently remove a task from the list"
        )
        parser_delete.add_argument(
            "task_id",
            type = int,
            help = "ID of the task to be deleted"
        )
        parser_delete.set_defaults(func = self._cmd_delete)

    def _setup_mark_done_command(self, command_registry: argparse._SubParsersAction):
        parser_mark_done = command_registry.add_parser(
            "mark-done",
            help = "Set a task status to 'done'"
        )
        parser_mark_done.add_argument(
            "task_id",
            type = int,
            help = "ID of the task to complete"
        )
        parser_mark_done.set_defaults(
            func = self._cmd_mark,
            status = "done"
        )

    def _setup_mark_in_progress_command(self, command_registry: argparse._SubParsersAction):
        parser_mark_in_progress = command_registry.add_parser(
            "mark-in-progress",
            help = "Set a task status to 'in-progress'"
        )
        parser_mark_in_progress.add_argument(
            "task_id",
            type = int,
            help = "ID of the task currently being worked on"
        )
        parser_mark_in_progress.set_defaults(
            func = self._cmd_mark,
            status = "in-progress"
        )

    def _setup_list_command(self, command_registry: argparse._SubParsersAction):
        parser_list = command_registry.add_parser(
            "list",
            help = "Display tasks based on their current status"
        )
        parser_list.add_argument(
            "filter",
            nargs = "?",
            default = None,
            choices = ["done", "in-progress", "todo"],
            help = "Filter by: todo, in-progress, or done (optional)"
        )
        parser_list.set_defaults(func = self._cmd_list)
