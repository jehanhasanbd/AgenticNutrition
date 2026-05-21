#
#
# def render_chat_interface():
#     pass
#
#
#
# def render_chat_history():
#     pass
# def handle_user_message():
#     pass
# def generate_ai_stream():
#     pass
# def build_graph_input():
#     pass

import streamlit as st

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
)

from agent.graph_builder import chatbot


def render_chat_interface():
    st.title("💬 Nutrition Agent Chatbot (RAG + Tools)")

    # ----------------------------- Show Chat History -----------------------------
    for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # ----------------------------- User Input -----------------------------
    user_input = st.chat_input(
        "Ask about meal plans, diet for diabetes/CKD/HTN, affordable foods, etc..."
    )

    if not user_input:
        return

    # Add user message to UI history
    st.session_state["message_history"].append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # ----------------------------- Graph Config -----------------------------
    config = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        }
    }

    # ----------------------------- Graph Input -----------------------------
    graph_input = {
        "messages": [
            HumanMessage(content=user_input)
        ],
        "user_profile": st.session_state["user_profile"],
        "ehr_json": st.session_state["ehr_json"],
        "ehr_ready": bool(
            st.session_state["ehr_json"]
        ),
        "hard_constraints": st.session_state[
            "hard_constraints"
        ],
        "ehr_context": "",
        "tool_context": {},
        "final_answer": "",
    }

    # ----------------------------- Assistant Response -----------------------------
    with st.chat_message("assistant"):

        def ai_only_stream():
            for chunk, meta in chatbot.stream(
                graph_input,
                config=config,
                stream_mode="messages",
            ):
                if isinstance(chunk, AIMessage):
                    yield chunk.content

        ai_text = st.write_stream(ai_only_stream())

    # Save assistant response
    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": ai_text,
        }
    )