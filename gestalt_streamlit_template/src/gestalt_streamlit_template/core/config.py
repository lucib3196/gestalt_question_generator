from pydantic import BaseModel, Field
from typing import Dict, Literal
from enum import Enum


class ALLOWED_MODE(str, Enum):
    TEXT = "text"
    FILE = "file"
    BOTH = "both"


CHAT_NAMES = Literal["mychat"]


class ChatOption(BaseModel):
    label: str = Field(description="Label for UI")
    chat_id: str = Field(description="ID for chatbot")
    description: str | None = Field(description="chatbot description")
    mode: ALLOWED_MODE = Field(
        default=ALLOWED_MODE.TEXT,
        description="Whether it accepts files or not",
    )
    active: bool = Field(default=True, description="Wether chatbot is available")


CHAT_OPTIONS: Dict[CHAT_NAMES, ChatOption] = {
    "mychat": ChatOption(
        label="My Chat",
        chat_id="question_classification",
        description="A simple chatbot",
        mode=ALLOWED_MODE.TEXT,
    )
}
