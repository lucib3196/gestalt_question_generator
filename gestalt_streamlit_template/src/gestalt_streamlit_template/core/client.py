from langgraph_sdk import get_client
import streamlit as st

environment = st.secrets["ENV"]
if not environment:
    raise ValueError(f"Cannot initialize client. No environment set {environment}")

if environment == "local":
    url = st.secrets["LOCAL_URL"]
elif environment == "production":
    url = st.secrets["PRODUCTION_URL"]
else:
    raise ValueError(f"Cannot initialize client. Unknown environment set {environment}")

try:
    client = get_client(url=url, api_key=st.secrets["LANGSMITH_API_KEY"])
except Exception as e:
    raise ValueError(f"Cannot initialize client {e}")
