from enum import Enum

from task_cli.domain.task import TaskStatus


class Msgs(Enum):
    SHOW = "show"
    LIST = "list"
    NOTHING_FILTERED = "nothing filtered"
class Action(Enum):
    ADD = "add"
    DELETE = "delete"
    MARK = "mark"
    MARK_TODO = "mark_todo"
    MARK_DONE = "mark-done"
    MARK_IN_PROGRESS = "mark-in-progress"
    UPDATE = "update"
    LIST = "list"
    READ = "read"

feedback_msgs = {
    "en":{
        Msgs.SHOW: "\nYou interacted with this task.",
        Msgs.LIST: "\nYou listed the tasks.",
    },
    "es":{
        Msgs.SHOW: "\nInteractuaste con esta tarea",
        Msgs.LIST: "\nListaste las tareas",
    }
}

action_msgs = {
    "en":{
        Action.ADD : "\nYou added this new task.",
        Action.UPDATE : "\nYou updated this existing task.",
        Action.DELETE: "\nYou removed this task.",
        Action.READ: "\nYou read this tasks.",
        Action.MARK: "\nYou mark this task.",
        Action.LIST: "\nYou listed the tasks.",
    },
    "es":{
        Action.ADD : "\nAñadiste esta tarea nueva.",
        Action.UPDATE : "\nActualizaste esta tarea existente.",
        Action.DELETE: "\nEliminaste esta tarea.",
        Action.READ: "\nLeíste esta tarea",
        Action.MARK: "\nMarcaste esta tarea.",
        Action.LIST: "\nListaste las tareas.",
    },
}

commands_data ={
    "en":{
        Action.ADD:{
            "command": {
                "name": "add",
                "help": "Add a new task to the tracker",
            },
            "parser1":{
                "name": "description",
                "help": "The description text of the task",
            },
        },
        Action.UPDATE:{
            "command": {
                "name": "update",
                "help": "Change the description of an existing task",
            },
            "parser1":{
                "name": "task_id",
                "help": "Unique identifier of the task to update",
            },
            "parser2":{
                "name": "description",
                "help": "New description text",
            },
        },
        Action.DELETE:{
            "command": {
                "name": "delete",
                "help": "Permanently remove a task from the list",
            },
            "parser1":{
                "name": "task_id",
                "help":"ID of the task to be deleted",
            },
        },
        Action.READ:{
            "command": {
                "name": "read",
                "help": "Read a task from the list",
            },
            "parser1":{
                "name": "task_id",
                "help": "ID of the task to be readd",
            },
            "parser2":{
                "name": "-d",
                "long name": "--detail",
                "help": "Show detailed view",
            },
        },
        Action.MARK_DONE:{
            "command": {
                "name": "mark-done",
                "help": "Set a task status to 'done'"
            },
            "parser1": {
                "name": "task_id",
                "help": "ID of the task to complete"
            },
        },
        Action.MARK_IN_PROGRESS:{
            "command": {
                "name": "mark-in-progress",
                "help": "Set a task status to mark 'in-progress'"
            },
            "parser1": {
                "name": "task_id",
                "help": "ID of the task to complete"
            },
        },
        Action.LIST:{
            "command": {
                "name": "list",
                "help": "Display tasks based on their current status",
            },
            "parser1": {
                "name": "filter",
                "help": "Filter by: todo, in-progress, or done (optional)",
            }
        }
    },
    "es": {
        Action.ADD: {
            "command": {
                "name": "añadir",
                "help": "Agregar una nueva tarea al tracker",
            },
            "parser1": {
                "name": "description",
                "help": "Texto de descripción de la tarea",
            },
        },
        Action.UPDATE: {
            "command": {
                "name": "actualizar",
                "help": "Cambiar la descripción de una tarea existente",
            },
            "parser1": {
                "name": "task_id",
                "help": "Identificador único de la tarea a actualizar",
            },
            "parser2": {
                "name": "description",
                "help": "Nuevo texto de descripción",
            },
        },
        Action.DELETE: {
            "command": {
                "name": "eliminar",
                "help": "Eliminar permanentemente una tarea de la lista",
            },
            "parser1": {
                "name": "task_id",
                "help": "ID de la tarea a eliminar",
            },
        },
        Action.READ: {
            "command": {
                "name": "leer",
                "help": "Leer una tarea de la lista",
            },
            "parser1": {
                "name": "task_id",
                "help": "ID de la tarea a leer",
            },
            "parser2": {
                "name": "-d",
                "long name": "--detail",
                "help": "Mostrar vista detallada",
            },
        },
        Action.MARK_DONE: {
            "command": {
                "name": "marcar-hecha",
                "help": "Marcar el estado de una tarea como 'hecha'",
            },
            "parser1": {
                "name": "task_id",
                "help": "ID de la tarea a completar",
            },
        },
        Action.MARK_IN_PROGRESS: {
            "command": {
                "name": "marcar-en-progreso",
                "help": "Marcar el estado de una tarea como 'en progreso'",
            },
            "parser1": {
                "name": "task_id",
                "help": "ID de la tarea a marcar",
            },
        },
        Action.LIST: {
            "command": {
                "name": "listar",
                "help": "Mostrar tareas según su estado actual",
            },
            "parser1": {
                "name": "filter",
                "help": f"Filtrar por: {TaskStatus.TODO.value}(a hacer), {TaskStatus.IN_PROGRESS.value}(en progreso) o {TaskStatus.DONE.value}(hecho) [opcional]",
            },
        },
    },
}