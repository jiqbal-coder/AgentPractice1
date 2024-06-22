import streamlit as st
import os
from graph import salesCompAgent
import random


os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGSMITH_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']

DEBUGGING=0

def start_chat():
    st.title('Test Zoom Conflict Handler')
    avatars={"system":"💻🧠","user":"🧑‍💼","assistant":"🎓"}

    if "messages" not in st.session_state:
        st.session_state.messages = []

    #
    # Keeping context of conversations.
    # In practice, this will be say from the Slack - perhaps hash of user-id and channel-id.
    #
    if "thread-id" not in st.session_state:
        st.session_state.thread_id = random.randint(1000, 9999)
    thread_id = st.session_state.thread_id

    # Reminder
    st.sidebar.write("""
    Use cases:
    1. Student didnt join.
    2. Teacher cannot join session.
    3. Teacher needs to cancel existing session.
    4. ...
                      """)


    for message in st.session_state.messages:
        if message["role"] != "system":
            avatar=avatars[message["role"]]
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=avatars["user"]):
            st.markdown(prompt)
        abot=salesCompAgent(st.secrets['OPENAI_API_KEY'])
        thread={"configurable":{"thread_id":thread_id}}
        for s in abot.graph.stream({'initialMsg':prompt},thread):
            if DEBUGGING:
                print(f"GRAPH RUN: {s}")
                st.write(s)
            for k,v in s.items():
                if DEBUGGING:
                    print(f"Key: {k}, Value: {v}")
                if resp := v.get("responseToUser"):
                    with st.chat_message("assistant", avatar=avatars["assistant"]):
                        st.write(resp)
                    st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == '__main__':
    start_chat()
 