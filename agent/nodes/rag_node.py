from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage

from agent.state import AgentState
from agent.prompts.rag_prompt import RAG_PROMPT

from agent.rag import (

    build_ehr_vectorstore,
    retrieve_ehr_context
)


_VECTOR_STORE_CACHE: Dict[str,Any] = {}
# utils
def build_or_vector_store(thread_id: str, ehr_json: Dict[str, Any]):
    if thread_id not in _VECTOR_STORE_CACHE:
        _VECTOR_STORE_CACHE[thread_id] = build_or_vector_store(thread_id,ehr_json)
    return _VECTOR_STORE_CACHE[thread_id]
def rag_node(state: AgentState, config:RunnableConfig) -> Dict[str, Any]:
    thread_id = str(config.get("configurable", {}).get("thread_id", "default"))
    ehr_json = state.get("ehr_json", {}) or {}

    if not ehr_json:
        return {"ehr_context": "No EHR uploaded by the user."}

    # Use latest human message as query
    last_user = None
    for msg in reversed(state['messages']):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break
    query = last_user or "personalized nutrition recommendation"

    vector_store = build_or_vector_store(thread_id,ehr_json)
    docs = retrieve_ehr_context(
        vector_store=vector_store,
        query=query,
        k=6
    )
    ehr_context = "\n".join([f" - ({doc.metadata.get("type","ehr")}) {doc.page_content}" for doc in docs])
    return {"ehr_context": ehr_context}

