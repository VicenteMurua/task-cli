from pathlib import Path
from platformdirs import user_data_dir
from task_cli.repository.task_repository import (
    FileTaskRepository, JSONBulkStorage, CSVBulkStorage, SQLiteTaskRepository, ITaskRepository
)

repo_factories = {
    "json": lambda path: FileTaskRepository(JSONBulkStorage(path)),
    "csv": lambda path: FileTaskRepository(CSVBulkStorage(path)),
    "sqlite": lambda path: SQLiteTaskRepository(path),
}
file_ext = {
    "json": ".json",
    "csv": ".csv",
    "sqlite": ".sqlite"
}
def make_task_repository(repo_type: str = "json") -> ITaskRepository:
    path_dir = Path(user_data_dir("task_cli"))
    path_dir.mkdir(parents=True, exist_ok=True)

    file_dir = path_dir / f"task{file_ext[repo_type]}"

    factory = repo_factories.get(repo_type)
    if not factory:
        raise ValueError(f"Unknown repository type: {repo_type}")

    return factory(file_dir)