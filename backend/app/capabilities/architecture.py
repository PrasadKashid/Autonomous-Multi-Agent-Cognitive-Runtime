from app.capabilities.base_capability import BaseCapability

class ArchitectureCapability(BaseCapability):

    def __init__(self):
        super().__init__("ARCHITECT_AGENT")

    def execute(
        self,
        task_name,
        dependency_outputs,
        workflow_context,
        memories,
    ):

        return self.ask_llm(
            task=task_name,
            dependency_outputs=dependency_outputs,
            workflow_context=workflow_context,
            memories=memories,
        )
