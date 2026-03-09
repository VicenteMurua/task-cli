# tests/ui/test_command_interface.py
import pytest
from unittest.mock import patch

from task_cli.domain.task import TaskStatus
from task_cli.ui.command_interface import CommandInterface
from task_cli.domain.task_manager import TaskManager
from tests.fakes.fake_repository import FakeRepo
from tests.fakes.fake_dtos import TaskDataset


@pytest.fixture
def cli_es():
    """Instancia la CLI en español con un repo en memoria."""
    return CommandInterface(TaskManager(FakeRepo()), lang="es")


@pytest.fixture
def cli_en():
    """Instancia la CLI en inglés para probar localización."""
    return CommandInterface(TaskManager(FakeRepo()), lang="en")


class TestCLIIntegration:
    """
    Tests de integración de la 'Carrocería'.
    Verifican que los cables entre la terminal y el manager estén bien conectados.
    """

    def test_add_command_flow(self, cli_es, capsys):
        """Verifica que el comando 'añadir' llega hasta el repo."""
        test_args = ["task-cli", "añadir", "Nueva tarea de prueba"]
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        assert "Nueva tarea de prueba" in captured.out
        assert "Añadiste esta tarea nueva" in captured.out

    def test_error_handling_not_found(self, cli_es, capsys):
        """Verifica que un ID inexistente muestra el error rojo y no un crash."""
        test_args = ["task-cli", "eliminar", "999"]
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        # Buscamos el mensaje del catálogo de errores en español
        assert "No se encontró la tarea con ID 999" in captured.out
        assert "[✖]" in captured.out  # Prefijo de tu formateador de errores

    def test_validation_error_empty_desc(self, cli_es, capsys):
        """Verifica que la regla de 'descripción no vacía' sube hasta la UI."""
        test_args = ["task-cli", "añadir", "   "]
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        assert "La descripción no es válida" in captured.out

    def test_list_filter_behavior(self, cli_es, capsys):
        """Verifica que el filtro 'hecha' funciona en la CLI."""
        # 1. Preparamos datos: una pendiente y una hecha
        repo = cli_es._manager._repository
        with repo:
            TaskDataset().add("Tarea 1", status=TaskStatus.TODO).add("Tarea 2", status=TaskStatus.DONE).load_into(repo)

        # 2. Ejecutamos listar filtrado
        test_args = ["task-cli", "listar", "done"]
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        assert "Tarea 2" in captured.out
        assert "Tarea 1" not in captured.out

    def test_localization_en_switch(self, cli_en, capsys):
        """Verifica que si la CLI está en inglés, reconoce 'add' y no 'añadir'."""
        test_args = ["task-cli", "add", "English Task"]
        with patch("sys.argv", test_args):
            cli_en.run()

        captured = capsys.readouterr()
        assert "You added this new task" in captured.out