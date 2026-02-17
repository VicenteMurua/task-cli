from abc import ABC, abstractmethod
from pathlib import Path
from task_cli.domain.dtos import TaskDTO
from task_cli.domain.task import TaskStatus
from task_cli.repository.mappers import TaskMapper

import json

class ITaskRepository(ABC):

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
    def filter_by_status(self, status: TaskStatus) -> list[TaskDTO]:
        pass

class JSONTaskRepository(ITaskRepository):
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def _ensure_file(self) -> None:
        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")

    def _load_raw_data(self) -> dict[int, dict]:
        self._ensure_file()
        raw_task_by_id = {}
        with open(self.path, 'r', encoding='utf-8') as file:
            task_array = json.load(file)
            for task_entry in task_array:
                raw_task_by_id[int(task_entry["task_id"])] = task_entry
            return raw_task_by_id

    def _save_raw_data(self, task_by_id: dict[int, dict]) -> None:
        task_json_format: list[dict] = list(task_by_id.values())
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(task_json_format, file, ensure_ascii=False, indent=4)

    def add(self, new_data: TaskDTO) -> None:
        pass

    def update(self, updated_data: TaskDTO) -> None:
        pass

    def delete(self, id_to_delete: int) -> None:
        pass

    def read(self, id_to_read: int) -> TaskDTO:
        pass

    def filter_by_status(self, status: TaskStatus) -> list[TaskDTO]:
        pass