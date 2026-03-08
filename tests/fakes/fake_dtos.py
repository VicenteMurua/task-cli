from datetime import datetime
from task_cli.domain.dtos import TaskDTO
from task_cli.domain.task import TaskStatus


class TaskDataset:

    def __init__(self):
        self._tasks: list[TaskDTO] = []

    def add(
        self,
        description: str,
        status: TaskStatus,
        task_id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "TaskDataset":

        now = datetime.now()

        task_id = task_id or (len(self._tasks) + 1)
        created_at = created_at or now
        updated_at = updated_at or created_at

        dto = TaskDTO(
            task_id=task_id,
            description=description,
            status=status.value,
            created_at=created_at.isoformat(),
            updated_at=updated_at.isoformat(),
        )

        self._tasks.append(dto)
        return self

    def all(self) -> list[TaskDTO]:
        return list(self._tasks)

    def by_status(self, status: TaskStatus) -> list[TaskDTO]:
        return [t for t in self._tasks if t.status == status.value]

    def todo(self) -> list[TaskDTO]:
        return self.by_status(TaskStatus.TODO)

    def in_progress(self) -> list[TaskDTO]:
        return self.by_status(TaskStatus.IN_PROGRESS)

    def done(self) -> list[TaskDTO]:
        return self.by_status(TaskStatus.DONE)

    def count(self, status: TaskStatus | None = None) -> int:
        if status is None:
            return len(self._tasks)
        return len(self.by_status(status))

    def add_many(self, descriptions: list[str], status: TaskStatus) -> "TaskDataset":
        for desc in descriptions:
            self.add(description=desc, status=status)
        return self

    def load_into(self, repo) -> None:
        with repo as r:
            for dto in self._tasks:
                r.add(dto)