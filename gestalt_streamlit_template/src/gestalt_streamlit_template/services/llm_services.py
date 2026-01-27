import streamlit as st
from core import client
from .async_wrappers import run_async


async def get_thread_id():
    return await client.threads.create()


def initialize_thread_id() -> str:
    if "thread_id" not in st.session_state:
        thread = run_async(get_thread_id())
        st.session_state.thread_id = thread["thread_id"]
    return st.session_state.thread_id


async def stream_langgraph(messages, thread_id: str | None, assistant_id: str):
    async for chunk in client.runs.stream(
        thread_id,
        assistant_id=assistant_id,
        input={"messages": messages},
        stream_mode="updates",
    ):
        if chunk.event != "updates":
            continue
        model_data = chunk.data.get("model")
        if not model_data:
            continue
        messages_list = model_data.get("messages", [])

        if not messages_list:
            continue
        last_msg = messages_list[-1]
        # print("Last message in stream", last_msg)
        if last_msg:
            yield last_msg


def send_message(prompt: str):
    if not prompt:
        return
    st.chat_message("user").markdown(prompt)
    user_message = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_message)
    assistant_box = st.chat_message("assistant")
    placeholder = assistant_box.empty()
    tool_placeholder = assistant_box.container()

    async def consume():
        buffer = ""
        tool_calls_rendered = set()
        thread_id = None
        if "thread_id" in st.session_state:
            thread_id = st.session_state.thread_id

        async for token in stream_langgraph(
            [user_message],
            thread_id,
            st.session_state.chat_data.chat_id,
        ):
            content = token.get("content")
            if content:
                buffer += content
                placeholder.markdown(buffer)
            tool_calls = token.get("tool_calls")
            if tool_calls:
                for call in tool_calls:
                    call_id = call.get("id")
                    if call_id in tool_calls_rendered:
                        continue
                    tool_calls_rendered.add(call_id)
                    with tool_placeholder:
                        with st.expander(
                            f"Tool call: `{call['name']}`", expanded=False
                        ):
                            st.json(call["args"])
            st.session_state.messages.append({"role": "assistant", "content": buffer})

    run_async(consume())
