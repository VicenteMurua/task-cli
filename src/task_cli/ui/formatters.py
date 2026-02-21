from task_cli.domain.dtos import TaskDTO
from task_cli.domain.task import TaskStatus
from colorama import init, Fore, Back, Style
init(autoreset=True)


class TableStyle:
    cell_border: str
    row_sep: str
    header_sep: str
    corner_tl: str
    corner_tr: str
    corner_bl: str
    corner_br: str
    def __init__(self, ascii_mode=True) -> None:
        if ascii_mode:
            self.cell_border = "|"
            self.row_sep = "-"
            self.header_sep = "-"
            self.intersection = "+"
            self.corner_tl = self.intersection
            self.corner_tr = self.intersection
            self.corner_bl = self.intersection
            self.corner_br = self.intersection
            self.t_top = self.intersection
            self.t_bot = self.intersection
            self.t_left = self.intersection
            self.t_right = self.intersection

        else:  # UTF-8 box drawing
            self.cell_border = "║"
            self.row_sep = "═"
            self.header_sep = "═"
            self.corner_tl = "╔"
            self.corner_tr = "╗"
            self.corner_bl = "╚"
            self.corner_br = "╝"
            self.intersection = "╬"
            self.t_top = "╦"
            self.t_bot = "╩"
            self.t_left = "╠"
            self.t_right = "╣"

class TaskCliFormatter:

    _STATUS_ICON = {
        TaskStatus.TODO.value: Fore.YELLOW + "○" + Style.RESET_ALL,
        TaskStatus.IN_PROGRESS.value: Fore.CYAN + "◐" + Style.RESET_ALL,
        TaskStatus.DONE.value: Fore.GREEN + "●" + Style.RESET_ALL,
    }
    _COLUMNS = [
        {"name": "ID", "width": 4, "align": ">", "fill": "0"},
        {"name": "@", "width": 1, "align": "^"},
        {"name": "Status", "width": len(TaskStatus.IN_PROGRESS.value), "align": "<"},
        {"name": "Description", "width": 50, "align": "<"},
    ]
    @staticmethod
    def _format_cell(value: str, width: int, align: str = "<", fill: str = " ") -> str:
        return f"{value:{fill}{align}{width}}"

    @classmethod
    def format_task(cls, task: TaskDTO, style: TableStyle) -> str:
        status_icon = cls._STATUS_ICON.get(task.status, "?")

        values = [
            str(task.task_id),
            status_icon,
            task.status,
            task.description,
        ]

        cells = [
            cls._format_cell(
                value,
                column["width"],
                column.get("align", "<"),
                column.get("fill", " ")
            )
            for value, column in zip(values, cls._COLUMNS)
        ]

        border = style.cell_border
        return f"{border} " + f" {border} ".join(cells) + f" {border}"

    @classmethod
    def format_header(cls, style: TableStyle) -> str:
        values = [column["name"] for column in cls._COLUMNS]
        cells = [
            cls._format_cell(
                value,
                column["width"],
                column.get("align", "<"),
                column.get("fill", " ")
            )
            for value, column in zip(values, cls._COLUMNS)
        ]

        border = style.cell_border
        return f"{border} " + f" {border} ".join(cells) + f" {border}"

    @classmethod
    def format_row(cls, style: TableStyle, mode: str|None = None) -> str:
        widths = [column["width"] for column in cls._COLUMNS]
        sep = style.row_sep
        cells = [sep*width for width in widths]
        if mode == "top":
            return f"\n{style.corner_tl}{sep}" + f"{sep}{style.t_top}{sep}".join(cells) + f"{sep}{style.corner_tr}\n"
        elif mode == "bot":
            return f"\n{style.corner_bl}{sep}" + f"{sep}{style.t_bot}{sep}".join(cells) + f"{sep}{style.corner_br}\n"
        else:
            return f"\n{style.t_left}{sep}" + f"{sep}{style.intersection}{sep}".join(cells) + f"{sep}{style.t_right}\n"

    @classmethod
    def format_task_list(cls, task_list: list[TaskDTO], style: TableStyle) -> list[str]:
        return [cls.format_task(task, style=style) for task in task_list]

    @classmethod
    def format_task_table(cls, task_list: list[TaskDTO], style: TableStyle) -> str:
        header: str =cls.format_header(style=style)
        body: list[str] = cls.format_task_list(task_list, style=style)
        no_format_table: list[str] = [header] + body

        top_sep: str = cls.format_row(style=style, mode="top")
        mid_sep: str = cls.format_row(style=style)
        bot_sep: str = cls.format_row(style=style, mode="bot")
        table: str = top_sep + mid_sep.join(no_format_table) + bot_sep
        return table