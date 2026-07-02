import json

from app.db.repositories.memory_repository import memory_repository
from app.memory.vector.vector_store import vector_store


class AgentMemory:

    def __init__(self, agent_name):
        self.agent_name = agent_name

    def _build_embedding_text(self, memory_data):

        if isinstance(memory_data, dict):

            lines = []

            for key, value in memory_data.items():

                if isinstance(value, list):
                    value = ", ".join(map(str, value))

                lines.append(f"{key}: {value}")

            return "\n".join(lines)

        return str(memory_data)

    def store(
        self,
        workflow_id: str,
        task_name: str,
        memory_data,
    ):

        # ---------- SQL ----------
        memory_repository.save(
            workflow_id=workflow_id,
            agent_name=self.agent_name,
            task_name=task_name,
            memory_data=memory_data,
        )

        # ---------- Vector ----------
        embedding_text = self._build_embedding_text(memory_data)

        vector_store.add_memory(
            workflow_id=workflow_id,
            agent_name=self.agent_name,
            task_name=task_name,
            memory_data=embedding_text,
        )

    def get_recent(self, limit=10):

        return memory_repository.get_recent(
            agent_name=self.agent_name,
            limit=limit,
        )

    def get_workflow_memory(self, workflow_id):

        return memory_repository.get_by_workflow(workflow_id)

    def search(self, query, top_k=5):

        return vector_store.search_memories(
            agent_name=self.agent_name,
            query=query,
            top_k=top_k,
        )