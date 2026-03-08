from datetime import datetime, timezone
from functools import wraps
from enum import Enum
from task_cli.domain.exceptions import TaskValidationError, IllegalTaskDescriptionError

time_zone = timezone.utc


class TaskStatus(Enum):
    """
    Enumeration representing the possible states of a task.

    Attributes
    ----------
    TODO
        The task has not been started yet.
    IN_PROGRESS
        The task is currently being worked on.
    DONE
        The task has been completed.
    """
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    DONE = "done"


def update_timestamp(func):
    """
    Decorator that automatically updates the `updated_at` timestamp
    after executing a method that mutates the task state.

    This ensures that any state change within the entity correctly
    reflects the last modification time.

    Parameters
    ----------
    func : callable
        Method that modifies the internal state of the task.

    Returns
    -------
    callable
        Wrapped function that executes the original method and then
        refreshes the `updated_at` timestamp.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        self._refresh_updated_at()
        return result

    return wrapper


class Task:
    """
    Domain entity representing a task.

    This class encapsulates business rules related to a task,
    including validation logic, state transitions, and timestamp
    management for creation and updates.

    Attributes
    ----------
    description : str
        Textual description of the task.
    status : TaskStatus
        Current state of the task.
    task_id : int
        Unique identifier of the task.
    created_at : datetime
        Timestamp indicating when the task was created.
    updated_at : datetime
        Timestamp indicating the last modification of the task.
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

        Parameters
        ----------
        description : str
            Task description.
        task_id : int
            Unique identifier of the task.
        status : TaskStatus
            Initial status of the task.
        created_at : datetime | None
            Creation timestamp. If None, the current time is used.
        updated_at : datetime | None
            Last update timestamp. If None, it defaults to created_at.

        Raises
        ------
        TypeError
            If an argument has an invalid type.
        TaskValidationError
            If any domain validation rule is violated.
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
        """Return the current task description."""
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
        """Return the current task status."""
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
        Validate that the description is a non-empty string.
        """
        if not isinstance(new_description, str):
            raise TypeError("Description must be a string")
        if not new_description.strip():
            raise IllegalTaskDescriptionError()

    @staticmethod
    def _validate_id(new_id: int) -> None:
        """
        Validate that the task ID is a positive integer.
        """
        if type(new_id) is not int:
            raise TypeError("ID must be a integer")
        if new_id <= 0:
            raise TaskValidationError("Task ID must be greater than 0")

    @staticmethod
    def _validate_status(new_status: TaskStatus) -> None:
        """
        Validate that the status is a TaskStatus enum member.
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
        Return a developer-friendly string representation of the task.
        """
        class_name = self.__class__.__name__
        return f"{class_name}({self._task_id=},{self.description=},{self.status=},{self.created_at=},{self.updated_at=})"

    def _refresh_updated_at(self):
        """
        Update the `updated_at` timestamp to the current time.
        """
        self._updated_at = datetime.now(time_zone)

    @update_timestamp
    def update_description(self, new_description: str) -> None:
        """
        Update the task description.

        This operation automatically refreshes the `updated_at` timestamp.
        """
        self._validate_description(new_description)
        self._set_description(new_description)

    @update_timestamp
    def update_status(self, status: TaskStatus) -> None:
        """
        Update the task status.

        This operation automatically refreshes the `updated_at` timestamp.
        """
        self._validate_status(status)
        self._set_status(status)