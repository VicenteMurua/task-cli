import sys
from platformdirs import  user_data_dir
from pathlib import Path

from task_cli.domain.task_manager import TaskManager
from task_cli.repository.task_repository import JSONTaskRepository, ITaskRepository
from task_cli.ui.ui_cli import TaskCli
def main():

    app_name = "task_cli"
    data_dir = user_data_dir(app_name)
    path_dir = Path(data_dir)
    path_dir.mkdir(parents=True, exist_ok=True)
    json_path = path_dir / "task.json"
    repo: ITaskRepository = JSONTaskRepository(json_path)

    task_manager = TaskManager(repo)
    cli_handler = TaskCli(task_manager)
    cli_handler.run()

if __name__ == "__main__":
    main()