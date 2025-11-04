from typing import Literal, List, TypedDict, TypeAlias, Dict
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from fastapi import UploadFile


class Thread(BaseModel):
    messages: List[AnyMessage] = Field(default=[])


class Threads(BaseModel):
    threads: Dict[str, Thread] = Field(
        description="kumpulan messages tiap thread/menu", default={}
    )


class ChatHistory(BaseModel):
    messages: list[AnyMessage]


class UserInput(BaseModel):
    pdfs: List[UploadFile] | None
    message: str = Field(
        description="User input to the agent.",
        examples=["What is the weather in Tokyo?"],
    )
    agent: str
    user_id: str | None = Field(
        description="User ID to persist and continue a conversation across multiple threads.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )
    thread_id: str | None = Field(
        description="Thread ID to persist and continue a multi-turn conversation.",
        default=None,
        examples=["847c6285-8fc9-4560-a83f-4e6285809254"],
    )


class PdfUnggah(BaseModel):
    path: str
    name: str


class ChatMeta(TypedDict, total=False):
    pdfs: List[PdfUnggah]
    is_display: bool
