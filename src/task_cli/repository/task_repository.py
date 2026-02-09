from abc import ABC, abstractmethod
from pathlib import Path
from task_cli.domain.task import Task, TaskStatus
from datetime import datetime
import json

class ITaskRepository(ABC):

    @abstractmethod
    def load(self) -> list[tuple[str, str, int, datetime, datetime]]:
        pass

    @abstractmethod
    def save(self, task_list: list[Task]) -> None:
        pass

class JSONTaskRepository(ITaskRepository):
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def load(self) -> list[tuple[str, TaskStatus, int, datetime, datetime]]:

        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")
        task_data_list: list[tuple[str, TaskStatus, int, datetime, datetime]] = []
        with open(self.path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
            for task_entry in raw_data:
                description: str = task_entry['description']
                status: TaskStatus = TaskStatus(task_entry['status'])
                task_id: int = int(task_entry['id'])
                created_at: datetime = datetime.fromisoformat(task_entry['created_at'])
                updated_at: datetime = datetime.fromisoformat(task_entry['updated_at'])
                task_tuple = description, status, task_id, created_at, updated_at
                task_data_list.append(task_tuple)
        return  task_data_list

    def save(self, task_list: list[Task]) -> None:
        serialized_task = []
        for task in task_list:
            serialized_task.append(task.to_dict())

        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(serialized_task, file, ensure_ascii=False, indent=4)
