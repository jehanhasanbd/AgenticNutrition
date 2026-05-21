import json

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage

from agent.state import AgentState
from agent.prompts.rag_prompt import RAG_PROMPT
from agent.llm import llm
from agent.safety.safety import basic_safety_scan, medical_disclaimer, enforce_dietary_constraints

def generate_answer_node(state: AgentState, config: RunnableConfig):
    """
        Produce final nutrition plan using prompt + tool context + RAG.
    """
    user_profile = state.get("user_profile", {}) or {}
    tool_context = state.get("tool_context", {}) or {}
    ehr_context = state.get("ehr_context", "") or ""
    hard_constraints = state.get("hard_constraints", []) or []

    # Latest user message
    user_message = ""
    for msg in reversed(state['messages']):
        if isinstance(msg, HumanMessage):
            user_message = msg.content
            break

    # Compose prompt
    rag_prompt = RAG_PROMPT.format(
        user_message=user_message,
        user_profile=json.dumps(user_profile, ensure_ascii=False, indent=2),
        tool_context=json.dumps(tool_context, ensure_ascii=False, indent=2),
        ehr_context=ehr_context,
        hard_constraints=json.dumps(hard_constraints, ensure_ascii=False),
    )

    # Use tool-enabled LLM (it can still call tools if needed later)
    response_ans = llm.invoke(rag_prompt)

    response_text = response_ans.content if hasattr(response_ans,"content") else str(response_ans)

    # Safety scan
    scanned_text = basic_safety_scan(response_text)
    if not scanned_text['ok']:
        safe_text = (
                "I can’t help with that request because it may be unsafe medically.\n\n"
                "If you want, tell me your condition and goals, and I’ll provide a safe meal plan "
                "within clinical dietary guidelines.\n\n"
                f"Flagged content: {scanned_text['hits']}\n\n"
                + medical_disclaimer()
        )

    # Constraint check (basic)
    constraint_check = enforce_dietary_constraints(response_text, hard_constraints=hard_constraints)
    if not constraint_check['ok']:
        response_text += (
                "\n\n⚠️ **Constraint warning:** I might have violated these constraints: "
                + ", ".join(constraint_check["violated"])
                + "\nPlease tell me which foods are strictly forbidden, and I will regenerate."
        )
    # Always add disclaimer
    if "Medical note" not in response_text and "Medical" not in response_text:
        response_text += "\n\n" + medical_disclaimer()

    return {"final_answer": response_text, "messages": [AIMessage(content=response_text)]}


