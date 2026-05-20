from langgraph.graph import StateGraph, START, END

from langgraph.checkpoint.memory import InMemorySaver

from agent.state import AgentState


from agent.nodes import (
    tool_context_node,
    rag_node,
    generate_answer_node
)



# -----------------------
# GRAPH
# -----------------------

def build_agent():
    graph = StateGraph(AgentState)

    graph.add_node("tool_context_node",tool_context_node)
    graph.add_node("rag_node",rag_node)
    graph.add_node("generate_answer_node",generate_answer_node)

    graph.add_edge(START,"tool_context_node")
    graph.add_edge("tool_context_node","rag_node")
    graph.add_edge("rag_node","generate_answer_node")
    graph.add_edge("generate_answer_node",END)

    checkpointer = InMemorySaver()
    return graph.compile(checkpointer=checkpointer)

chatbot = build_agent()