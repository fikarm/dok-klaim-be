from langchain_ollama import ChatOllama


ollama_url = "http://localhost:11434"


def init(model="gemma3:12b"):
    return ChatOllama(base_url=ollama_url, model=model)
