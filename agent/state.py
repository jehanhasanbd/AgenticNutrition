from typing import TypedDict, Annotated, Dict, Any,List

from langgraph.graph.message import add_messages

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages = Annotated[list[BaseMessage], add_messages]

    # user-provided profile and constraints
    user_profile = Dict[str, Any]
    hard_constraints = List[str]

    # EHR / RAG
    ehr_json = Dict[str, Any]
    ehr_ready = bool
    ehr_context = str

    # tool context
    tool_context = Dict[str, Any]

    # final text
    final_answer = str