from abc import ABC, abstractmethod
from pathlib import Path
from task_cli.domain.dtos import TaskDTO
from task_cli.repository.mappers import TaskMapper

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
                task_dto: TaskDTO = TaskMapper.from_dict(task_entry)
                task_dto_list.append(task_dto)
        return  task_dto_list

    def save(self, task_dto_list: list[TaskDTO]) -> None:
        serialized_task: list[dict] = []
        for task_dto in task_dto_list:
            serialized_task.append(TaskMapper.to_dict(task_dto))

        with open(self.path, 'w', encoding='utf-8') as file:
            json.dump(serialized_task, file, ensure_ascii=False, indent=4)