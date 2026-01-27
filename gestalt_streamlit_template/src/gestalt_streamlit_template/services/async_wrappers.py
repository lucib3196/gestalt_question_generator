import asyncio
import streamlit as st


# TODO: Improve this logic
def get_loop():
    if "event_loop" not in st.session_state:
        loop = asyncio.new_event_loop()
        st.session_state.event_loop = loop
    else:
        loop = st.session_state.event_loop
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            st.session_state.event_loop = loop

    asyncio.set_event_loop(loop)
    return loop


def run_async(coro):
    loop = get_loop()
    return loop.run_until_complete(coro)
