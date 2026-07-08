import json

from app.prompting.architect_prompt import ARCHITECT_PROMPT
from app.prompting.developer_prompt import DEVELOPER_PROMPT
from app.prompting.pm_prompt import PM_PROMPT
from app.prompting.qa_prompt import QA_PROMPT


class PromptBuilder:

    PROMPTS = {
        "ARCHITECT_AGENT": ARCHITECT_PROMPT,
        "DEVELOPER_AGENT": DEVELOPER_PROMPT,
        "QA_AGENT": QA_PROMPT,
        "PM_AGENT": PM_PROMPT,
    }

    def build(
        self,
        agent_name,
        task,
        dependencies=None,
        workflow_context=None,
        memories=None,
    ):

        template = self.PROMPTS[agent_name]

        return template.format(
            task=task,
            dependencies=json.dumps(
                dependencies or {},
                indent=2,
            ),
            workflow_context=json.dumps(
                workflow_context or {},
                indent=2,
            ),
            memories=json.dumps(
                memories or [],
                indent=2,
            ),
        )


prompt_builder = PromptBuilder()
