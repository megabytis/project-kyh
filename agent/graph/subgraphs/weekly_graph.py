# START → weekly_analysis_node → weekly_report_node → END

from langgraph.graph import END, START, StateGraph

from agent.nodes.weekly_analysis_node import weekly_analysis_node
from agent.nodes.weekly_report_node import weekly_report_node
from agent.state.agent_state import AgentState


def build_weekly_graph():
    builder = StateGraph(AgentState)

    builder.add_node("weekly_analysis", weekly_analysis_node)
    builder.add_node("weekly_report", weekly_report_node)

    builder.add_edge(START, "weekly_analysis")
    builder.add_edge("weekly_analysis", "weekly_report")
    builder.add_edge("weekly_report", END)

    workflow = builder.compile()

    return workflow


weekly_graph = build_weekly_graph()
