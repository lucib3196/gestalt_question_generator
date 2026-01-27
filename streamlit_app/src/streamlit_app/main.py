from core import init_session
from ui import (
    render_title,
    render_select_box,
    render_chatbot_description,
    render_chat,
    render_chat_input,
)
import streamlit as st


init_session()


def render_ui():
    # Header Section
    render_title(
        title=st.secrets["NAME"],
        env=st.secrets["ENV"],
        thread_id=st.session_state.thread_id,
    )
    print("Some change")
    render_select_box()
    render_chatbot_description()

    # Actual Chat Component
    render_chat()
    render_chat_input()


render_ui()
