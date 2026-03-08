from colorama import Fore, Style
from task_cli.domain.exceptions import TaskException, TaskValidationError, TaskNotFoundError, NoTaskOnFilter
from task_cli.domain.task import TaskStatus
from task_cli.ui.formatters import TaskCliFormatter, TableStyle
from task_cli.domain.task_manager import TaskManager
from task_cli.domain.dtos import TaskDTO
from task_cli.ui.messages.commands import Msgs, action_msgs, Action, feedback_msgs, commands_data
import sys
import argparse


def show_error(exc: TaskException, style: TableStyle, lang: str = "en") -> None:
    """
    Muestra en consola un error de Task usando TaskCliFormatter.
    Usa ERROR_CATALOG y RETRY_MESSAGES para multi lenguaje.
    """
    print(TaskCliFormatter.format_client_error(exc, style, lang=lang))

class CommandInterface:
    _manager: TaskManager

    def __init__(self, manager: TaskManager, style: bool = False, lang: str = "en") -> None:
        self._manager = manager
        self.style = style
        self.lang = lang

        self.texts = commands_data.get(self.lang, commands_data["en"])

        self._parser = argparse.ArgumentParser(prog="task-cli")
        self._setup_all_commands()

    def run(self) -> None:
        args = self._parser.parse_args(sys.argv[1:])

        try:
            args.func(args)

        # 1. Errores que el usuario PUEDE arreglar (Validación y Búsqueda)
        except (TaskValidationError, TaskNotFoundError, NoTaskOnFilter) as exc:
            style = TableStyle(self.style)
            show_error(exc, style, lang=self.lang)

        # 2. Errores que el programador DEBE arreglar (Bugs de lógica)
        except TaskException as exc:
            # Aquí no usamos "show_error" porque no queremos el mensaje de "reintenta"
            print(f"{Fore.RED}[SISTEMA] Error de lógica interna: {type(exc).__name__}")
            print(f"Detalle técnico: {exc}{Style.RESET_ALL}")

        # 3. Errores catastróficos (Se cortó la luz, no hay disco, etc.)
        except Exception as e:
            print(f"{Fore.RED}FATAL: Ocurrió un error inesperado. {type(e).__name__}: {e}{Style.RESET_ALL}")
    def show_feedback(self, task: TaskDTO, style: bool=False) -> None:
        print(feedback_msgs[self.lang][Msgs.SHOW])
        print(TaskCliFormatter.format_task_detail(task, TableStyle(style)))

    def quick_show_feedback(self, task: TaskDTO, style: bool=False) -> None:
        print(feedback_msgs[self.lang][Msgs.LIST])
        print(TaskCliFormatter.format_task_table(task, TableStyle(style)))

    def quick_show_list(self, tasks: list[TaskDTO], style: bool=False) -> None:
        print(feedback_msgs[self.lang][Msgs.SHOW])
        print(TaskCliFormatter.format_tasks_table(tasks, TableStyle(style)))

    def _cmd_add(self, args: argparse.Namespace) -> None:
        task:TaskDTO = self._manager.add(args.description)
        self.show_feedback(task, self.style)
        print(action_msgs[self.lang][Action.ADD])

    def _cmd_update(self, args: argparse.Namespace) -> None:
        task: TaskDTO = self._manager.update(args.task_id, args.description)
        self.show_feedback(task, self.style)
        print(action_msgs[self.lang][Action.UPDATE])

    def _cmd_delete(self, args: argparse.Namespace) -> None:
        task: TaskDTO = self._manager.delete(args.task_id)
        self.show_feedback(task, self.style)
        print(action_msgs[self.lang][Action.DELETE])

    def _cmd_read(self, args: argparse.Namespace) -> None:
        task: TaskDTO = self._manager.read(args.task_id)
        if args.detail:
            self.show_feedback(task, self.style)
        else:
            self.quick_show_feedback(task, self.style)
        print(action_msgs[self.lang][Action.READ])

    def _cmd_mark(self, args: argparse.Namespace) -> None:
        task: TaskDTO = self._manager.mark(args.status, args.task_id)
        self.show_feedback(task, self.style)
        print(action_msgs[self.lang][Action.MARK])

    def _cmd_list(self, args: argparse.Namespace) -> None:
        task_list: list[TaskDTO] = self._manager.filter_by_status(args.filter)
        if not task_list:
            raise NoTaskOnFilter(args.filter)
        self.quick_show_list(task_list, self.style)

    def _setup_all_commands(self):
        command_registry: argparse._SubParsersAction = self._parser.add_subparsers(dest="command", required=True)
        self._setup_add_command(command_registry)
        self._setup_update_command(command_registry)
        self._setup_delete_command(command_registry)
        self._setup_mark_done_command(command_registry)
        self._setup_mark_in_progress_command(command_registry)
        self._setup_list_command(command_registry)
        self._setup_read_command(command_registry)

    def _setup_add_command(self, command_registry: argparse._SubParsersAction):
        data = self.texts[Action.ADD]
        command = data["command"]
        description = data["parser1"]
        parser_add = command_registry.add_parser(
            name=command["name"],
            help=command["help"]
        )
        parser_add.add_argument(
            description["name"],
            help=description["help"]
        )
        parser_add.set_defaults(func = self._cmd_add)

    def _setup_update_command(self, command_registry: argparse._SubParsersAction):
        data = self.texts[Action.UPDATE]
        command = data["command"]
        task_id = data["parser1"]
        description = data["parser2"]
        parser_update = command_registry.add_parser(
            name=command["name"],
            help=command["help"]
        )
        parser_update.add_argument(
            task_id["name"],
            type=int,
            help=task_id["help"]
        )
        parser_update.add_argument(
            description["name"],
            help=description["help"]
        )
        parser_update.set_defaults(func = self._cmd_update)

    def _setup_delete_command(self, command_registry: argparse._SubParsersAction):
        data = self.texts[Action.DELETE]
        command = data["command"]
        task_id = data["parser1"]
        parser_delete = command_registry.add_parser(
            name=command["name"],
            help=command["help"]
        )
        parser_delete.add_argument(
            task_id["name"],
            type=int,
            help=task_id["help"]
        )
        parser_delete.set_defaults(func = self._cmd_delete)

    def _setup_read_command(self, command_registry: argparse._SubParsersAction):
        data = self.texts[Action.READ]
        command = data["command"]
        task_id = data["parser1"]
        detail  = data["parser2"]
        parser_read = command_registry.add_parser(
            name=command["name"],
            help=command["help"]
        )
        parser_read.add_argument(
            task_id["name"],
            type=int,
            help=task_id["help"]
        )
        parser_read.add_argument(
            detail["name"],
            detail["long name"],
            action="store_true",
            help=detail["help"]
        )
        parser_read.set_defaults(func = self._cmd_read)

    def _setup_mark_done_command(self, command_registry: argparse._SubParsersAction):
        data = self.texts[Action.MARK_DONE]
        command = data["command"]
        task_id = data["parser1"]
        parser_mark_done = command_registry.add_parser(
            name=command["name"],
            help=command["help"]
        )
        parser_mark_done.add_argument(
            task_id["name"],
            type = int,
            help = task_id["help"]
        )
        parser_mark_done.set_defaults(
            func = self._cmd_mark,
            status=TaskStatus.DONE
        )

    def _setup_mark_in_progress_command(self, command_registry: argparse._SubParsersAction):
        data = self.texts[Action.MARK_IN_PROGRESS]
        command = data["command"]
        task_id = data["parser1"]
        parser_mark_in_progress = command_registry.add_parser(
            name=command["name"],
            help=command["help"]
        )
        parser_mark_in_progress.add_argument(
            task_id["name"],
            type = int,
            help=task_id["help"]
        )
        parser_mark_in_progress.set_defaults(
            func = self._cmd_mark,
            status = TaskStatus.IN_PROGRESS
        )

    def _setup_list_command(self, command_registry: argparse._SubParsersAction):
        data = self.texts[Action.LIST]
        command = data["command"]
        filter_tasks = data["parser1"]
        parser_list = command_registry.add_parser(
            name=command["name"],
            help=command["help"]
        )
        parser_list.add_argument(
            filter_tasks["name"],
            nargs="?",
            default=None,
            choices=filter_tasks["choices"],
            help=filter_tasks["help"]
        )
        parser_list.set_defaults(func = self._cmd_list)
