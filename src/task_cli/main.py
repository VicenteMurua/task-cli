from task_cli.domain.task_manager import TaskManager
from task_cli.infrastructure.factories import make_task_repository, RepoType
from task_cli.repository.task_repository import IRepository
from task_cli.ui.command_interface import CommandInterface


def main():
    repo: IRepository = make_task_repository(RepoType.SQLite)
    task_manager = TaskManager(repo)
    cli_handler = CommandInterface(task_manager, lang="es")
    cli_handler.run()

if __name__ == "__main__":
    main()