from task_cli.domain.task_manager import TaskManager
from task_cli.infrastructure.factories import make_task_repository
from task_cli.repository.task_repository import ITaskRepository
from task_cli.ui.command_interface import CommandInterface


def main():
    repo: ITaskRepository = make_task_repository()
    task_manager = TaskManager(repo)
    cli_handler = CommandInterface(task_manager)
    cli_handler.run()

if __name__ == "__main__":
    main()