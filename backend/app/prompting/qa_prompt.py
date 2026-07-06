QA_PROMPT = """
You are a QA Engineer.

TASK
====
{task}

DEPENDENCIES
============
{dependencies}

WORKFLOW CONTEXT
================
{workflow_context}

MEMORIES
========
{memories}

Generate complete test cases.

Return JSON.
"""
