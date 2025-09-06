import os
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL")

class LLMManager:
    def __init__(self):
        self.anthropic_api_key = ANTHROPIC_API_KEY

    def get_llm(self):
        """Crea y retorna una nueva instancia de LLM"""
        return ChatAnthropic(
            model=ANTHROPIC_MODEL,
            api_key= self.anthropic_api_key,
        )