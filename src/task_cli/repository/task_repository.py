from abc import ABC, abstractmethod
from pathlib import Path
from task_cli.domain.dtos import TaskDTO
from task_cli.domain.exceptions import TaskNotFoundError, TaskAlreadyExistsError
from task_cli.domain.task import TaskStatus
from task_cli.repository.mappers import TaskMapper
from functools import wraps
import sqlite3
import csv
import json


def ensure_active(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._ensure_active()
        return method(self, *args, **kwargs)
    return wrapper

class IBulkStorage(ABC):
    @abstractmethod
    def load(self) -> dict[int, dict]:
        pass
    @abstractmethod
    def save(self, tasks_by_id: dict[int, dict]) -> None:
        pass

class ITaskRepository(ABC):
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


class JSONBulkStorage(IBulkStorage):
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def _ensure_file(self) -> None:
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def load(self) -> dict[int, dict]:
        self._ensure_file()
        tasks_by_id: dict[int,dict] = {}

        with open(self.path, 'r', encoding='utf-8') as file:
            raw_tasks: list[dict] = json.load(file)

        for task_entry in raw_tasks:
            tasks_by_id[int(task_entry["task_id"])] = task_entry

        return tasks_by_id

    def save(self, tasks_by_id: dict[int, dict]) -> None:
        # es un requerimiento de json.dump pasar la lista no una vista
        task_json_format: list[dict] = list(tasks_by_id.values())
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(task_json_format, file, ensure_ascii=False, indent=4)

class CSVBulkStorage(IBulkStorage):
    _HEADER = ["task_id", "status", "description", "created_at", "updated_at"]
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def _ensure_file(self) -> None:
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


class IBulkRepository(ITaskRepository, ABC):
    pass

class FileTaskRepository(IBulkRepository):
    def __init__(self, storage: IBulkStorage) -> None:
        self.storage = storage
        self.tasks_by_id = None

    def __enter__(self):
        self.tasks_by_id = self.storage.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            pass
        else:
            self.storage.save(self.tasks_by_id)
        self.tasks_by_id = None
        return False

    def _ensure_active(self):
        if self.tasks_by_id is None:
            raise RuntimeError("Repository must be used within a context manager")

    @ensure_active
    def get_max_id(self) -> int:
        return max(self.tasks_by_id.keys(), default=0)

    @ensure_active
    def add(self, new_data: TaskDTO) -> None:
        tasks_by_id = self.tasks_by_id

        if new_data.task_id in tasks_by_id:
            raise TaskAlreadyExistsError(f"Task with id {new_data.task_id} already exists")

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

        if status_filter is None:
            return [
                TaskMapper.from_dict(task)
                for task in tasks_by_id.values()
            ]

        if not isinstance(status_filter, TaskStatus):
            raise ValueError(f"Invalid status filter: {status_filter}")

        return [
            TaskMapper.from_dict(task)
            for task in tasks_by_id.values()
            if task["status"] == status_filter.value
        ]


class IDirectAccessRepository(ITaskRepository, ABC):
    pass

class SQLiteTaskRepository(IDirectAccessRepository):
    def __init__(self, db_path: Path):
        self.path: Path = db_path
        self.conn = None
        pass

    def __enter__(self):
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
                raise TaskAlreadyExistsError(
                    f"Task with id {new_data.task_id} already exists"
                )
            raise

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
        return [TaskMapper.from_dict(dict(row)) for row in rows]