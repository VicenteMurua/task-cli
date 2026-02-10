from abc import ABC, abstractmethod
from pathlib import Path
from task_cli.domain.task import  TaskStatus, TaskDTO
from datetime import datetime
from dataclasses import asdict
import json

class ITaskRepository(ABC):

    @abstractmethod
    def load(self) -> list[TaskDTO]:
        pass

    @abstractmethod
    def save(self, task_list: list[TaskDTO]) -> None:
        pass

class JSONTaskRepository(ITaskRepository):
    def __init__(self, path: Path) -> None:
        self.path: Path = path

    def load(self) -> list[TaskDTO]:

        if not self.path.exists():
            self.path.write_text("[]", encoding="utf-8")
        task_dto_list: list[TaskDTO] = []
        with open(self.path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)
            for task_entry in raw_data:
                description: str = task_entry['description']
                status: TaskStatus = TaskStatus(task_entry['status'])
                task_id: int = int(task_entry['id'])
                created_at: datetime = datetime.fromisoformat(task_entry['created_at'])
                updated_at: datetime = datetime.fromisoformat(task_entry['updated_at'])
                task_dto = TaskDTO(
                    description=description,
                    status=status,
                    task_id=task_id,
                    created_at=created_at,
                    updated_at=updated_at
                )
                task_dto_list.append(task_dto)
        return  task_dto_list

    def save(self, task_list: list[TaskDTO]) -> None:
        serialized_task:list[TaskDTO] = []
        for task in task_list:
            serialized_task.append(asdict(task))

        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(serialized_task, file, ensure_ascii=False, indent=4)
    def _from_dto_to_json(self, task_dto: TaskDTO) -> dict:
        pass