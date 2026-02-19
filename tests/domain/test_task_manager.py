import pytest
from tests.fakes.fake_repository import  FakeTaskRepository
from task_cli.domain.task_manager import TaskManager


@pytest.fixture
def fake_repo() -> FakeTaskRepository:
    return FakeTaskRepository()

@pytest.fixture
def manager(fake_repo: FakeTaskRepository) -> TaskManager:
    return TaskManager(fake_repo)

class TestRepository:

