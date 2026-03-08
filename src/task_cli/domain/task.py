from datetime import datetime, timezone
from functools import wraps
from enum import Enum
from task_cli.domain.exceptions import TaskValidationError, IllegalTaskDescriptionError

time_zone = timezone.utc


class TaskStatus(Enum):
    """
    Enumeration of the possible lifecycle states of a task.

    Members:
        TODO: The task has not been started yet.
        IN_PROGRESS: Work on the task is currently underway.
        DONE: The task has been completed.
    """
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


def update_timestamp(func):
    """
    Decorator that refreshes the `updated_at` timestamp after a state mutation.

    This decorator should be applied to methods that modify the internal
    state of a `Task` instance. After the wrapped method executes
    successfully, the `updated_at` attribute is automatically updated
    to the current time.

    Args:
        func: The method responsible for mutating the task state.

    Returns:
        The wrapped method with automatic timestamp refresh.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._refresh_updated_at()
        return result

    return wrapper


class Task:
    """
    Domain entity representing a task within the task tracking system.

    The Task entity encapsulates domain invariants such as validation
    of identifiers, description constraints, state transitions,
    and timestamp management.

    Instances of this class are responsible for maintaining their
    own internal consistency.

    Attributes:
        _description: Human-readable description of the task.
        _status: Current lifecycle state of the task.
        _task_id: Unique identifier of the task.
        _created_at: Timestamp indicating when the task was created.
        _updated_at: Timestamp of the last modification.
    """

    _description: str
    _status: TaskStatus
    _task_id: int
    _created_at: datetime
    _updated_at: datetime

    def __init__(
            self,
            description: str,
            task_id: int,
            status: TaskStatus,
            created_at: datetime | None = None,
            updated_at: datetime | None = None
    ):
        """
        Initialize a new Task instance.

        Args:
            description: Text describing the task.
            task_id: Unique identifier of the task.
            status: Initial task status.
            created_at: Creation timestamp. If None, the current UTC time is used.
            updated_at: Last modification timestamp. If None, it defaults to
                the same value as `created_at`.

        Raises:
            TypeError: If an argument has an invalid type.
            TaskValidationError: If any domain validation rule is violated.
        """
        self._validate_description(description)
        self._validate_id(task_id)
        self._validate_status(status)
        self._validate_creation_date(created_at)
        self._validate_updated_date(updated_at)
        self._validate_dates_relation(new_created_at=created_at, new_updated_at=updated_at)

        self._description = description
        self._task_id = task_id
        self._status = status
        self._created_at = datetime.now(time_zone) if created_at is None else created_at
        self._updated_at = self._created_at if updated_at is None else updated_at

    @property
    def description(self) -> str:
        """Return the task description."""
        return self._description

    def _set_description(self, description: str) -> None:
        """
        Set the internal description of the task.

        This method is intended for internal use within the entity.
        """
        self._validate_description(description)
        self._description = description

    @property
    def status(self) -> TaskStatus:
        """Return the current status of the task."""
        return self._status

    def _set_status(self, status: TaskStatus) -> None:
        """
        Set the internal task status.

        This method is intended for internal use within the entity.
        """
        self._validate_status(status)
        self._status = status

    @property
    def task_id(self) -> int:
        """Return the unique identifier of the task."""
        return self._task_id

    @property
    def created_at(self) -> datetime:
        """Return the creation timestamp of the task."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Return the last update timestamp of the task."""
        return self._updated_at

    @staticmethod
    def _validate_description(new_description: str) -> None:
        """
        Validate a task description.

        Ensures the description is a string containing at least one
        non-whitespace character.

        Raises:
            TypeError: If the value is not a string.
            IllegalTaskDescriptionError: If the description is empty or whitespace.
        """
        if not isinstance(new_description, str):
            raise TypeError("Description must be a string")
        if not new_description.strip():
            raise IllegalTaskDescriptionError()

    @staticmethod
    def _validate_id(new_id: int) -> None:
        """
        Validate the task identifier.

        The identifier must be a positive integer.

        Raises:
            TypeError: If the value is not an integer.
            TaskValidationError: If the identifier is not greater than zero.
        """
        if type(new_id) is not int:
            raise TypeError("ID must be an integer")
        if new_id <= 0:
            raise TaskValidationError("Task ID must be greater than 0")

    @staticmethod
    def _validate_status(new_status: TaskStatus) -> None:
        """
        Validate the task status.

        Ensures that the provided value is a valid `TaskStatus` member.

        Raises:
            TypeError: If the value is not a `TaskStatus`.
        """
        if type(new_status) is not TaskStatus:
            raise TypeError("Status must be a TaskStatus")

    @staticmethod
    def _validate_creation_date(new_date: datetime | None) -> None:
        """
        Validate the type of the creation timestamp.
        """
        if not isinstance(new_date, (datetime, type(None))):
            raise TypeError("CreatedAt must be a datetime or None")

    @staticmethod
    def _validate_updated_date(new_date: datetime | None) -> None:
        """
        Validate the type of the updated timestamp.
        """
        if not isinstance(new_date, (datetime, type(None))):
            raise TypeError("UpdatedAt must be a datetime or None")

    @staticmethod
    def _validate_dates_relation(new_created_at: datetime | None, new_updated_at: datetime | None) -> None:
        """
        Validate the logical relationship between creation and update timestamps.

        Rules:
            - Both timestamps must either be provided together or both be None.
            - If provided, `created_at` must not be later than `updated_at`.

        Raises:
            TaskValidationError: If the timestamps violate domain invariants.
        """
        if (new_created_at is None) ^ (new_updated_at is None):
            raise TaskValidationError(
                "CreatedAt and updatedAt must both be None or defined at the same time"
            )

        if new_created_at is not None and new_updated_at is not None:
            if new_created_at > new_updated_at:
                raise TaskValidationError(
                    "CreatedAt must not be greater than UpdatedAt"
                )

    def __repr__(self):
        """
        Return a developer-oriented representation of the task.

        This representation includes the identifier, description,
        status, and timestamps to facilitate debugging.
        """
        class_name = self.__class__.__name__
        return f"{class_name}({self._task_id=},{self.description=},{self.status=},{self.created_at=},{self.updated_at=})"

    def _refresh_updated_at(self):
        """
        Update the `updated_at` field to the current UTC time.

        This method is typically invoked automatically by the
        `update_timestamp` decorator after a state mutation.
        """
        self._updated_at = datetime.now(time_zone)

    @update_timestamp
    def update_description(self, new_description: str) -> None:
        """
        Update the task description.

        The `updated_at` timestamp is automatically refreshed.

        Args:
            new_description: The new description for the task.

        Raises:
            TypeError: If the value is not a string.
            IllegalTaskDescriptionError: If the description is invalid.
        """
        self._validate_description(new_description)
        self._set_description(new_description)

    @update_timestamp
    def update_status(self, status: TaskStatus) -> None:
        """
        Change the task status.

        The `updated_at` timestamp is automatically refreshed.

        Args:
            status: The new status of the task.

        Raises:
            TypeError: If the value is not a valid `TaskStatus`.
        """
        self._validate_status(status)
        self._set_status(status)