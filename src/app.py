from fastapi import FastAPI
from fastapi.routing import APIRoute
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from src.memory import initialize_database, memory_saver
from agents import agents, get_agent
from src.routers.ChatRouter import ChatRouter


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Dijalankan ketika _startup_ dan _shutdown_ dari FastApi.
    Dekorator @asynccontextmanager memberikan implikasi:
    - `function` bisa digunakan dengan keyword `async with`.
    - Kode sebelum `yield` akan dijalankan setelah _startup_.
    - Kode setelah `yield` akan dijalankan sebelum _shutdown_.
    """
    # Inisiasi checkpointer (untuk short-term memory)
    # TODO: inisiasi store (untuk long-term memory)
    # async with initialize_database() as saver:

    print("before yield")

    # # set checkpointer dan persistent store ke agent
    # for agent_key in agents:
    #     agent = get_agent(agent_key)
    #     agent.checkpointer = memory_saver()
    #     # TODO: store

    yield

    print("after yield")


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate idiomatic operation IDs for OpenAPI client generation."""
    return route.name


app = FastAPI(lifespan=lifespan, custom_generate_unique_id=custom_generate_unique_id)


app.include_router(ChatRouter)
