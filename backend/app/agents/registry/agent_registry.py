class AgentRegistry:

    def __init__(self):
        self.agents = {}

    def register_agent(self, agent_name, capabilities):
        self.agents[agent_name] = capabilities

    def find_agent(self, capability):

        for agent_name, capabilities in self.agents.items():

            if capability in capabilities:
                return agent_name

        return None

    def get_all_agents(self):
        return self.agents


agent_registry = AgentRegistry()
