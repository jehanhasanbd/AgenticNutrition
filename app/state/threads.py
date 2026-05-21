import uuid
import streamlit as st
from agent.graph_builder import chatbot

def generate_thread_id():
    return str(uuid.uuid4())

def add_new_thread(thread_id: str):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id: str):
    state = chatbot.get_state(config={"configurable": {"thread_id":thread_id}})
    return state.values.get("messages",[])

def conversation_title(thread_id: str):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    messages = state.values.get("messages",[])
    for msg in messages:
        return (msg.content[:60] + " ...") if len(msg.content) > 60 else msg.content
    return "Current Conversation"

