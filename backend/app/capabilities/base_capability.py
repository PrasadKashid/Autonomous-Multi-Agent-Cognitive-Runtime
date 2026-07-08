from app.prompting.prompt_builder import prompt_builder
from app.llm.factory import llm_factory
from app.llm.parser import response_parser


class BaseCapability:

    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.llm = llm_factory.get_llm()

    def ask_llm(
        self,
        task,
        dependency_outputs,
        workflow_context,
        memories,
    ):

        prompt = prompt_builder.build(
            agent_name=self.agent_name,
            task=task,
            dependencies=dependency_outputs,
            workflow_context=workflow_context,
            memories=memories,
        )

        print(f"\n===== GENERATED PROMPT ===== {self.agent_name}")
        print(prompt)

        response = self.llm.generate(prompt)

        print(f"\n===== LLM RESPONSE ===== {self.agent_name}")
        print(response)

        return response_parser.parse(response)
