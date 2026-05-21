import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

import streamlit as st
import uuid
import json

from langchain_core.messages import HumanMessage, AIMessage
from agent.graph_builder import chatbot
from app.state.session import initialize_session
from app.ui import (
    render_sidebar,
    render_chat_interface
)

initialize_session()

render_sidebar()

render_chat_interface()
