from agent.nodes.intake_node import intake_node
from agent.nodes.respond_node import respond_node
from langgraph.graph import END, START, StateGraph
from agent.state.agent_state import AgentState


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("intake", intake_node)
    builder.add_node("respond", respond_node)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "respond")
    builder.add_edge("respond", END)

    workflow = builder.compile()

    return workflow


graph = build_graph()
