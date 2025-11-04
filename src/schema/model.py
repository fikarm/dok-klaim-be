from enum import Enum
from typing import TypeAlias


class LlamaModelName(Enum):
    LLAMA3_1_8B = "llama3.1:8b"


class GemmaModelName(Enum):
    GEMMA3_4B = "gemma3:4b"
    GEMMA3_12B = "gemma3:12b"
    GEMMA3_27B = "gemma3:27b"


AllModelEnum: TypeAlias = LlamaModelName | GemmaModelName
