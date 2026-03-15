import pytest
from pathlib import Path

from task_cli.domain.dtos import TaskDTO
from task_cli.domain.exceptions import TaskAlreadyExistsError, TaskNotFoundError, NoTaskToList
from task_cli.domain.task import TaskStatus


from task_cli.repository.task_repository import (
    FileRepository,
    JSONStorage,
    CSVStorage,
    SQLiteRepository,
)

from tests.fakes.fake_dtos import TaskDataset


class TestTaskRepository:

    @pytest.fixture(params=["json", "csv", "sqlite"])
    def repo(self, request, tmp_path: Path):
        if request.param == "json":
            path = tmp_path / "tasks.json"
            return FileRepository(JSONStorage(path))
        if request.param == "csv":
            path = tmp_path / "tasks.csv"
            return FileRepository(CSVStorage(path))

        path = tmp_path / "tasks.db"
        return SQLiteRepository(path)

    @pytest.fixture
    def dataset(self):
        return (
            TaskDataset()
            .add("task 1", TaskStatus.TODO)
            .add("task 2", TaskStatus.TODO)
            .add("task 3", TaskStatus.IN_PROGRESS)
            .add("task 4", TaskStatus.DONE)
        )

    def test_add_1(self, repo):
        dataset = TaskDataset().add("task", TaskStatus.TODO)
        dto = dataset.all()[0]
        with repo as r:
            r.add(dto)
        with repo as r:
            result = r.read(dto.task_id)
        assert result == dto

    def test_add_n(self, repo, dataset):
        dataset.load_into(repo)
        with repo as r:
            result = r.filter_by_status(None)
        assert len(result) == dataset.count()

    def test_add_duplicate(self, repo):
        dto = TaskDataset().add("task", TaskStatus.TODO).all()[0]
        with repo as r:
            r.add(dto)
            with pytest.raises(TaskAlreadyExistsError):
                r.add(dto)

    def test_update(self, repo):
        dataset = TaskDataset().add("task", TaskStatus.TODO)
        dto = dataset.all()[0]
        with repo as r:
            r.add(dto)
        updated = TaskDataset().add(
            description="updated",
            status=TaskStatus.TODO,
            task_id=dto.task_id,
        ).all()[0]
        with repo as r:
            r.update(updated)
        with repo as r:
            result = r.read(dto.task_id)
        assert result.description == "updated"

    def test_update_bad_index(self, repo):
        dto = TaskDataset().add("task", TaskStatus.TODO).all()[0]
        with repo as r:
            with pytest.raises(TaskNotFoundError):
                r.update(dto)

    def test_delete(self, repo):
        dto = TaskDataset().add("task", TaskStatus.TODO).all()[0]
        with repo as r:
            r.add(dto)
            r.delete(dto.task_id)
        with repo as r:
            with pytest.raises(NoTaskToList):
                r.filter_by_status(None)

    def test_delete_bad_index(self, repo):
        with repo as r:
            with pytest.raises(TaskNotFoundError):
                r.delete(999)

    def test_read(self, repo):
        dto = TaskDataset().add("task", TaskStatus.TODO).all()[0]
        with repo as r:
            r.add(dto)
        with repo as r:
            result = r.read(dto.task_id)
        assert result == dto

    def test_read_bad_index_parametrized(self, repo):
        """Cubre raise TaskNotFoundError (línea 187)"""
        ids = [999, 12345, -1]
        with repo as r:
            for id_to_read in ids:
                with pytest.raises(TaskNotFoundError):
                    r.read(id_to_read)

    @pytest.mark.parametrize("status_filter", [TaskStatus.TODO, TaskStatus.DONE, TaskStatus.IN_PROGRESS])
    def test_filter_by_status_parametrized(self, repo, dataset, status_filter):
        """Cubre la lista por comprensión de filter_by_status (línea 205)"""
        dataset.load_into(repo)
        with repo as r:
            tasks = r.filter_by_status(status_filter)
            assert all(t.status == status_filter.value for t in tasks)

    def test_task_class_last_lines(self):
        """Cubre última línea de Task (línea 213) usando métodos existentes"""
        from task_cli.domain.task import Task, TaskStatus

        # Instanciamos un task válido
        task = Task(description="dummy", task_id=1, status=TaskStatus.TODO)

        # Llamamos a update_status para cubrir update_timestamp y _refresh_updated_at
        task.update_status(TaskStatus.DONE)
        assert task.status == TaskStatus.DONE

        # Llamamos a update_description para cubrir también la otra función decorada
        task.update_description("new description")
        assert task.description == "new description"

    # --- Resto de los tests existentes ---
    def test_filter_by_status_none(self, repo, dataset):
        dataset.load_into(repo)
        with repo as r:
            result = r.filter_by_status(None)
        assert len(result) == dataset.count()

    def test_filter_by_wrong_status(self, repo):
        with repo as r:
            with pytest.raises(TypeError):
                r.filter_by_status("zapallo") # type: ignore

    def test_persistence_between_sessions(self, repo):
        dto = TaskDataset().add("persistent", TaskStatus.TODO).all()[0]
        with repo as r:
            r.add(dto)
        with repo as r:
            result = r.read(dto.task_id)
        assert result == dto

    def test_get_max_id(self, repo):
        dataset = (
            TaskDataset()
            .add("a", TaskStatus.TODO)
            .add("b", TaskStatus.TODO)
            .add("c", TaskStatus.DONE)
        )
        dataset.load_into(repo)
        with repo as r:
            max_id = r.get_max_id()
        assert max_id == dataset.count()

    def test_get_max_id_empty(self, repo):
        with repo as r:
            result = r.get_max_id()
        assert result == 0

    def test_delete_only_removes_target(self, repo, dataset):
        dataset.load_into(repo)
        with repo as r:
            r.delete(1)
        with repo as r:
            result = r.filter_by_status(None)
        assert len(result) == dataset.count() - 1
        assert all(task.task_id != 1 for task in result)

    def test_update_does_not_change_id(self, repo):
        dto = TaskDataset().add("task", TaskStatus.TODO).all()[0]
        with repo as r:
            r.add(dto)
        updated = TaskDataset().add(
            "new",
            TaskStatus.TODO,
            task_id=dto.task_id,
        ).all()[0]
        with repo as r:
            r.update(updated)
        with repo as r:
            result = r.read(dto.task_id)
        assert result.task_id == dto.task_id

    def test_repository_requires_context_manager(self, repo):
        dto = TaskDataset().add("task", TaskStatus.TODO).all()[0]
        with pytest.raises(RuntimeError):
            repo.add(dto)

    def test_empty_repository(self, repo):
        with repo as r:
            with pytest.raises(NoTaskToList):
                r.filter_by_status(None)

    def test_filter_returns_correct_objects(self, repo, dataset):
        dataset.load_into(repo)
        with repo as r:
            todos = r.filter_by_status(TaskStatus.TODO)
        assert all(t.status == TaskStatus.TODO.value for t in todos)

    def test_filter_empty_repo(self, repo):
        with repo as r:
            with pytest.raises(NoTaskToList):
                r.filter_by_status(TaskStatus.TODO)

    def test_add_after_delete_reuses_correct_state(self, repo):
        dataset = TaskDataset().add("task", TaskStatus.TODO)
        dto = dataset.all()[0]
        with repo as r:
            r.add(dto)
            r.delete(dto.task_id)
        new = TaskDataset().add("new task", TaskStatus.DONE).all()[0]
        with repo as r:
            r.add(new)
        with repo as r:
            result = r.filter_by_status(None)
        assert len(result) == 1

    def test_multiple_sessions_persistence(self, repo):
        dataset = (
            TaskDataset()
            .add("a", TaskStatus.TODO)
            .add("b", TaskStatus.DONE)
        )
        dataset.load_into(repo)
        with repo as r:
            tasks = r.filter_by_status(None)
        assert len(tasks) == 2

    def test_repositories_rollback_on_exception(self, repo):
        """
        Este test fuerza un error dentro del 'with' para ejecutar:
        1. El rollback en SQLiteRepository.
        2. El bloque 'if exc_type' (el que no guarda) en FileRepository.
        """

        # 1. Preparamos un DTO para intentar insertarlo
        dto = TaskDTO(
            task_id=999,
            description="test rollback",
            status="todo",
            created_at="2023-01-01",
            updated_at="2023-01-01"
        )

        # 2. Abrimos el repo y PROVOCAMOS un error manual (RuntimeError)
        # Esto hará que entre al 'if exc_type:' de los métodos __exit__
        with pytest.raises(RuntimeError):
            with repo as r:
                r.add(dto)
                # Justo después de añadirlo, rompemos la ejecución
                # En SQLite esto debería disparar el rollback()
                # En FileRepository esto debería hacer que NO se llame a save()
                raise RuntimeError("Error forzado para ver rollback")

                # 3. Verificamos que los cambios NO se aplicaron
        # Si el rollback/no-save funcionó, el ID 999 no debe existir
        with repo as r:
            with pytest.raises(TaskNotFoundError):
                r.read(999)