from sys import exception
from typing import Dict

import pytest
from src.task_cli.domain.task import Task, TaskStatus


@pytest.fixture
def task_body() -> dict:
    body = {
        "description": "",
        "task_id": 1,
        "status": TaskStatus.DONE,
        "created_at": None,
        "updated_at": None,
    }
    return body

class TestTaskInitInitialization:
    assigned_id = 1
    assigned_description = "Nueva Tarea"
    @pytest.fixture
    def new_task(self) -> Task:
        """Crea una Task nueva para cada test"""
        return Task(
            description=self.assigned_description,
            task_id=self.assigned_id,
        )
    def test_task_id(self, new_task: Task) -> None:
        assert new_task.task_id == self.assigned_id

    def test_description(self, new_task: Task) -> None:
        assert new_task.description == self.assigned_description
        
    def test_status(self, new_task: Task) -> None:
        assert new_task.status == TaskStatus.DONE

    def test_time(selfself, new_task: Task) -> None:
        assert new_task.created_at == new_task.updated_at

class TestTaskRules:

    def test_has_no_description(self, task_body: Dict) -> None:
        task_body["description"] = ""
        with pytest.raises(ValueError) as exc:
            bad_task = Task(**task_body)
        assert  str(exc.value) == "Description cannot be empty"
    def test_has_space_description(self, task_body: Dict) -> None:
        task_body["description"] = ""
        with pytest.raises(ValueError):
            bad_task = Task(**task_body)
    def test_has_negative_id(self, task_body: Dict) -> None:
        task_body["task_id"] = -1
        with pytest.raises(ValueError):
            bad_task = Task(**task_body)