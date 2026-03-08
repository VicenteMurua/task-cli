import pytest

from task_cli.domain.exceptions import TaskNotFoundError
from task_cli.domain.task import TaskStatus
from task_cli.domain.task_manager import TaskManager
from tests.fakes.fake_repository import FakeRepo
from tests.fakes.fake_descriptions import fake_desc_1, fake_desc_2, fake_desc_list


@pytest.fixture
def fake_repo() -> FakeRepo:
    return FakeRepo()


@pytest.fixture
def manager(fake_repo: FakeRepo) -> TaskManager:
    return TaskManager(fake_repo)


class TestTaskManager:

    def test_add_1(self, manager: TaskManager):

        manager.add(fake_desc_1)

        with manager._repository as repo:
            tasks = repo.filter_by_status(None)

        assert len(tasks) == 1
        assert tasks[0].description == fake_desc_1


    def test_add_n(self, manager: TaskManager):

        for desc in fake_desc_list:
            manager.add(desc)

        with manager._repository as repo:
            tasks = repo.filter_by_status(None)

        assert len(tasks) == len(fake_desc_list)

        descriptions = {t.description for t in tasks}
        assert descriptions == set(fake_desc_list)


    def test_update(self, manager: TaskManager):

        dto = manager.add(fake_desc_1)

        manager.update(dto.task_id, fake_desc_2)

        with manager._repository as repo:
            updated = repo.read(dto.task_id)

        assert updated.description == fake_desc_2


    def test_delete(self, manager: TaskManager):

        dto = manager.add(fake_desc_1)

        manager.delete(dto.task_id)

        with manager._repository as repo:
            tasks = repo.filter_by_status(None)

        assert len(tasks) == 0


    @pytest.mark.parametrize(
        "status",
        [status for status in TaskStatus]
    )
    def test_mark(self, manager: TaskManager, status):

        dto = manager.add(fake_desc_1)

        manager.mark(status, dto.task_id)

        with manager._repository as repo:
            task = repo.read(dto.task_id)

        assert task.status == status.value


    def test_filter_tasks(self, manager: TaskManager):

        for desc in fake_desc_list:
            manager.add(desc)

        manager.mark(TaskStatus.IN_PROGRESS, 1)
        manager.mark(TaskStatus.DONE, 2)
        manager.mark(TaskStatus.DONE, 3)
        manager.mark(TaskStatus.TODO, 3)

        done_tasks = manager.filter_by_status(TaskStatus.DONE)
        in_progress_tasks = manager.filter_by_status(TaskStatus.IN_PROGRESS)
        todo_tasks = manager.filter_by_status(TaskStatus.TODO)

        assert {t.task_id for t in done_tasks} == {2}
        assert {t.task_id for t in in_progress_tasks} == {1}
        assert {t.task_id for t in todo_tasks} == {3}


    def test_read_existing_task(self, manager: TaskManager):

        dto = manager.add("test task")

        result = manager.read(dto.task_id)

        assert result.task_id == dto.task_id
        assert result.description == "test task"


    def test_ids_are_incremental(self, manager: TaskManager):

        t1 = manager.add("a")
        t2 = manager.add("b")
        t3 = manager.add("c")

        assert t1.task_id == 1
        assert t2.task_id == 2
        assert t3.task_id == 3


    def test_update_does_not_change_status(self, manager: TaskManager):

        dto = manager.add("task")

        manager.mark(TaskStatus.DONE, dto.task_id)

        manager.update(dto.task_id, "new description")

        with manager._repository as repo:
            task = repo.read(dto.task_id)

        assert task.status == TaskStatus.DONE.value


    def test_read_not_found(self, manager: TaskManager):

        with pytest.raises(TaskNotFoundError):
            manager.read(999)


    def test_delete_not_found(self, manager: TaskManager):

        with pytest.raises(TaskNotFoundError):
            manager.delete(999)


    def test_update_not_found(self, manager: TaskManager):

        with pytest.raises(TaskNotFoundError):
            manager.update(999, "something")


    def test_mark_not_found(self, manager: TaskManager):

        with pytest.raises(TaskNotFoundError):
            manager.mark(TaskStatus.DONE, 999)


    def test_mark_invalid_status(self, manager: TaskManager):

        dto = manager.add("task")

        with pytest.raises(AttributeError):
            manager.mark(TaskStatus.invalid_status, dto.task_id)

    def test_filter_by_status_none_returns_all(self, manager: TaskManager):
        # Agregamos varias tareas
        dto1 = manager.add("task 1")
        dto2 = manager.add("task 2")
        dto3 = manager.add("task 3")

        # Llamamos filter_by_status con None
        tasks = manager.filter_by_status(None)

        # Debe devolver todas las tareas
        assert len(tasks) == 3
        descriptions = {t.description for t in tasks}
        assert descriptions == {"task 1", "task 2", "task 3"}