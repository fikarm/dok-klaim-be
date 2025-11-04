from contextlib import AbstractAsyncContextManager
from src.memory.memory import get_memory_saver
from langgraph.checkpoint.memory import InMemorySaver


async def initialize_database() -> AbstractAsyncContextManager[InMemorySaver]:
    """
    Initialize the appropriate database checkpointer based on configuration.
    Returns an initialized AsyncCheckpointer instance.
    """
    return InMemorySaver()


def memory_saver():
    return InMemorySaver()
