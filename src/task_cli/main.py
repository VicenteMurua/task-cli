from platformdirs import  user_data_dir
from pathlib import Path
from task_cli.domain.task_manager import TaskManager
from task_cli.repository.task_repository import JSONTaskRepository, ITaskRepository
from task_cli.ui.command_interface import CommandInterface

def generate_path_dir(app_name: str = "task_cli") -> Path:
    path_dir = Path(user_data_dir(app_name))
    path_dir.mkdir(parents=True, exist_ok=True)
    return path_dir

def main():

    path_dir = generate_path_dir()
    json_path = path_dir / "task.json"
    repo: ITaskRepository = JSONTaskRepository(json_path)

    task_manager = TaskManager(repo)
    cli_handler = CommandInterface(task_manager)
    cli_handler.run()

if __name__ == "__main__":
    main()