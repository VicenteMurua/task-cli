from abc import ABC, abstractmethod
from pathlib import Path
from task_cli.domain.dtos import TaskDTO
from task_cli.domain.exceptions import TaskNotFoundError, TaskAlreadyExistsError
from task_cli.domain.task import TaskStatus
from task_cli.repository.mappers import TaskMapper
import csv
import json


class IBulkStorage(ABC):
    @abstractmethod
    def load(self) -> dict[int, dict]:
        pass
    @abstractmethod
    def save(self, tasks_by_id: dict[int, dict]) -> None:
        pass

class ITaskRepository(ABC):
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


class JSONStorage(IBulkStorage):
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

class CSVStorage(IBulkStorage):
    _HEADER = ["task_id", "status", "description", "created_at", "updated_at"]
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def _ensure_file(self) -> None:
        if not self.path.exists():
            # es un requerimiento de csv utilizar el parametro newline en ''
            with open(self.path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self._HEADER)
                writer.writeheader()

    def load(self) -> dict[int, dict]:
        self._ensure_file()
        tasks_by_id: dict[int, dict] = {}

        with open(self.path, 'r', encoding='utf-8') as file:
            raw_tasks= csv.DictReader(file)
            # Aca no es como el json porque el json carga los datos mientras que el csv itera mientras lee
            for task_entry in raw_tasks:
                tasks_by_id[int(task_entry["task_id"])] = task_entry

        return tasks_by_id

    def save(self, tasks_by_id: dict[int, dict]) -> None:
        with open(self.path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self._HEADER)
            writer.writeheader()
            for task_entry in tasks_by_id.values():
                writer.writerow(task_entry)

class BulkRepository(ITaskRepository):
    def __init__(self, storage: IBulkStorage) -> None:
        self.storage = storage

    def _load(self) -> dict[int, dict]:
        return self.storage.load()

    def _save(self, tasks_by_id: dict[int, dict]) -> None:
        self.storage.save(tasks_by_id)

    def get_max_id(self) -> int:
        tasks_by_id = self.storage.load()
        return max(tasks_by_id.keys(), default=0)

    def add(self, new_data: TaskDTO) -> None:
        tasks_by_id = self._load()

        if new_data.task_id in tasks_by_id:
            raise TaskAlreadyExistsError(f"Task with id {new_data.task_id} already exists")

        tasks_by_id[new_data.task_id] = TaskMapper.to_dict(new_data)

        self._save(tasks_by_id)

    def update(self, updated_data: TaskDTO) -> None:
        tasks_by_id = self._load()

        if updated_data.task_id not in tasks_by_id:
            raise TaskNotFoundError(f"Task with id {updated_data.task_id} not found, cant update")

        tasks_by_id[updated_data.task_id] = TaskMapper.to_dict(updated_data)
        self._save(tasks_by_id)

    def delete(self, id_to_delete: int) -> None:
        tasks_by_id = self._load()

        if id_to_delete not in tasks_by_id:
            raise TaskNotFoundError(f"Task with id {id_to_delete} not found, cant delete")

        del tasks_by_id[id_to_delete]
        self._save(tasks_by_id)

    def read(self, id_to_read: int) -> TaskDTO:
        tasks_by_id = self._load()

        if id_to_read not in tasks_by_id:
            raise TaskNotFoundError(f"Task with id {id_to_read} not found, cant read")

        return TaskMapper.from_dict(tasks_by_id[id_to_read])

    def filter_by_status(self, status_filter: TaskStatus|None = None) -> list[TaskDTO]:
        tasks_by_id = self._load()

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
