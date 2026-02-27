from enum import Enum
from pathlib import Path
from platformdirs import user_data_dir
from task_cli.repository.task_repository import (
    FileRepository, JSONStorage, CSVStorage, SQLiteRepository, IRepository
)

repo_factories = {
    "json": lambda path: FileRepository(JSONStorage(path)),
    "csv": lambda path: FileRepository(CSVStorage(path)),
    "sqlite": lambda path: SQLiteRepository(path),
}

file_ext = {
    "json": ".json",
    "csv": ".csv",
    "sqlite": ".sqlite"
}

class RepoType(str, Enum):
    JSON = "json"
    CSV = "csv"
    SQLite = "sqlite"

def make_task_repository(repo_type: RepoType = RepoType.SQLite) -> IRepository:
    path_dir = Path(user_data_dir("task_cli"))
    path_dir.mkdir(parents=True, exist_ok=True)

    file_dir = path_dir / f"task{file_ext[repo_type.value]}"

    factory = repo_factories.get(repo_type.value)
    if not factory:
        raise ValueError(f"Unknown repository type: {repo_type}")

    return factory(file_dir)