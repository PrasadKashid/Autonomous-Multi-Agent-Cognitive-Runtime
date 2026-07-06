from app.capabilities.base_capability import BaseCapability

class BackendCapability(BaseCapability):

    def __init__(self):
        super().__init__("DEVELOPER_PROMPT")

    def execute(
        self,
        task_name,
        dependency_outputs,
        workflow_context,
        memories,
    ):

        return self.ask_llm(
            task=task_name,
            dependencies=dependency_outputs,
            workflow_context=workflow_context,
            memories=memories,
        )
