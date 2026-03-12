from abc import ABC, abstractmethod
from pathlib import Path
from task_cli.domain.dtos import TaskDTO
from task_cli.domain.exceptions import TaskNotFoundError, TaskAlreadyExistsError, NoTaskToList
from task_cli.domain.task import TaskStatus
from task_cli.repository.mappers import TaskMapper
from functools import wraps
import sqlite3
import csv
import json


def ensure_active(method):
    """
    Decorator ensuring that repository operations are executed
    only when the repository context is active.

    This decorator calls the repository's `_ensure_active` method
    before executing the wrapped operation, preventing access to
    repository methods outside the context manager lifecycle.

    Parameters
    ----------
    method : callable
        Repository method to wrap.

    Returns
    -------
    callable
        Wrapped method that verifies repository activation.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._ensure_active()
        return method(self, *args, **kwargs)
    return wrapper

class IStorage(ABC):
    """
    Abstract interface for low-level storage backends.

    Storage implementations are responsible only for loading
    and saving serialized task data. They do not implement
    repository semantics such as validation or filtering.
    """
    @abstractmethod
    def load(self) -> dict[int, dict]:
        """
        Load serialized task data from the storage backend.

        Returns
        -------
        dict[int, dict]
            Mapping of task identifiers to serialized task records.
        """
        pass
    @abstractmethod
    def save(self, tasks_by_id: dict[int, dict]) -> None:
        """
        Persist serialized task data to the storage backend.

        Parameters
        ----------
        tasks_by_id : dict[int, dict]
            Mapping of task identifiers to serialized task records.
        """
        pass

class ConfigJson:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.configs = {}
        self._load()

    def _ensure_file(self) -> None:
        if not self.path.exists():
            self.path.write_text(json.dumps({"lang": "en"}), encoding="utf-8")

    def _load(self):
        self._ensure_file()
        with open(self.path, 'r', encoding='utf-8') as file:
            self.configs = json.load(file)

    def _save(self):
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(self.configs, file, ensure_ascii=False, indent=4)

    def change_config(self, key: str, value: str) -> None:
        if key in self.configs:
            self.configs[key] = value
        else:
            raise ValueError("Eso no se puede poner acá")
        self._save()

    def get(self, key: str, default=None):
        if key in self.configs.keys():
            return self.configs.get(key, default)
        else:
            raise ValueError("Eso no está acá")


class IRepository(ABC):
    """
    Abstract repository interface for task persistence.

    Repositories provide a higher-level abstraction over
    storage mechanisms, exposing CRUD operations and
    query capabilities for `TaskDTO` objects.

    Implementations must be used as context managers in
    order to manage resource lifecycles (e.g., files,
    database connections).
    """
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def _ensure_active(self):
        pass

    @abstractmethod
    def get_max_id(self) -> int:
        pass

    @abstractmethod
    def add(self, new_data: TaskDTO) -> None:
        pass

    @abstractmethod
    def update(self, updated_data: TaskDTO) -> None:
        pass

    @abstractmethod
    def delete(self, id_to_delete: int) -> None:
        pass

    @abstractmethod
    def read(self, id_to_read: int) -> TaskDTO:
        pass

    @abstractmethod
    def filter_by_status(self, status: TaskStatus|None) -> list[TaskDTO]:
        pass


class JSONStorage(IStorage):
    """
    Storage backend that persists tasks in a JSON file.

    Tasks are stored as a list of serialized dictionaries.
    The storage layer is responsible only for reading and
    writing the file; higher-level logic is handled by
    the repository layer.
    """
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def _ensure_file(self) -> None:
        """
        Ensure that the storage file exists.

        If the file does not exist, it is created with an empty
        structure compatible with the storage format.
        """
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def load(self) -> dict[int, dict]:
        """
        Load tasks from the JSON file.

        Returns
        -------
        dict[int, dict]
            Mapping of task identifiers to serialized task records.
        """
        self._ensure_file()
        tasks_by_id: dict[int,dict] = {}

        with open(self.path, 'r', encoding='utf-8') as file:
            raw_tasks: list[dict] = json.load(file)

        for task_entry in raw_tasks:
            tasks_by_id[int(task_entry["task_id"])] = task_entry

        return tasks_by_id

    def save(self, tasks_by_id: dict[int, dict]) -> None:
        """
        Persist task records to the JSON file.

        Parameters
        ----------
        tasks_by_id : dict[int, dict]
            Mapping of task identifiers to serialized task records.
        """
        # es un requerimiento de json.dump pasar la lista no una vista
        task_json_format: list[dict] = list(tasks_by_id.values())
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(task_json_format, file, ensure_ascii=False, indent=4)

class CSVStorage(IStorage):
    """
    Storage backend that persists tasks in a CSV file.

    Tasks are stored as rows in a CSV file with predefined
    column headers. All values are serialized as strings
    to preserve compatibility with CSV format constraints.
    """
    _HEADER = ["task_id", "status", "description", "created_at", "updated_at"]
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def _ensure_file(self) -> None:
        """
        Ensure that the storage file exists.

        If the file does not exist, it is created with an empty
        structure compatible with the storage format.
        """
        if not self.path.exists():
            # es un requerimiento de csv utilizar el parametro newline en ''
            with open(self.path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self._HEADER, delimiter=';')
                writer.writeheader()

    def load(self) -> dict[int, dict]:
        self._ensure_file()
        tasks_by_id: dict[int, dict] = {}

        with open(self.path, 'r', encoding='utf-8') as file:
            raw_tasks= csv.DictReader(file, delimiter=';')
            # Aca no es como el json porque el json carga los datos mientras que el csv itera mientras lee
            for task_entry in raw_tasks:
                tasks_by_id[int(task_entry["task_id"])] = task_entry

        return tasks_by_id

    def save(self, tasks_by_id: dict[int, dict]) -> None:
        with open(self.path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self._HEADER, delimiter=';')
            writer.writeheader()
            for task_entry in tasks_by_id.values():
                row: dict[str, str] = {}
                for key, value in task_entry.items():
                    row[key] = str(value) # cuidamos integridad del csv
                writer.writerow(row)


class IBulkRepository(IRepository, ABC):
    pass

class FileRepository(IBulkRepository):
    """
    Repository implementation backed by a file-based storage.

    This repository loads all tasks into memory when entering
    the context manager and writes them back to storage when
    exiting successfully.

    It operates on a dictionary mapping task identifiers
    to serialized task records.
    """
    def __init__(self, storage: IStorage) -> None:
        self.storage = storage
        self.tasks_by_id = None

    def __enter__(self) -> "FileRepository":
        """
        Load all tasks from storage into memory.

        Returns
        -------
        FileRepository
            Active repository instance.
        """
        self.tasks_by_id = self.storage.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Persist in-memory changes to storage when exiting the context.

        If an exception occurs, changes are discarded.
        """
        if exc_type:
            pass
        else:
            self.storage.save(self.tasks_by_id)
        self.tasks_by_id = None
        return False

    def _ensure_active(self):
        """
        Ensure that the repository is currently active.

        Raises
        ------
        RuntimeError
            If the repository is accessed outside its context manager.
        """
        if self.tasks_by_id is None:
            raise RuntimeError("Repository must be used within a context manager")

    @ensure_active
    def get_max_id(self) -> int:
        return max(self.tasks_by_id.keys(), default=0)

    @ensure_active
    def add(self, new_data: TaskDTO) -> None:
        tasks_by_id = self.tasks_by_id

        if new_data.task_id in tasks_by_id:
            raise TaskAlreadyExistsError(new_data.task_id)

        tasks_by_id[new_data.task_id] = TaskMapper.to_dict(new_data)

    @ensure_active
    def update(self, updated_data: TaskDTO) -> None:
        tasks_by_id = self.tasks_by_id

        if updated_data.task_id not in tasks_by_id:
            raise TaskNotFoundError(updated_data.task_id)

        tasks_by_id[updated_data.task_id] = TaskMapper.to_dict(updated_data)

    @ensure_active
    def delete(self, id_to_delete: int) -> None:
        tasks_by_id = self.tasks_by_id

        if id_to_delete not in tasks_by_id:
            raise TaskNotFoundError(id_to_delete)

        del tasks_by_id[id_to_delete]

    @ensure_active
    def read(self, id_to_read: int) -> TaskDTO:
        tasks_by_id = self.tasks_by_id

        if id_to_read not in tasks_by_id:
            raise TaskNotFoundError(id_to_read)

        return TaskMapper.from_dict(tasks_by_id[id_to_read])

    @ensure_active
    def filter_by_status(self, status_filter: TaskStatus|None = None) -> list[TaskDTO]:
        tasks_by_id = self.tasks_by_id

        if not isinstance(status_filter, (TaskStatus, type(None))):
            raise TypeError(f"Invalid status filter: {status_filter}")

        task_list = [
            TaskMapper.from_dict(task)
            for task in tasks_by_id.values()
            if task["status"] == status_filter.value
        ]

        if task_list:
            return task_list
        raise NoTaskToList(status_filter)


class IDirectAccessRepository(IRepository, ABC):
    pass

class SQLiteRepository(IDirectAccessRepository):
    """
    Repository implementation backed by an SQLite database.

    Unlike file-based repositories, this implementation performs
    direct SQL operations against the database instead of loading
    all tasks into memory.

    The repository manages database connections through the
    context manager protocol.
    """
    def __init__(self, db_path: Path):
        self.path: Path = db_path
        self.conn = None
        pass

    def __enter__(self) -> "SQLiteRepository":
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_table()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn is not None:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()
            self.conn = None
        return False

    def _ensure_active(self):
        """
        Ensure that the tasks table exists in the database.

        The table is created automatically if it does not exist.
        This allows the repository to initialize a new database
        without requiring manual schema setup.
        """
        if self.conn is None:
            raise RuntimeError("Repository must be used within a context manager")

    def _ensure_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY,
        description TEXT,
        status text,
        created_at TEXT,
        updated_at TEXT
        ) 
        """
        self.conn.execute(query)

    @ensure_active
    def get_max_id(self) -> int:
        """
        Return the highest task identifier currently stored.

        Returns
        -------
        int
            Maximum task ID, or 0 if no tasks exist.
        """
        query = """
        SELECT IFNULL(MAX(task_id), 0) AS max_id
        FROM tasks
        """
        cursor = self.conn.execute(query)
        row = cursor.fetchone()
        return row["max_id"]

    @ensure_active
    def add(self, new_data: TaskDTO) -> None:
        query = """
        INSERT INTO tasks (task_id, description, status, created_at, updated_at)
        VALUES (:task_id, :description, :status, :created_at, :updated_at)
        """
        record = TaskMapper.to_dict(new_data)
        try:
            self.conn.execute(query, record)
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: tasks.task_id" in str(e):
                raise TaskAlreadyExistsError(new_data.task_id)
            raise #pragma: no cover

    @ensure_active
    def update(self, updated_data: TaskDTO) -> None:
        query = """
        UPDATE tasks
        SET description = :description, status = :status, updated_at = :updated_at
        WHERE task_id = :task_id
        """
        record: dict = TaskMapper.to_dict(updated_data)
        cursor = self.conn.execute(query, record)
        if cursor.rowcount == 0:
            raise TaskNotFoundError(updated_data.task_id)

    @ensure_active
    def delete(self, id_to_delete: int) -> None:
        query = """
        DELETE FROM tasks
        WHERE task_id = :task_id
        """
        cursor = self.conn.execute(query, {"task_id": id_to_delete})
        if cursor.rowcount == 0:
            raise TaskNotFoundError(id_to_delete)

    @ensure_active
    def read(self, id_to_read: int) -> TaskDTO:
        query = """
            SELECT *
            FROM tasks
            WHERE task_id = :task_id
            """
        cursor = self.conn.execute(query, {"task_id": id_to_read})
        row = cursor.fetchone()
        if row is None:
            raise TaskNotFoundError(id_to_read)
        return TaskMapper.from_dict(dict(row))



    @ensure_active
    def filter_by_status(self, status_filter: TaskStatus | None) -> list[TaskDTO]:
        """
        Retrieve tasks filtered by status.

        Parameters
        ----------
        status_filter : TaskStatus or None, optional
            Status used to filter tasks. If None, all tasks are returned.

        Returns
        -------
        list[TaskDTO]
            List of tasks matching the filter.
        """
        if status_filter is None:
            query = "SELECT * FROM tasks"
            cursor = self.conn.execute(query)
            rows = cursor.fetchall()
            return [TaskMapper.from_dict(dict(row)) for row in rows]

        if not isinstance(status_filter, TaskStatus):
            raise TypeError(f"Invalid status filter: {status_filter}")
        query = """
        SELECT *
        FROM tasks
        WHERE status = :status
        """
        cursor = self.conn.execute(query, {"status": status_filter.value})

        rows = cursor.fetchall()
        task_list = [TaskMapper.from_dict(dict(row)) for row in rows]
        if task_list is not None:
            return task_list
        raise NoTaskToList()