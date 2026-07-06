from app.llm.settings import LLM_PROVIDER

from app.llm.providers.ollama_llm import OllamaLLM
from app.llm.providers.local_llm import LocalLLM


class LLMFactory:

    @staticmethod
    def get_llm():

        if LLM_PROVIDER == "ollama":
            return OllamaLLM()
        return LocalLLM()


llm_factory = LLMFactory()
