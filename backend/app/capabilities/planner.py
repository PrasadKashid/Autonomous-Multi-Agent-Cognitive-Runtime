from app.llm.factory import llm_factory
from app.llm.planner_parser import planner_parser
from app.prompting.planner_prompt import PLANNER_PROMPT


class PlannerCapability:

    def __init__(self):
        self.llm = llm_factory.get_llm()

    def execute(self, request):

        prompt = PLANNER_PROMPT.format(
            task=request,
        )

        response = self.llm.generate(prompt)
        return planner_parser.parse(response)


planner_capability = PlannerCapability()
