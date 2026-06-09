class AgentMemory:

    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.memories = {}

    def store(self, key, value):
        self.memories[key] = value

    def get(self, key):
        return self.memories[key]

    def get_all(self):
        return self.memories
