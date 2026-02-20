from task_cli.domain.dtos import TaskDTO
from task_cli.domain.task import TaskStatus


class TaskCliFormatter:

    _STATUS_ICON = {
        TaskStatus.TODO.value: "○",
        TaskStatus.IN_PROGRESS.value: "◐",
        TaskStatus.DONE.value: "●",
    }

    @classmethod
    def format_task(cls, task: TaskDTO) -> str:
        status_icon = cls._STATUS_ICON.get(task.status, "?")
        return f"{status_icon}[{task.status}] | #{task.task_id} | {task.description}"

    @staticmethod
    def format_task_list(task_list: list[TaskDTO]) -> str:
        return "\n".join(
            TaskCliFormatter.format_task(task)
            for task in task_list
        )