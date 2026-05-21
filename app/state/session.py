import streamlit as st
import uuid

from app.state.threads import add_new_thread, generate_thread_id


def default_user_profile():
    return {
        "age": None,
        "sex": None,
        "height_cm": None,
        "weight_kg": None,
        "activity_level": "moderate",
        "dietary_pattern": "mixed",
        "culture_or_cuisine": "Bangladeshi",
        "country": "Bangladesh",
        "manual_location": "Dhaka",  # you can set None to use IP geo
        "hemisphere": "north",
        "budget_level": "medium",  # low/medium/high
    }

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_new_thread(thread_id)
    st.session_state["message_history"] = []
    st.session_state["ehr_json"] = {}
    st.session_state["user_profile"] = default_user_profile()
    st.session_state["hard_constraints"] = []


def initialize_session():
    if "message_history" not in st.session_state:
        st.session_state["message_history"] = []

    if "chat_threads" not in st.session_state:
        st.session_state["chat_threads"] = []

    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = generate_thread_id()

    if "ehr_json" not in st.session_state:
        st.session_state["ehr_json"] = {}

    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = default_user_profile()

    if "hard_constraints" not in st.session_state:
        st.session_state["hard_constraints"] = []

    add_new_thread(thread_id=st.session_state['thread_id'])