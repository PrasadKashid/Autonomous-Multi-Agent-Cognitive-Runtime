class PlannedTask:

    def __init__(
        self,
        task_name,
        capability,
        dependencies=None,
    ):
        self.task_name = task_name
        self.capability = capability
        self.dependencies = dependencies or []
