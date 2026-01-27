from typing import Any, List
from pydantic import BaseModel
import streamlit as st
from .config import CHAT_NAMES
from services.llm_services import get_thread_id, initialize_thread_id


class DefaultState(BaseModel):
    messages: List[Any] = []
    thread_id: str | None = None
    chat_select: CHAT_NAMES | None


DEFAULT_STATE = DefaultState(
    messages=[], chat_select=None, thread_id=initialize_thread_id()
)


def init_session():
    for key, value in DEFAULT_STATE.model_dump().items():
        if key not in st.session_state:
            st.session_state[key] = value
