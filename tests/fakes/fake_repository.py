# tests/fakes/fake_repository.py
"""
In-memory fake implementation of IRepository used for testing.

This fake repository mimics the behavior of the real persistence layer
(e.g., SQLiteRepo or FileRepo) while storing data in memory. Its purpose
is to allow deterministic and fast tests without relying on external
infrastructure such as databases or files.

Key characteristics
-------------------
- Stores TaskDTO objects in an internal dictionary.
- Enforces the same interface contract as IRepository.
- Raises the same domain exceptions as the real repository.
- Requires usage within a context manager to simulate resource lifecycle
  (similar to opening/closing a database connection).

This makes the FakeRepo suitable for unit tests that need realistic
repository behavior without the cost or complexity of real I/O.
"""
from task_cli.domain.task import TaskStatus
from task_cli.repository.task_repository import IRepository
from task_cli.domain.dtos import TaskDTO
from task_cli.domain.exceptions import TaskNotFoundError, TaskAlreadyExistsError


class FakeRepo(IRepository):
    """
    In-memory test double for IRepository.

    This class is designed for unit tests where a lightweight and
    predictable repository implementation is required. It reproduces
    the behavior and error conditions of the real repository while
    avoiding external dependencies.
    """

    def __init__(self):
        """Initialize the fake repository with empty storage."""
        self.storage: dict[int, TaskDTO] = {}
        self._is_active = False

    # --- INFRASTRUCTURE (Context lifecycle) ---

    def __enter__(self):
        """
        Activate the repository context.

        Simulates opening a database connection or loading a file-backed cache.
        """
        self._is_active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Deactivate the repository context.

        Simulates closing the connection or releasing resources.
        """
        self._is_active = False
        return False  # Do not suppress exceptions

    def _ensure_active(self):
        """
        Ensure the repository is being used inside a context manager.

        This simulates the safety checks commonly present in real
        infrastructure implementations (e.g., active database connection).
        """
        if not self._is_active:
            raise RuntimeError("Repository must be used within a context manager")

    # --- BUSINESS OPERATIONS ---

    def get_max_id(self) -> int:
        """
        Return the highest task ID currently stored.

        Returns
        -------
        int
            Maximum task ID, or 0 if the repository is empty.
        """
        self._ensure_active()
        return max(self.storage.keys(), default=0)

    def add(self, new_task: TaskDTO) -> None:
        """
        Add a new task to the repository.

        Raises
        ------
        TaskAlreadyExistsError
            If a task with the same ID already exists.
        """
        self._ensure_active()

        if new_task.task_id in self.storage:
            raise TaskAlreadyExistsError(new_task.task_id)

        self.storage[new_task.task_id] = new_task

    def update(self, updated_task: TaskDTO) -> None:
        """
        Update an existing task.

        Raises
        ------
        TaskNotFoundError
            If the task does not exist.
        """
        self._ensure_active()

        if updated_task.task_id not in self.storage:
            raise TaskNotFoundError(updated_task.task_id)

        self.storage[updated_task.task_id] = updated_task

    def delete(self, task_id: int) -> None:
        """
        Remove a task from the repository.

        Raises
        ------
        TaskNotFoundError
            If the task does not exist.
        """
        self._ensure_active()

        if task_id not in self.storage:
            raise TaskNotFoundError(task_id)

        del self.storage[task_id]

    def read(self, task_id: int) -> TaskDTO:
        """
        Retrieve a task by its ID.

        Raises
        ------
        TaskNotFoundError
            If the task does not exist.
        """
        self._ensure_active()

        if task_id not in self.storage:
            raise TaskNotFoundError(task_id)

        return self.storage[task_id]

    def filter_by_status(self, status_filter: TaskStatus | None) -> list[TaskDTO]:
        """
        Return tasks filtered by status.

        Parameters
        ----------
        status_filter : TaskStatus | None
            If None, all tasks are returned.

        Returns
        -------
        list[TaskDTO]
            Tasks matching the filter condition.
        """
        self._ensure_active()

        if status_filter is None:
            return list(self.storage.values())

        return [
            data
            for data in self.storage.values()
            if data.status == status_filter.value
        ]