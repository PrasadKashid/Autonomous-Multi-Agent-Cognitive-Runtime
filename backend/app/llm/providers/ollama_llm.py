from app.llm.base_llm import BaseLLM
import requests


class OllamaLLM(BaseLLM):

    def generate(self, prompt: str) -> str:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "stream": False,
            },
        )

        return response.json()["response"]
