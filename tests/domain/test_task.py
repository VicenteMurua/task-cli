import time
import pytest
from task_cli.domain.task import Task, TaskStatus, time_zone
from datetime import datetime, timedelta
from task_cli.domain.exceptions import TaskValidationError

@pytest.fixture
def task_body() -> dict:
    body = {
        "description": "Comprar pan",
        "task_id": 1,
        "status": TaskStatus.TODO,
        "created_at": None,
        "updated_at": None,
    }
    return body

@pytest.fixture
def new_task(task_body: dict) -> Task:
    return Task(**task_body)

@pytest.fixture
def time_now() -> datetime:
    return datetime.now(time_zone)

class TestTaskInitInitialization:
    assigned_id = 1
    assigned_description = "Nueva Tarea"

    @pytest.fixture
    def new_task(self) -> Task:
        """Crea una Task nueva para cada test"""
        return Task(
            description=self.assigned_description,
            task_id=self.assigned_id,
            status=TaskStatus.TODO,
        )

    def test_task_id(self, new_task: Task) -> None:
        assert new_task.task_id == self.assigned_id

    def test_description(self, new_task: Task) -> None:
        assert new_task.description == self.assigned_description
        
    def test_status(self, new_task: Task) -> None:
        assert new_task.status == TaskStatus.TODO

    def test_time(self, new_task: Task) -> None:
        assert new_task.created_at == new_task.updated_at


class TestAttributeProtection:

    def test_description(self, new_task: Task) -> None:
        with pytest.raises(AttributeError):
            # noinspection PyPropertyAccess
            new_task.description = "hello"

    def test_status(self, new_task: Task) -> None:
        with pytest.raises(AttributeError):
            # noinspection PyPropertyAccess
            new_task.status = TaskStatus.IN_PROGRESS

    def test_task_id(self, new_task: Task) -> None:
        with pytest.raises(AttributeError):
            # noinspection PyPropertyAccess
            new_task.task_id = 5

    def test_created_at(self, new_task: Task, time_now) -> None:
        with pytest.raises(AttributeError):
            # noinspection PyPropertyAccess
            new_task.created_at = time_now

    def test_updated_at(self, new_task: Task, time_now) -> None:
        with pytest.raises(AttributeError):
            # noinspection PyPropertyAccess
            new_task.updated_at = time_now


class TestTaskRules:


    def test_has_no_description(self, task_body: dict) -> None:
        task_body["description"] = ""
        with pytest.raises(TaskValidationError) as exc:
            Task(**task_body)
        assert str(exc.value) == "Description cannot be empty"

    def test_has_space_description(self, task_body: dict) -> None:
        task_body["description"] = "   "
        with pytest.raises(TaskValidationError) as exc:
            Task(**task_body)
        assert str(exc.value) == "Description cannot be empty"


    def test_has_negative_id(self, task_body: dict) -> None:
        task_body["task_id"] = -1
        with pytest.raises(TaskValidationError) as exc:
            Task(**task_body)
        assert str(exc.value) == "Task ID must be greater than 0"

    @pytest.mark.parametrize(
        "new_created_at, new_updated_at",
        [
            (None, "time_now"),
            ("time_now", None)
        ]
    )
    def test_dates_xor(self, task_body:dict, new_created_at, new_updated_at, time_now) -> None:
        task_body["created_at"] = time_now if new_created_at == "time_now" else new_created_at
        task_body["updated_at"] = time_now if new_updated_at == "time_now" else new_updated_at
        with pytest.raises(TaskValidationError) as exc:
            Task(**task_body)
        assert str(exc.value) == "CreatedAt and updatedAt must both be None or defined at the same time"

    def test_date_not_greater(self, task_body: dict, time_now) -> None:
        tomorrow = time_now + timedelta(days=1)
        task_body["created_at"] = tomorrow
        task_body["updated_at"] = time_now
        with pytest.raises(TaskValidationError) as exc:
            Task(**task_body)
        assert str(exc.value) == "CreatedAt must not be greater than UpdatedAt"


class TestTaskTypeValidations:

    @pytest.mark.parametrize(
        "description",
        [
            None,
            2,
            True,
        ]
    )
    def test_description(self, task_body: dict, description) -> None:
        task_body["description"] = description
        with pytest.raises(TypeError) as exc:
            Task(**task_body)
        assert str(exc.value) == "Description must be a string"


    @pytest.mark.parametrize(
        "new_id",
        [
            None,
            "asd",
            True,
        ]
    )
    def test_task_id(self, task_body: dict, new_id) -> None:
        task_body["task_id"] = new_id
        with pytest.raises(TypeError) as exc:
            Task(**task_body)
        assert str(exc.value) == "ID must be a integer"


    @pytest.mark.parametrize(
        "new_status",
        [
            None,
            "asd",
            True,
            12,
        ]
    )
    def test_status(self, task_body, new_status) -> None:
        task_body["status"] = new_status
        with pytest.raises(TypeError) as exc:
            Task(**task_body)
        assert str(exc.value) == "Status must be a TaskStatus"
    @pytest.mark.parametrize(
        "new_created_at",
        [
            "asdf",
            True,
            123,
        ]
    )


    def test_created_at(self, new_created_at, task_body: dict) -> None:
        task_body["created_at"] = new_created_at
        with pytest.raises(TypeError) as exc:
            Task(**task_body)
        assert str(exc.value) == "CreatedAt must be a datetime or None"

    @pytest.mark.parametrize(
        "new_updated_at",
        [
            "asdf",
            True,
            123,
        ]
    )
    def test_updated_at(self, new_updated_at, task_body: dict) -> None:
        task_body["updated_at"] = new_updated_at
        with pytest.raises(TypeError) as exc:
            Task(**task_body)
        assert str(exc.value) == "UpdatedAt must be a datetime or None"


class TestTaskUpdate:
    @pytest.mark.parametrize(
        "new_description",
        [
            "Comprar pan",
            "Jugar un juego",
            "Programar",
        ]
    )
    def test_description(self, new_task: Task, new_description) -> None:
        # permite que pase tiempo suficiente para que la actualización y creación no ocurran muy rapido
        time.sleep(0.01)
        new_task.update_description(new_description)
        assert new_task.description == new_description
        assert new_task.updated_at > new_task.created_at

    @pytest.mark.parametrize(
        "new_status",
        [
            TaskStatus.TODO,
            TaskStatus.DONE,
            TaskStatus.IN_PROGRESS,
        ]
    )
    def test_status(self, new_task: Task, new_status) -> None:
        # permite que pase tiempo suficiente para que la actualización y creación no ocurran muy rapido
        time.sleep(0.01)
        new_task.update_status(new_status)
        assert new_task.status == new_status
        assert new_task.updated_at > new_task.created_at