import streamlit as st
import requests

API_BASE = st.secrets.get("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="AI Support Chat", page_icon="💬")
st.title("AI Customer Support (Demo)")

if "session_id" not in st.session_state:
    st.session_state.session_id = None

query = st.text_input("Ask a question:", key="q")
if st.button("Send"):
    data = {"query": query, "session_id": st.session_state.session_id}
    resp = requests.post(f"{API_BASE}/ask", json=data).json()
    st.session_state.session_id = resp['session_id']
    st.write("**Bot:**", resp['reply'])
    st.write("_source:_", resp.get('source'), " score:", resp.get('score'))
    st.experimental_rerun()

if st.button("Show history"):
    if st.session_state.session_id:
        hist = requests.get(f"{API_BASE}/history/{st.session_state.session_id}").json()
        for h in hist:
            st.write("**User:**", h['user_query'])
            st.write("**Bot:**", h['bot_reply'])
            st.write("---")
    else:
        st.info("Start conversation first.")
