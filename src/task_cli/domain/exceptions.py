class TaskException(Exception):
    """
    Base exception for all errors raised within the Task Tracker domain.

    This class serves as the root of the domain-specific exception hierarchy,
    allowing callers to catch all task-related errors with a single exception
    type if desired.
    """
    pass


# --- VALIDATION LAYER (User Input) ---
# These inherit from ValueError to signal that the type is correct
# but the value violates domain constraints.

class TaskValidationError(TaskException, ValueError):
    """
    Base class for errors caused by invalid task data.

    Raised when user-provided values violate domain validation rules
    such as invalid identifiers, malformed descriptions, or other
    business constraints.
    """
    pass


class IllegalTaskDescriptionError(TaskValidationError):
    """
    Raised when a task description violates validation rules.

    This may occur when the description is empty, contains only
    whitespace, or exceeds the allowed length constraints.
    """
    pass


class TaskIDError(TaskValidationError):
    """
    Raised when a task identifier is invalid.

    Examples include identifiers that are zero, negative, or
    otherwise malformed according to the domain rules.
    """
    pass


# --- PERSISTENCE / BUSINESS LOGIC LAYER ---

class NoTaskOnFilter(TaskException, ValueError):
    """
    Raised when no tasks match the requested filter criteria.

    Attributes:
        filter: The status filter that produced no matching tasks.
    """

    def __init__(self, status_filter: str):
        self.filter = status_filter
        super().__init__(f"No tasks found for filter: {status_filter}")


class TaskNotFoundError(TaskException, KeyError):
    """
    Raised when attempting to operate on a task that does not exist.

    This typically occurs when retrieving, updating, or deleting a task
    using an identifier that is not present in the repository.

    Inherits from KeyError for semantic compatibility with dictionary-like
    storage systems.
    """

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class TaskAlreadyExistsError(TaskException, ValueError):
    """
    Raised when attempting to create a task with an identifier
    that is already present in the repository.
    """
    pass


# --- INTEGRITY / SYSTEM LAYER ---
# These represent programming errors or internal state inconsistencies.

class TaskRelationError(TaskException, RuntimeError):
    """
    Raised when an internal consistency rule is violated.

    Examples include invalid relationships between task states,
    timestamps, or other domain invariants that should never break
    during normal execution.
    """
    pass


class UnknownTaskError(TaskException, RuntimeError):
    """
    Raised when the system encounters an unexpected or unsupported
    task state.

    This typically indicates a programming error, corrupted data,
    or an unhandled domain condition.
    """
    pass

class NoTaskToList(TaskException):
    pass