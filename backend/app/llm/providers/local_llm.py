from app.llm.base_llm import BaseLLM


class LocalLLM(BaseLLM):

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:

        return f"""
{{
    "message":"Local LLM Response",
    "prompt":"{prompt}"
}}
"""


# class LocalLLM(BaseLLM):

#     def __init__(self):

#         self.model = ...

#     def generate(self, prompt):

#         response = self.model.invoke(prompt)

#         return response
