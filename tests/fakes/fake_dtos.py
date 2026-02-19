from task_cli.domain.dtos import TaskDTO
from task_cli.domain.task import TaskStatus
from datetime import datetime, timedelta

now = datetime.now()
tomorrow = now + timedelta(days=1)

fake_todo_1_dict = {
    "task_id": 1,
    "description": "Tarea Falsa 1",
    "status": TaskStatus.TODO.value,
    "created_at": now.isoformat(),
    "updated_at": now.isoformat(),
}
fake_todo_1_dto = TaskDTO(**fake_todo_1_dict)

modified_todo_1_dict = {
    "task_id": 1,
    "description": "Tarea Falsa 1 modificada",
    "status": TaskStatus.IN_PROGRESS.value,
    "created_at": fake_todo_1_dict["created_at"],
    "updated_at": fake_todo_1_dict["updated_at"],
}
modified_dto_1_dto = TaskDTO(**modified_todo_1_dict)

fake_todo_2_dict = {
    "task_id": 2,
    "description": "Tarea Falsa 2",
    "status": TaskStatus.TODO.value,
    "created_at": tomorrow.isoformat(),
    "updated_at": tomorrow.isoformat(),
}
fake_todo_2_dto = TaskDTO(**fake_todo_2_dict)

fake_done_1_dict = {
    "task_id": 3,
    "description": "Tarea Falsa 3",
    "status": TaskStatus.DONE.value,
    "created_at": tomorrow.isoformat(),
    "updated_at": tomorrow.isoformat(),
}
fake_done_1_dto = TaskDTO(**fake_done_1_dict)

fake_in_progress_1_dict = {
    "task_id": 4,
    "description": "Tarea Falsa 4",
    "status": TaskStatus.IN_PROGRESS.value,
    "created_at": tomorrow.isoformat(),
    "updated_at": tomorrow.isoformat(),
}
fake_in_progress_1_dto = TaskDTO(**fake_in_progress_1_dict)

fake_dto_list_no_duplicates: list[TaskDTO] = [
    fake_todo_1_dto,
    fake_todo_2_dto,
    fake_done_1_dto,
    fake_in_progress_1_dto,
]