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

    def test_read_simple(self, cli_es, capsys):
        """Cubre la rama 'else' del comando leer (vista compacta)."""
        repo = cli_es._manager._repository
        with repo:
            repo.add(TaskDataset().add("Leer esta", TaskStatus.TODO, task_id=10).all()[0])

        test_args = ["task-cli", "leer", "10"]  # Sin el flag -d
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        assert "10" in captured.out
        # Aquí verificamos que se llamó a Msgs.LIST (feedback rápido)
        assert "Listaste" in captured.out or "Interactuaste" in captured.out

    def test_read_detailed(self, cli_es, capsys):
        """Cubre la rama 'if args.detail' del comando leer."""
        repo = cli_es._manager._repository
        with repo:
            repo.add(TaskDataset().add("Detalle", TaskStatus.TODO, task_id=11).all()[0])

        test_args = ["task-cli", "leer", "11", "--detail"]
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        assert "Created:" in captured.out  # La vista detallada tiene fechas

    def test_mark_done_integration(self, cli_es, capsys):
        """Verifica el comando marcar-hecha."""
        repo = cli_es._manager._repository
        with repo:
            repo.add(TaskDataset().add("A medio hacer", TaskStatus.TODO, task_id=20).all()[0])

        test_args = ["task-cli", "marcar-hecha", "20"]
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        assert "Marcaste esta tarea" in captured.out
        # Verificamos que el icono cambió a hecho
        assert "✓" in captured.out or "done" in captured.out

    def test_list_empty_filter_raises_error_ui(self, cli_es, capsys):
        """Verifica que listar una categoría vacía dispara el error capturado."""
        # El repo está vacío, listar cualquier cosa debe fallar
        test_args = ["task-cli", "listar", "done"]
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        assert "No se encontraron tareas" in captured.out

    def test_system_logic_error_catch(self, cli_es, capsys):
        """Simula un TaskRelationError para cubrir el bloque de error de sistema."""
        from task_cli.domain.exceptions import TaskRelationError

        # 'Hackeamos' el manager para que lance un error interno al intentar listar
        with patch.object(cli_es._manager, "filter_by_status", side_effect=TaskRelationError("Consistencia rota")):
            test_args = ["task-cli", "listar"]
            with patch("sys.argv", test_args):
                cli_es.run()

        captured = capsys.readouterr()
        assert "[SISTEMA] Error de lógica interna" in captured.out

    def test_fatal_error_catch(self, cli_es, capsys):
        """Simula una explosión total (ej. error de memoria) para el bloque FATAL."""
        with patch.object(cli_es._manager, "add", side_effect=RuntimeError("Explosión")):
            test_args = ["task-cli", "añadir", "Boom"]
            with patch("sys.argv", test_args):
                cli_es.run()

        captured = capsys.readouterr()
        assert "FATAL: Ocurrió un error inesperado" in captured.out

    def test_update_command_flow(self, cli_es, capsys):
        """Cubre el Happy Path de _cmd_update."""
        repo = cli_es._manager._repository
        with repo:
            # Primero inyectamos una tarea para poder actualizarla
            TaskDataset().add("Original", status=TaskStatus.TODO, task_id=5).load_into(repo)

        test_args = ["task-cli", "actualizar", "5", "Modificada"]
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        assert "Actualizaste esta tarea existente" in captured.out
        assert "Modificada" in captured.out

    def test_delete_command_success_flow(self, cli_es, capsys):
        """Cubre el Happy Path de _cmd_delete."""
        repo = cli_es._manager._repository
        with repo:
            TaskDataset().add("A borrar", status=TaskStatus.TODO, task_id=6).load_into(repo)

        test_args = ["task-cli", "eliminar", "6"]
        with patch("sys.argv", test_args):
            cli_es.run()

        captured = capsys.readouterr()
        assert "Eliminaste esta tarea" in captured.out