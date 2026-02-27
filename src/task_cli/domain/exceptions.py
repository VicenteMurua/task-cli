class TaskException(Exception):
    pass

class TaskValidationError(TaskException, ValueError):
    pass

class TaskNotFoundError(TaskException, KeyError):
    pass

class TaskAlreadyExistsError(TaskException, ValueError):
    pass

class IllegalTaskDescriptionError(TaskValidationError):
    pass

class TaskIDError(TaskValidationError):
    pass

class TaskRelationError(TaskException, RuntimeError):
    pass