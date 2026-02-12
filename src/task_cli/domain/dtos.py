from dataclasses import dataclass


@dataclass(frozen=True)
class TaskDTO:
    task_id: int
    description: str
    status: str
    created_at: str
    updated_at: str
