from app.db.repositories.memory_repository import memory_repository


class AgentMemory:

    def __init__(self, agent_name):
        self.agent_name = agent_name

    def store(
        self,
        workflow_id: str,
        task_name: str,
        memory_data: str,
    ):
        memory_repository.save(
            workflow_id=workflow_id,
            agent_name=self.agent_name,
            task_name=task_name,
            memory_data=memory_data,
        )

    def get_recent(self, limit=10):
        return memory_repository.get_recent(
            agent_name=self.agent_name,
            limit=limit,
        )

    def get_workflow_memory(self, workflow_id):
        return memory_repository.get_by_workflow(workflow_id)
