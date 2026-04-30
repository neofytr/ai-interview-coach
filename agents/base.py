from utils import LLMClient


class BaseAgent:
    def __init__(self, prompt_name: str, llm: LLMClient) -> None:
        self.system_prompt = LLMClient.load_prompt(prompt_name)
        self.llm = llm
