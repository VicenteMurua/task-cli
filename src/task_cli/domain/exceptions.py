class TaskException(Exception):
    """Base jerárquica para todas las excepciones del dominio Task Tracker."""
    pass

# --- CAPA DE VALIDACIÓN (Input del Usuario) ---
# Heredan de ValueError para indicar que el dato es del tipo correcto pero contenido inválido.

class TaskValidationError(TaskException, ValueError):
    """Error base para datos que no cumplen las reglas de negocio."""
    pass

class IllegalTaskDescriptionError(TaskValidationError):
    """Se lanza cuando la descripción está vacía, es solo espacios o excede límites."""
    pass

class TaskIDError(TaskValidationError):
    """Se lanza cuando el ID es menor o igual a cero o tiene un formato inválido."""
    pass

# --- CAPA DE PERSISTENCIA Y LÓGICA DE NEGOCIO ---
class NoTaskOnFilter(TaskException, ValueError):
    def __init__(self, status_filter: str):
        self.filter = status_filter

class TaskNotFoundError(TaskException, KeyError):
    """Se lanza cuando se intenta operar sobre un ID que no existe en el repositorio."""
    # Hereda de KeyError por compatibilidad semántica con búsquedas en diccionarios/almacenes.
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")

class TaskAlreadyExistsError(TaskException, ValueError):
    """Se lanza al intentar crear una tarea con un ID que ya está en uso."""
    pass

# --- CAPA DE INTEGRIDAD Y SISTEMA (Errores de Programación o Datos Corruptos) ---

class TaskRelationError(TaskException, RuntimeError):
    """Error de integridad: inconsistencia entre estados o fechas del objeto."""
    # Hereda de RuntimeError porque no es un error de input del usuario,
    # sino un fallo en el estado de ejecución o consistencia interna.
    pass

class UnknownTaskError(TaskException, RuntimeError):
    pass