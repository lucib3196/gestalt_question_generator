import streamlit as st
from services import send_message


def render_chat():
    for msg in st.session_state.messages or []:
        role = msg.get("role", "ai")
        with st.chat_message(role):
            st.markdown(msg["content"])


def render_chat_input():
    prompt = st.chat_input("Type a message")
    if prompt:
        send_message(prompt)
