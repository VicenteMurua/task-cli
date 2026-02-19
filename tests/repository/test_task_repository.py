import json
from pathlib import Path
from task_cli.domain.exceptions import TaskAlreadyExistsError, TaskNotFoundError
from task_cli.repository.mappers import TaskMapper
from task_cli.repository.task_repository import JSONTaskRepository
from task_cli.domain.dtos import TaskDTO
from task_cli.domain.task import TaskStatus
import pytest
from tests.fakes.fake_dtos import fake_dto_list_no_duplicates, fake_todo_1_dto, fake_todo_2_dto, modified_dto_1_dto, fake_done_1_dto, fake_in_progress_1_dto


class TestJSONTaskRepository:
    @pytest.fixture()
    def json_path(self, tmp_path: Path) -> Path:
        return tmp_path / "test_add.json"

    @pytest.fixture
    def repo(self, json_path: Path) -> JSONTaskRepository:
        return JSONTaskRepository(json_path)

    @pytest.mark.parametrize(
        "task_dto",
        fake_dto_list_no_duplicates
    )
    def test_add_1(self, task_dto: TaskDTO, json_path: Path, repo: JSONTaskRepository):
        repo.add(task_dto)
        task_dict: dict = TaskMapper.to_dict(task_dto)
        with open(json_path, 'r', encoding='utf-8') as file:
            data_list: list[dict] = json.load(file)
            assert 1 == len(data_list)
            assert  task_dict in data_list

    def test_add_n(self, json_path: Path, repo: JSONTaskRepository):
        for task_dto in fake_dto_list_no_duplicates:
            repo.add(task_dto)

        with open(json_path, 'r', encoding='utf-8') as file:
            data_list: list[dict] = json.load(file)
            assert len(fake_dto_list_no_duplicates) == len(data_list)
            assert all(TaskMapper.to_dict(task_dto) in data_list for task_dto in fake_dto_list_no_duplicates)

    def test_add_duplicate(self, repo: JSONTaskRepository):
        repo.add(fake_todo_1_dto)
        with pytest.raises(TaskAlreadyExistsError):
            repo.add(fake_todo_1_dto)


    def test_update(self, json_path: Path, repo: JSONTaskRepository):
        repo.add(fake_todo_1_dto)
        repo.update(modified_dto_1_dto)
        with open(json_path, 'r', encoding='utf-8') as file:
            data_list: list[dict] = json.load(file)
            assert 1 == len(data_list)
            assert data_list[0] == TaskMapper.to_dict(modified_dto_1_dto)

    def test_update_bad_index(self, repo: JSONTaskRepository):
        with pytest.raises(TaskNotFoundError):
            repo.update(fake_todo_1_dto)


    def test_delete(self, json_path: Path, repo: JSONTaskRepository):
        repo.add(fake_todo_1_dto)
        repo.delete(fake_todo_1_dto.task_id)
        with open(json_path, 'r', encoding='utf-8') as file:
            data_list: list[dict] = json.load(file)
            assert not len(data_list)

    def test_delete_bad_index(self, repo: JSONTaskRepository):
        with pytest.raises(TaskNotFoundError):
            repo.delete(fake_todo_1_dto)


    def test_read(self, json_path: Path, repo: JSONTaskRepository):
        repo.add(fake_todo_1_dto)
        assert fake_todo_1_dto == repo.read(fake_todo_1_dto.task_id)

    def test_read_bad_index(self, repo: JSONTaskRepository):
        with pytest.raises(TaskNotFoundError):
            repo.read(fake_todo_1_dto.task_id)


    def test_filter_by_status_none(self, repo: JSONTaskRepository):
        for data in fake_dto_list_no_duplicates:
            repo.add(data)
        result = repo.filter_by_status(None)
        assert len(fake_dto_list_no_duplicates) == len(result)
        assert result == fake_dto_list_no_duplicates

    @pytest.mark.parametrize(
        "status, output",
        [
            (TaskStatus.TODO, [fake_todo_1_dto, fake_todo_2_dto]),
            (TaskStatus.DONE, [fake_done_1_dto]),
            (TaskStatus.IN_PROGRESS, [fake_in_progress_1_dto]),
        ]
    )
    def test_filter_by_status(self, repo: JSONTaskRepository, status: TaskStatus, output: list[TaskDTO]):
        for data in fake_dto_list_no_duplicates:
            repo.add(data)
        assert output == repo.filter_by_status(status)

    def test_filter_by_wrong_status(self, repo: JSONTaskRepository):
        with pytest.raises(ValueError):
            repo.filter_by_status("zapallo") #type: ignore[arg-type]

# TODO: Tests de robustez / condiciones adversas
# - Qué pasa si el archivo JSON está corrupto o vacío
# - Qué pasa si se pasan IDs inválidos (negativos, strings)
# - Validación de concurrencia (si se agregan/actualizan tareas simultáneamente)
# - Manejo de errores de I/O (permiso denegado, disco lleno, etc.)
