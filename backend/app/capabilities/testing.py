from app.capabilities.base_capability import BaseCapability


class TestingCapability(BaseCapability):

    def __init__(self):
        super().__init__("QA_AGENT")

    def execute(self, task_name, depedency_output, workflow_context, memories):
        return self.ask_llm(
            task=task_name,
            dependencies=depedency_output,
            workflow_context=workflow_context,
            memories=memories,
        )
