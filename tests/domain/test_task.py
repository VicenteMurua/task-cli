# tests/domain/test_task.py
import time
import pytest
from datetime import datetime, timedelta
from task_cli.domain.task import Task, TaskStatus, time_zone
from task_cli.domain.exceptions import (
    TaskValidationError,
    IllegalTaskDescriptionError
)


@pytest.fixture
def task_params() -> dict:
    """Valores base para instanciar una Task en los tests."""
    return {
        "description": "Comprar pan",
        "task_id": 1,
        "status": TaskStatus.TODO,
        "created_at": None,
        "updated_at": None,
    }


@pytest.fixture
def new_task(task_params: dict) -> Task:
    """Crea una Task válida para pruebas de comportamiento."""
    return Task(**task_params)


class TestTaskInitialization:
    def test_basic_initialization(self, task_params):
        """Verifica que los datos se asignen correctamente al nacer."""
        task = Task(**task_params)
        assert task.task_id == 1
        assert task.description == "Comprar pan"
        assert task.status == TaskStatus.TODO
        # Al nacer sin fechas, created y updated deben ser idénticos
        assert task.created_at == task.updated_at

    def test_repr_contains_info(self, new_task):
        """Verifica que el __repr__ sea útil para el programador."""
        representation = repr(new_task)
        assert "Task" in representation
        assert "task_id=1" in representation
        assert "description='Comprar pan'" in representation


class TestAttributeProtection:
    """Verifica que la Task sea un objeto honesto (solo lectura)."""

    @pytest.mark.parametrize("attribute", [
        "description", "status", "task_id", "created_at", "updated_at"
    ])
    def test_properties_are_read_only(self, new_task, attribute):
        with pytest.raises(AttributeError):
            # Usamos setattr para que el IDE no marque error de tipado
            setattr(new_task, attribute, "Intento de cambio")


class TestTaskBusinessRules:
    """Pruebas de integridad de reglas de negocio."""

    def test_empty_description_raises_specific_error(self, task_params):
        task_params["description"] = "   "
        with pytest.raises(IllegalTaskDescriptionError):  # ← Corregido: antes era ValidationError
            Task(**task_params)

    def test_invalid_task_id(self, task_params):
        task_params["task_id"] = 0
        with pytest.raises(TaskValidationError):
            Task(**task_params)

    @pytest.mark.parametrize("created, updated", [
        (None, datetime.now(time_zone)),
        (datetime.now(time_zone), None)
    ])
    def test_dates_must_be_both_none_or_both_defined(self, task_params, created, updated):
        task_params["created_at"] = created
        task_params["updated_at"] = updated
        with pytest.raises(TaskValidationError):
            Task(**task_params)

    def test_created_at_cannot_be_after_updated_at(self, task_params):
        now = datetime.now(time_zone)
        past = now - timedelta(days=1)
        task_params["created_at"] = now
        task_params["updated_at"] = past
        with pytest.raises(TaskValidationError):
            Task(**task_params)


class TestTaskTypeSafety:
    """Pruebas de contrato técnico (Programador)."""

    def test_description_must_be_string(self, task_params):
        task_params["description"] = 123
        with pytest.raises(TypeError, match="Description must be a string"):
            Task(**task_params)

    def test_status_must_be_enum(self, task_params):
        task_params["status"] = "todo"  # Debe ser el objeto Enum, no el string
        with pytest.raises(TypeError, match="Status must be a TaskStatus"):
            Task(**task_params)


class TestTaskBehavior:
    """Pruebas de los métodos de mutación y decoradores."""

    def test_update_description_refreshes_timestamp(self, new_task):
        initial_update = new_task.updated_at
        time.sleep(0.01)  # Garantizamos que el reloj avance

        new_task.update_description("Nueva descripción")

        assert new_task.description == "Nueva descripción"
        assert new_task.updated_at > initial_update
        assert new_task.created_at == initial_update  # El pasado no cambia

    def test_update_status_refreshes_timestamp(self, new_task):
        initial_update = new_task.updated_at
        time.sleep(0.01)

        new_task.update_status(TaskStatus.DONE)

        assert new_task.status == TaskStatus.DONE
        assert new_task.updated_at > initial_update