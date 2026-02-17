from abc import ABC, abstractmethod
from pathlib import Path
from task_cli.domain.dtos import TaskDTO
from task_cli.domain.exceptions import TaskNotFoundError
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
        self._ensure_file()
        task_json_format: list[dict] = list(task_by_id.values())
        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(task_json_format, file, ensure_ascii=False, indent=4)

    def add(self, new_data: TaskDTO) -> None:
        information = self._load_raw_data()
        information[TaskDTO.task_id] = TaskMapper.to_dict(new_data)
        self._save_raw_data(information)

    def update(self, updated_data: TaskDTO) -> None:
        information = self._load_raw_data()
        if updated_data.task_id not in information:
            raise TaskNotFoundError(f"Task with id {updated_data.task_id} not found, cant update")
        information[TaskDTO.task_id] = TaskMapper.to_dict(updated_data)
        self._save_raw_data(information)

    def delete(self, id_to_delete: int) -> None:
        information = self._load_raw_data()
        if id_to_delete not in information:
            raise TaskNotFoundError(f"Task with id {id_to_delete} not found, cant delete")
        del information[TaskDTO.task_id]
        self._save_raw_data(information)

    def read(self, id_to_read: int) -> TaskDTO:
        information = self._load_raw_data()
        if id_to_read not in information:
            raise TaskNotFoundError(f"Task with id {id_to_read} not found, cant read")
        return TaskMapper.from_dict(information[id_to_read])

    def filter_by_status(self, status_filter: TaskStatus) -> list[TaskDTO]:
        information = self._load_raw_data()
        filtered_tasks: list[TaskDTO] = []
        if status_filter is None:
            return [TaskMapper.from_dict(task) for task in information.values()]
        for task in information.values():
            if task["status"] == TaskStatus(status_filter).value:
                filtered_tasks.append(TaskMapper.from_dict(task))
        return filtered_tasks