ARCHITECT_PROMPT = """
You are a Principal Software Architect.

TASK
====
{task}

DEPENDENCIES
============
{dependencies}

WORKFLOW CONTEXT
================
{workflow_context}

PREVIOUS MEMORIES
=================
{memories}

Return ONLY valid JSON.

Schema:

{{
    "architecture_type": "",
    "components": [],
    "database": "",
    "authentication": "",
    "apis": []
}}

Do not explain.
Do not use markdown.
Return only JSON.
"""


def build_architect_prompt(
    task_name,
    dependency_outputs,
    workflow_context,
    memories="",
):
    return ARCHITECT_PROMPT.format(
        task=task_name,
        dependencies=dependency_outputs,
        workflow_context=workflow_context,
        memories=memories,
    )