import os

import requests
import streamlit as st

st.set_page_config(page_title="Enterprise AI Agent", layout="wide")
st.title("Enterprise AI Knowledge & Workflow Agent")
st.caption("Supply Chain & Procurement Operations")

api_url = st.sidebar.text_input("Backend URL", os.getenv("API_URL", "http://localhost:8000"))
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Knowledge base")
    uploaded = st.file_uploader("Upload policy (.md/.txt)", type=["md", "txt"])
    if uploaded and st.button("Upload"):
        response = requests.post(f"{api_url}/documents/upload", files={"file": (uploaded.name, uploaded.getvalue())}, timeout=30)
        st.write(response.json())
    if st.button("Re-index documents"):
        response = requests.post(f"{api_url}/documents/index", timeout=120)
        st.write(response.json())

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("meta"):
            with st.expander("Evidence and tools"):
                st.json(message["meta"])

if prompt := st.chat_input("Ask about suppliers, policies, SLAs, quality or procurement operations"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    payload = {"message": prompt, "conversation_id": st.session_state.conversation_id}
    try:
        response = requests.post(f"{api_url}/chat", json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        st.session_state.conversation_id = data["conversation_id"]
        meta = {k: data.get(k) for k in ["route", "tools_used", "sources", "sql_query", "sql_result", "business_result"] if data.get(k)}
        st.session_state.messages.append({"role": "assistant", "content": data["answer"], "meta": meta})
        st.rerun()
    except requests.RequestException as exc:
        st.error(f"Backend request failed: {exc}")
