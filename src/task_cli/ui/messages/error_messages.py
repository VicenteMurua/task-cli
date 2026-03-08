from task_cli.domain.exceptions import (
    IllegalTaskDescriptionError,
    TaskNotFoundError,
    NoTaskOnFilter
)

ERROR_CATALOG = {
    "en": {
        IllegalTaskDescriptionError: lambda e: f"Description is invalid. It cannot be empty.",
        TaskNotFoundError: lambda e: f"Task with ID {e.task_id} not found.",
        NoTaskOnFilter: lambda e: f"No tasks found with status: {e.filter}"
    },
    "es": {
        IllegalTaskDescriptionError: lambda e: f"La descripción no es válida. No puede estar vacía.",
        TaskNotFoundError: lambda e: f"No se encontró la tarea con ID {e.task_id}.",
        NoTaskOnFilter: lambda e: f"No se encontraron tareas con el estado: {e.filter}"
    }
}

RETRY_MESSAGES = {
    "en": "Don't worry, try a new one!",
    "es": "No te preocupes, ¡intenta otra vez!",
}