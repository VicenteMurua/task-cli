class TaskException(Exception):
    pass

class TaskValidationError(TaskException, ValueError):
    pass

class TaskNotFoundError(TaskException, KeyError):
    pass