from src.task_cli.domain.dtos import TaskDTO
from src.task_cli.domain.task import TaskStatus
from datetime import datetime, timedelta

now = datetime.now()
tomorrow = now + timedelta(days=1)

fake_dto1 = {
    "task_id": 1,
    "description": "Tarea Falsa 1",
    "status": TaskStatus.TODO.value,
    "created_at": now.isoformat(),
    "updated_at": now.isoformat(),
}

fake_dto2 = {
    "task_id": 2,
    "description": "Tarea Falsa 2",
    "status": TaskStatus.TODO.value,
    "created_at": tomorrow.isoformat(),
    "updated_at": tomorrow.isoformat(),
}

fake_dto_list: list[TaskDTO] = [
    TaskDTO(**fake_dto1),
    TaskDTO(**fake_dto2),
]