from langgraph.checkpoint.memory import InMemorySaver


def get_memory_saver():
    return InMemorySaver()
