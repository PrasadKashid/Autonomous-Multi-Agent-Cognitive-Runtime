from app.memory.agent_memory import AgentMemory


class MemoryManager:

    def __init__(self):
        self.agent_memories = {}

    def get_memory(self, agent_name):

        if agent_name not in self.agent_memories:
            self.agent_memories[agent_name] = AgentMemory(agent_name)

        return self.agent_memories[agent_name]


memory_manager = MemoryManager()
