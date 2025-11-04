from functools import cache
from langchain_ollama import ChatOllama
from src.schema.model import AllModelEnum
from src.core.settings import settings


@cache
def get_model(model_name: AllModelEnum) -> ChatOllama:
    chat_ollama = ChatOllama(base_url=settings.OLLAMA_BASE_URL, model=model_name.value)
    return chat_ollama
