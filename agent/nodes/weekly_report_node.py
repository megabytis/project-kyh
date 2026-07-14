"""

weekly_report_node — Takes the extracted patterns, calls LLM.

Prompt:

text
"Here is your weekly fitness data:
- Average protein: Xg (target 110g) — below target on Y days
- Average carbs: Xg (target 200g) — above/below on Y days
- Workouts logged: X days out of 7
- Water logged: X days out of 7
- Sleep average: X hours

Generate a weekly report with:
1. What you did well
2. What needs improvement
3. Focus for next week

Keep it short and actionable."
Return: weekly_report (string)



"""

from agent.state.agent_state import AgentState


def weekly_report_node(state: AgentState) -> dict:
    pass
