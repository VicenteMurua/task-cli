from task_cli.domain.dtos import TaskDTO
from task_cli.domain.task import TaskStatus
from datetime import datetime, timedelta

now = datetime.now()
tomorrow = now + timedelta(days=1)

fake_dict_1 = {
    "task_id": 1,
    "description": "Tarea Falsa 1",
    "status": TaskStatus.TODO.value,
    "created_at": now.isoformat(),
    "updated_at": now.isoformat(),
}
fake_dto_1 = TaskDTO(**fake_dict_1)

fake_dict_1_modified = {
    "task_id": 1,
    "description": "Tarea Falsa 1 modificada",
    "status": TaskStatus.IN_PROGRESS.value,
    "created_at": fake_dict_1["created_at"],
    "updated_at": fake_dict_1["updated_at"],
}
fake_dto_1_modified = TaskDTO(**fake_dict_1_modified)
fake_dict_2 = {
    "task_id": 2,
    "description": "Tarea Falsa 2",
    "status": TaskStatus.TODO.value,
    "created_at": tomorrow.isoformat(),
    "updated_at": tomorrow.isoformat(),
}
fake_dto_2 = TaskDTO(**fake_dict_2)
fake_dict_3_done = {
    "task_id": 3,
    "description": "Tarea Falsa 3",
    "status": TaskStatus.DONE.value,
    "created_at": tomorrow.isoformat(),
    "updated_at": tomorrow.isoformat(),
}
fake_dto_3_done = TaskDTO(**fake_dict_3_done)
fake_dict_4_in_progress = {
    "task_id": 4,
    "description": "Tarea Falsa 4",
    "status": TaskStatus.IN_PROGRESS.value,
    "created_at": tomorrow.isoformat(),
    "updated_at": tomorrow.isoformat(),
}
fake_dto_4_in_progress = TaskDTO(**fake_dict_4_in_progress)
fake_dto_list_no_duplicates: list[TaskDTO] = [
    fake_dto_1,
    fake_dto_2,
    fake_dto_3_done,
    fake_dto_4_in_progress,
]