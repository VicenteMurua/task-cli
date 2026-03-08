from datetime import datetime
from task_cli.domain.dtos import TaskDTO
from task_cli.domain.task import TaskStatus
from task_cli.ui.messages.error_messages import (
    ERROR_CATALOG, RETRY_MESSAGES
)

import textwrap
import re
from colorama import init, Fore, Style
init(autoreset=True)


ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
def visible_len(s: str) -> int:
    """
    Calcula la longitud de una cadena ignorando códigos ANSI de color.

    Esto permite alinear texto con colores sin que los códigos influyan en
    la longitud visual.

    Parameters
    ----------
    s : str
        Cadena que puede contener secuencias ANSI.

    Returns
    -------
    int
        Longitud visible de la cadena.
    """
    return len(ANSI_ESCAPE.sub('', s))

def truncate(text: str, width: int) -> str:
    """
    Trunca un texto a un ancho máximo, agregando '...' si es necesario.

    Parameters
    ----------
    text : str
        Texto a truncar.
    width : int
        Ancho máximo permitido.

    Returns
    -------
    str
        Texto truncado.
    """
    if visible_len(text) <= width:
        return text
    return text[:width - 3] + "..."

class TableStyle:
    """
    Configuración de estilo para tablas en consola.

    Parameters
    ----------
    ascii_mode : bool, default=True
        Si True, se usan caracteres ASCII simples. Si False, se usan
        caracteres de caja UTF-8 para bordes más visuales.

    Attributes
    ----------
    cell_border : str
        Carácter que delimita las celdas.
    row_sep : str
        Carácter usado para separar filas.
    header_sep : str
        Carácter usado para separar encabezados.
    corner_tl, corner_tr, corner_bl, corner_br : str
        Esquinas de la tabla.
    intersection, t_top, t_bot, t_left, t_right : str
        Símbolos para intersecciones y uniones de líneas.
    error : str
        Símbolo para marcar errores.
    """
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
            self.error = "!"

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
            self.error = "✖"

class TaskCliFormatter:
    """
    Formatea tareas (`TaskDTO`) para mostrarlas en consola.

    Provee funciones para:
    - Mostrar tablas de tareas.
    - Mostrar detalles de una tarea individual.
    - Formatear errores de cliente con colores y mensajes multilenguaje.

    Usa `TableStyle` para determinar bordes y símbolos de tabla.
    """
    _STATUS_ICON = {
        TaskStatus.TODO.value: Fore.YELLOW + "▷" + Style.RESET_ALL,
        TaskStatus.IN_PROGRESS.value: Fore.CYAN + "▶" + Style.RESET_ALL,
        TaskStatus.DONE.value: Fore.GREEN + "✓" + Style.RESET_ALL,
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
    def _format_task(cls, task: TaskDTO, style: TableStyle) -> str:
        status_icon = cls._STATUS_ICON.get(task.status, "?")

        description_width = cls._COLUMNS[3]["width"]
        description = truncate(task.description, description_width)

        values = [
            str(task.task_id),
            status_icon,
            task.status,
            description,
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
    def _format_header(cls, style: TableStyle) -> str:
        values = [column["name"] for column in cls._COLUMNS]
        cells = [
            cls._format_cell(
                value,
                column["width"],
                "^",
                " "
            )
            for value, column in zip(values, cls._COLUMNS)
        ]

        border = style.cell_border
        return f"{border} " + f" {border} ".join(cells) + f" {border}"

    @classmethod
    def _format_row(cls, style: TableStyle, mode: str | None = None) -> str:
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
    def _format_task_list(cls, task_list: list[TaskDTO], style: TableStyle) -> list[str]:
        return [cls._format_task(task, style=style) for task in task_list]

    @classmethod
    def _get_row_separators(cls, style: TableStyle) -> tuple[str,str,str]:
        top: str = cls._format_row(style=style, mode="top")
        mid: str = cls._format_row(style=style)
        bot: str = cls._format_row(style=style, mode="bot")
        return top, mid, bot

    @classmethod
    def format_task_table(cls, task: TaskDTO, style: TableStyle) -> str:
        """
        Genera una tabla de una sola fila para una tarea.

        Parameters
        ----------
        task : TaskDTO
            Tarea a mostrar.
        style : TableStyle
            Configuración visual de la tabla.

        Returns
        -------
        str
            Cadena formateada representando la tarea en tabla.
        """
        header: str = cls._format_header(style=style)
        body: str = cls._format_task(task, style=style)
        no_format_table: list[str] = [header,body]

        top_sep, mid_sep, bot_sep = cls._get_row_separators(style=style)
        table: str = top_sep + mid_sep.join(no_format_table) + bot_sep
        return table

    @classmethod
    def format_tasks_table(cls, tasks: list[TaskDTO], style: TableStyle) -> str:
        """
        Genera una tabla para varias tareas.

        Parameters
        ----------
        tasks : list[TaskDTO]
            Lista de tareas a mostrar.
        style : TableStyle
            Configuración visual de la tabla.

        Returns
        -------
        str
            Cadena formateada con todas las tareas en tabla.
        """
        header: str =cls._format_header(style=style)
        body: list[str] = cls._format_task_list(tasks, style=style)
        no_format_table: list[str] = [header,*body]

        top_sep, mid_sep, bot_sep = cls._get_row_separators(style=style)
        table: str = top_sep + mid_sep.join(no_format_table) + bot_sep
        return table

    @staticmethod
    def _render_two_col_row(left: str, right: str, col_width: int, style: TableStyle, icon: str | None = None) -> str:
        border = style.cell_border
        vertical = "│" if style.cell_border != "|" else "|"

        if icon:
            right = right.ljust(col_width - visible_len(icon) - 1) + " " + icon
        else:
            right = right.ljust(col_width)

        return (
            f"{border} "
            f"{left.ljust(col_width)} "
            f"{vertical} "
            f"{right} "
            f"{border}"
        )

    @staticmethod
    def _render_full_width_block(text: str, width: int, style: TableStyle) -> str:
        border = style.cell_border
        wrapped = textwrap.wrap(text, width=width)

        lines = [
            f"{border} {line.ljust(width)} {border}"
            for line in wrapped
        ]

        return "\n".join(lines)

    @staticmethod
    def _build_frame(col_width: int, style: TableStyle):
        sep = style.row_sep

        separator = sep * (col_width + 2)
        top_union = separator + style.t_top + separator
        bot_union = separator + style.t_bot + separator

        top = f"\n{style.corner_tl}{top_union}{style.corner_tr}\n"
        mid_top = f"\n{style.t_left}{bot_union}{style.t_right}\n"
        mid_bot = f"\n{style.t_left}{top_union}{style.t_right}\n"
        bot = f"\n{style.corner_bl}{bot_union}{style.corner_br}\n"

        return top, mid_top, mid_bot, bot

    @classmethod
    def format_task_detail(cls, task: TaskDTO, style: TableStyle) -> str:
        """
        Muestra los detalles completos de una tarea en formato tabla.

        Incluye:
        - ID y estado con icono.
        - Descripción.
        - Fecha de creación y actualización.

        Parameters
        ----------
        task : TaskDTO
            Tarea a mostrar.
        style : TableStyle
            Configuración visual de la tabla.

        Returns
        -------
        str
            Tabla detallada formateada como string.
        """
        created = datetime.fromisoformat(task.created_at)
        updated = datetime.fromisoformat(task.updated_at)

        left_top = f"ID: {task.task_id}"
        right_top = f"Status: {task.status}"

        description = f"Description: {task.description}"

        left_bot = f"Created: {created.strftime('%Y-%m-%d %H:%M')}"
        right_bot = f"Updated: {updated.strftime('%Y-%m-%d %H:%M')}"

        col_width = max(len(left_top), len(right_top),len(left_bot), len(right_bot))

        total_width = col_width * 2 + 3

        top, mid_top, mid_bot, bot = cls._build_frame(col_width, style)

        status_icon = cls._STATUS_ICON[task.status]

        row1 = cls._render_two_col_row(left_top, right_top, col_width, style, status_icon)
        row2 = cls._render_full_width_block(description, total_width, style)
        row3 = cls._render_two_col_row(left_bot, right_bot, col_width, style)

        return top + row1 + mid_top + row2 + mid_bot + row3 + bot

    @staticmethod
    def format_client_error(exc, style, lang="es"):
        """
        Formatea un error de Task para mostrarlo en consola.

        Incluye:
        - Mensaje de error localizado según `lang`.
        - Indicador visual de error.
        - Mensaje de reintento.

        Parameters
        ----------
        exc : TaskException
            Error ocurrido.
        style : TableStyle
            Estilo visual (bordes y símbolos).
        lang : str, default='es'
            Idioma para el mensaje.

        Returns
        -------
        str
            Cadena lista para imprimir en consola con colores.
        """
        # 1. Buscamos el catálogo del idioma
        lang_dict = ERROR_CATALOG.get(lang, ERROR_CATALOG["en"])

        # 2. Obtenemos la función que genera el texto del error
        # Usamos type(exc) para saber cuál error es
        message_func = lang_dict.get(type(exc))

        if message_func:
            # 3. EJECUTAMOS la función. Como es un f-string, devuelve el texto directo.
            error_msg = message_func(exc)
        else:
            error_msg = str(exc)

        retry_msg = RETRY_MESSAGES.get(lang, RETRY_MESSAGES["en"])

        # Devolvemos el string final con colores
        return (
            f"{Fore.RED}[{style.error}] Error: {error_msg}{Style.RESET_ALL}\n"
            f"{Fore.CYAN} - {retry_msg}{Style.RESET_ALL}"
        )