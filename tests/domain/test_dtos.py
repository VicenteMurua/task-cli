# tests/domain/test_dtos.py
import pytest
from dataclasses import FrozenInstanceError
from task_cli.domain.dtos import TaskDTO


class TestTaskDTOContract:
    def test_dto_is_immutable(self):
        """Verifica que el contrato diplomático (inmutabilidad) se respete."""
        dto = TaskDTO(
            task_id=1,
            description="Test",
            status="todo",
            created_at="now",
            updated_at="now"
        )

        # Intentar modificar cualquier campo debe lanzar FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            dto.description = "Cambiado por accidente"


    def test_dto_identity(self):
        """Verifica que dos DTO con los mismos datos sean considerados iguales."""
        # Esto es un regalo de las dataclasses que queremos asegurar

        params = {
            "task_id": 1,
            "description": "Test",
            "status": "todo",
            "created_at": "2024-01-01",
            "updated_at": "2024-01-01"
        }
        dto1 = TaskDTO(**params)
        dto2 = TaskDTO(**params)

        assert dto1 == dto2