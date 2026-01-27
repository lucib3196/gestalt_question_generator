import streamlit as st
from core import ENV, ChatOption, CHAT_OPTIONS


def render_title(
    title: str = "My Chat", env: ENV = ENV.LOCAL, thread_id: str | None = None
):
    if env == "local":
        title += " (Local DEV)"
    if thread_id:
        title += f" {thread_id}"

    st.set_page_config(page_title=title, layout="centered")
    st.title(title)


def render_select_box() -> str | None:
    # Renders the labele for the option
    options = [k for k, v in CHAT_OPTIONS.items() if v.active]

    add_radio = st.selectbox(
        label="Choose Chat Mode",
        options=options,
        index=None,
        key="chat_select",
        format_func=lambda k: CHAT_OPTIONS[k].label,
        on_change=handle_chatbot_change,
    )

    return add_radio


def render_chatbot_description():
    if "chat_data" in st.session_state:
        chat_data: ChatOption = st.session_state.chat_data
        st.subheader(chat_data.label)
        st.write(chat_data.description)

        # TODO: Fix this
        if chat_data.mode == "file":
            uploaded_files = st.file_uploader("File upload", accept_multiple_files=True)
            for uploaded_file in uploaded_files:
                print(uploaded_file)


def handle_chatbot_change():
    selected = st.session_state.chat_select
    if not selected:
        return
    chat_data = CHAT_OPTIONS[selected]
    st.session_state.chat_data = chat_data
