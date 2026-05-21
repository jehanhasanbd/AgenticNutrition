import time
import uuid
from typing import Any, List, Dict
from langchain_core.messages import HumanMessage

from agent.graph_builder import chatbot

def now_ms() -> int:
    return int(time.time() * 1000)
def new_thread_id() -> str:
    return str(uuid.uuid4())

def run_agent_case(
        user_message: str,
        user_profile: Dict[str, Any],
        ehr_json: Dict[str, Any],
        hard_constraints: List[str]
    ) -> Dict[str, Any]:
    thread_id = new_thread_id()

    graph_input = {
        "messages": [HumanMessage(content=user_message)],
        "user_profile": user_profile,
        "ehr_json": ehr_json,
        "ehr_ready": bool(ehr_json),
        "hard_constraints": hard_constraints,
        "ehr_context": "",
        "tool_context": {},
        "final_answer": "",
    }

    t0 = now_ms()
    result = chatbot
    t1 = now_ms()

    return {
        "thread_id": thread_id,
        "latency_ms": t1 - t0,
        "answer": result.get("final_answer", "") or "",
        "ehr_context": result.get("ehr_context", "") or "",
        "tool_context": result.get("tool_context", {}) or {},
        "retrieved_ids": result.get("retrieved_ids", []) or [],
    }
