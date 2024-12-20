import pydantic
from enum import Enum


class SpeakerType(str, Enum):
    ASSISTANT = "assistant"
    USER = "user"


class History(pydantic.BaseModel):
    speaker: SpeakerType
    message: str
