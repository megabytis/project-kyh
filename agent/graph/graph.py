from langgraph.graph import END, START, StateGraph

from agent.nodes.daily_summary_node import daily_summary_node
from agent.nodes.feedback_node import feedback_node
from agent.nodes.intake_node import intake_node
from agent.nodes.plan_node import plan_node
from agent.nodes.respond_node import respond_node
from agent.state.agent_state import AgentState

# The below current flow is like: START → intake → respond → (if stage == "report_generation") → daily_summary → feedback → plan → END

def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("intake", intake_node)
    builder.add_node("respond", respond_node)
    builder.add_node("daily_summary", daily_summary_node)
    builder.add_node("feedback", feedback_node)
    builder.add_node("plan", plan_node)

    builder.add_edge(START, "intake")
    builder.add_edge("intake", "respond")
    builder.add_conditional_edges(
        "respond",
        lambda state: state.get("conversation_stage") == "report_generation",
        {True: "daily_summary", False: END},
    )
    builder.add_edge("daily_summary", "feedback")
    builder.add_edge("feedback", "plan")
    builder.add_edge("plan", END)

    workflow = builder.compile()

    return workflow


graph = build_graph()
