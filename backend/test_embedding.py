from app.llm.factory import llm_factory

llm = llm_factory.get_llm()

print(llm.generate("Say hello in JSON"))