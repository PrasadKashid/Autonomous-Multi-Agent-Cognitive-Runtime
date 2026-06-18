class MemoryRepository:
    def __init__(self):
        self._memory = {}

    def save(self, agent_name, key, value):
        if agent_name not in self._memory:
            self._memory[agent_name] = {}

        self._memory[agent_name][key] = value

    def get(self, agent_name, key):
        if agent_name not in self._memory:
            return None
        return self._memory[agent_name].get(key)

    def get_all(self, agent_name):
        if agent_name not in self._memory:
            return {}

        return self._memory[agent_name]


memory_repository = MemoryRepository()
