"""
Repository factory utilities.

This module provides a factory function to create task repository
instances based on the selected storage backend. It supports
multiple persistence implementations such as JSON, CSV, and SQLite.

The repository is stored in the user's data directory provided
by `platformdirs`.
"""
from pathlib import Path
from platformdirs import user_data_dir

from task_cli.infrastructure.enums import RepoType
from task_cli.repository.task_repository import (
    FileRepository, JSONStorage, CSVStorage, SQLiteRepository, IRepository
)
from task_cli.infrastructure.config import ConfigJson

repo_factories = {
    RepoType.JSON: lambda path: FileRepository(JSONStorage(path)),
    RepoType.CSV: lambda path: FileRepository(CSVStorage(path)),
    RepoType.SQLITE: lambda path: SQLiteRepository(path),
}


def make_task_repository(config: ConfigJson) -> IRepository:
    """
    Create a task repository using the specified storage backend.

    The repository is stored inside the user's data directory
    determined by `platformdirs`.

    Parameters
    ----------
    config :
        toda la data importante

    Returns
    -------
    IRepository
        Repository instance configured with the selected storage backend.

    Raises
    ------
    ValueError
        If an unsupported repository type is provided.
    """
    repo_name = config.get("repo_type")
    repo_type = RepoType(repo_name)
    factory = repo_factories.get(repo_type)
    current_user = config.get("current_user")
    if factory is None:
        raise ValueError(f"Unknown repository type: {repo_type}")

    path_dir = Path(user_data_dir(appname="task_cli", appauthor=False))
    user_path = path_dir / current_user
    user_path.mkdir(parents=True, exist_ok=True)

    file_dir = user_path / f"task.{repo_type.value}"

    return factory(file_dir)

def make_config_manager() -> ConfigJson:
    """
    Factory to create a ConfigJson manager stored in the user's config directory.

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