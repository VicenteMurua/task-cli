from task_cli.domain.task_manager import TaskManager
from task_cli.infrastructure.factories import make_task_repository, make_config_manager
from task_cli.infrastructure.enums import RepoType
from task_cli.repository.task_repository import IRepository
from task_cli.ui.command_interface import CommandInterface


def main():
    config_manager = make_config_manager()
    repo: IRepository = make_task_repository(config_manager)
    task_manager = TaskManager(repo)
    cli_handler = CommandInterface(task_manager, config_manager)
    cli_handler.run()

if __name__ == "__main__":
    main()