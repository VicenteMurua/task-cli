"""
Repository factory utilities.

This module provides a factory function to create task repository
instances based on the selected storage backend. It supports
multiple persistence implementations such as JSON, CSV, and SQLite.

The repository is stored in the user's data directory provided
by `platformdirs`.
"""
from enum import Enum
from pathlib import Path
from platformdirs import user_data_dir, user_config_dir
from task_cli.repository.task_repository import (
    FileRepository, JSONStorage, CSVStorage, SQLiteRepository, IRepository, ConfigJson
)



class RepoType(str, Enum):
    """
    Supported repository storage backends.

    Each value represents a persistence strategy used to
    create a concrete repository implementation.
    """
    JSON = "json"
    CSV = "csv"
    SQLite = "sqlite"


repo_factories = {
    RepoType.JSON: lambda path: FileRepository(JSONStorage(path)),
    RepoType.CSV: lambda path: FileRepository(CSVStorage(path)),
    RepoType.SQLite: lambda path: SQLiteRepository(path),
}


def make_task_repository(repo_type: RepoType = RepoType.SQLite) -> IRepository:
    """
    Create a task repository using the specified storage backend.

    The repository is stored inside the user's data directory
    determined by `platformdirs`.

    Parameters
    ----------
    repo_type : RepoType, optional
        Storage backend to use. Defaults to SQLite.

    Returns
    -------
    IRepository
        Repository instance configured with the selected storage backend.

    Raises
    ------
    ValueError
        If an unsupported repository type is provided.
    """
    factory = repo_factories.get(repo_type)
    if factory is None:
        raise ValueError(f"Unknown repository type: {repo_type}")

    path_dir = Path(user_data_dir("task_cli"))
    path_dir.mkdir(parents=True, exist_ok=True)

    file_dir = path_dir / f"task.{repo_type.value}"

    return factory(file_dir)

def make_config_manager() -> ConfigJson:
    """
    Factory to create a ConfigJson manager stored in the user's config directory.

    Parameters
    ----------
    app_name : str
        Name of the application, used to create a config folder.

    Returns
    -------
    ConfigJson
        Instance of ConfigJson ready to read/write configuration.
    """
    app_name = "task_cli"
    config_dir = Path(user_data_dir(app_name))
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "config.json"
    return ConfigJson(config_file)