import json
import streamlit as st
from langchain_core.messages import HumanMessage
from app.state.session import (
    reset_chat,
    default_user_profile,
)
from app.state.threads import (
    load_conversation,
    conversation_title
)

# ----------------------------- Sidebar UI -----------------------------
def render_sidebar():
    st.sidebar.title("🥗 Personalized Nutrition AI Agent")

    # New chat
    if st.sidebar.button("➕ New Chat"):
        reset_chat()

    # ----------------------------- User Profile -----------------------------
    st.sidebar.header("User Profile")

    with st.sidebar.expander("Edit profile", expanded=True):
        prof = st.session_state.get(
            "user_profile",
            default_user_profile()
        )

        prof["age"] = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=prof["age"] or 0,
        )

        sex_options = ["unknown", "female", "male"]

        prof["sex"] = st.selectbox(
            "Sex",
            sex_options,
            index=sex_options.index(
                prof["sex"] or "unknown"
            ),
        )

        prof["height_cm"] = st.number_input(
            "Height (cm)",
            min_value=50,
            max_value=250,
            value=int(prof["height_cm"] or 165),
        )

        prof["weight_kg"] = st.number_input(
            "Weight (kg)",
            min_value=20,
            max_value=300,
            value=int(prof["weight_kg"] or 65),
        )

        activity_options = [
            "sedentary",
            "light",
            "moderate",
            "active",
        ]

        prof["activity_level"] = st.selectbox(
            "Activity level",
            activity_options,
            index=activity_options.index(
                prof.get("activity_level", "moderate")
            ),
        )

        diet_options = [
            "mixed",
            "vegetarian",
            "vegan",
            "halal",
            "keto",
            "low_carb",
        ]

        prof["dietary_pattern"] = st.selectbox(
            "Diet pattern",
            diet_options,
            index=diet_options.index(
                prof.get("dietary_pattern", "mixed")
            ),
        )

        prof["culture_or_cuisine"] = st.text_input(
            "Cuisine preference",
            value=prof.get(
                "culture_or_cuisine",
                "Bangladeshi",
            ),
        )

        prof["country"] = st.text_input(
            "Country",
            value=prof.get("country", "Bangladesh"),
        )

        prof["manual_location"] = st.text_input(
            "City/Location (optional)",
            value=prof.get("manual_location", "Dhaka"),
        )

        budget_options = ["low", "medium", "high"]

        prof["budget_level"] = st.selectbox(
            "Budget level",
            budget_options,
            index=budget_options.index(
                prof.get("budget_level", "medium")
            ),
        )

        st.session_state["user_profile"] = prof

    # ----------------------------- Constraints -----------------------------
    st.sidebar.header("Hard Constraints")

    constraints_text = st.sidebar.text_area(
        "Add constraints (one per line). Examples:\n"
        "- no alcohol\n"
        "- no grapefruit\n"
        "- low potassium\n"
        "- low sodium",
        value="\n".join(
            st.session_state["hard_constraints"]
        ),
        height=120,
    )

    st.session_state["hard_constraints"] = [
        c.strip()
        for c in constraints_text.splitlines()
        if c.strip()
    ]

    # ----------------------------- EHR Upload -----------------------------
    st.sidebar.header("EHR Upload (JSON)")

    ehr_file = st.sidebar.file_uploader(
        "Upload EHR JSON",
        type=["json"],
    )

    if ehr_file is not None:
        try:
            ehr_json = json.load(ehr_file)

            st.session_state["ehr_json"] = ehr_json

            st.sidebar.success("EHR loaded ✅")

        except Exception as e:
            st.sidebar.error(f"Invalid JSON: {e}")

    # ----------------------------- Conversations -----------------------------
    st.sidebar.header("My Conversations")

    for thread_id in st.session_state["chat_threads"][::-1]:
        title = conversation_title(thread_id)

        if st.sidebar.button(
            title,
            key=f"btn_{thread_id}",
        ):
            st.session_state["thread_id"] = thread_id

            msgs = load_conversation(thread_id)

            temp = []

            for msg in msgs:
                role = (
                    "user"
                    if isinstance(msg, HumanMessage)
                    else "assistant"
                )

                temp.append(
                    {
                        "role": role,
                        "content": msg.content,
                    }
                )

            st.session_state["message_history"] = temp