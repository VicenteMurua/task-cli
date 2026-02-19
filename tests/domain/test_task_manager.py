import pytest

from fakes.fake_descriptions import fake_desc_list
from task_cli.domain.task import TaskStatus
from tests.fakes.fake_repository import  FakeRepo
from task_cli.domain.task_manager import TaskManager
from tests.fakes.fake_descriptions import fake_desc_1, fake_desc_2

@pytest.fixture
def fake_repo() -> FakeRepo:
    return FakeRepo()

@pytest.fixture
def manager(fake_repo: FakeRepo) -> TaskManager:
    return TaskManager(fake_repo)

class TestRepository:

    def test_add_1(self, manager: TaskManager) -> None:
        manager.add(fake_desc_1)
        repo_storage = manager._repository.filter_by_status(None)
        assert len(repo_storage) == 1
        assert repo_storage[0].description == fake_desc_1

    def test_add_n(self, manager: TaskManager) -> None:
        todo_list: list[str] = fake_desc_list
        for description in todo_list:
            manager.add(description)
        repo_storage = manager._repository.filter_by_status(None)

        assert len(repo_storage) == len(todo_list)

        for dto, expected in zip(repo_storage, todo_list):
            assert dto.description == expected


    def test_update_1(self, manager: TaskManager) -> None:
        manager.add(fake_desc_1)
        task_1 = manager._repository.read(1)
        manager.update(task_1.task_id, fake_desc_2)

        task_1 = manager._repository.read(task_1.task_id)
        repo_storage = manager._repository.filter_by_status(None)

        assert len(repo_storage) == 1
        assert task_1.description == fake_desc_2

    def test_delete_1(self, manager: TaskManager) -> None:
        manager.add(fake_desc_1)
        task = manager._repository.read(1)
        manager.delete(task.task_id)

        repo_storage = manager._repository.filter_by_status(None)

        assert not len(repo_storage)

    @pytest.mark.parametrize(
        "status",
        [status.value for status in TaskStatus]
    )
    def test_mark(self, manager: TaskManager, status) -> None:
        manager.add(fake_desc_1)
        task_1 = manager._repository.read(1)

        manager.mark(status, task_1.task_id)

        task_1 = manager._repository.read(task_1.task_id)
        repo_storage = manager._repository.filter_by_status(None)
        assert len(repo_storage) == 1
        assert TaskStatus(task_1.status) == TaskStatus(status)

    def test_filter_tasks(self, manager: TaskManager) -> None:
        for description in fake_desc_list:
            manager.add(description)

        manager.mark("in-progress", 1)
        manager.mark("done", 2)
        manager.mark("done", 3)
        manager.mark("todo", 3)

        assert manager.filter_tasks("done")[0] == manager._repository.read(2)
        assert manager.filter_tasks("in-progress")[0] == manager._repository.read(1)
        assert manager.filter_tasks("todo")[0] == manager._repository.read(3)