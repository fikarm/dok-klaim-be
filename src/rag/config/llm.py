from langchain_ollama import ChatOllama


ollama_url = "http://localhost:11434"

cache = {}


def llm_init(model="qwen3:latest") -> ChatOllama:
    if model in cache:
        return cache[model]

    cache[model] = ChatOllama(base_url=ollama_url, model=model)
    return cache[model]
