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

from agent.llm.llm_client import llm
from agent.state.agent_state import AgentState


def weekly_report_node(state: AgentState) -> dict:
    weekly_summary = state.get("weekly_summary", {})
    weekly_report_generating_prompt = f"""

    Here is your weekly fitness data:
    - Total days analyzed: {weekly_summary.get("total_days", 0)}
    - Average protein: {weekly_summary.get("avg_protein", 0)}g (target 110g)
    - Average carbs: {weekly_summary.get("avg_carbs", 0)}g (target 200g)
    - Average fat: {weekly_summary.get("avg_fat", 0)}g (target 60g)
    - Average calories: {weekly_summary.get("avg_calories", 0)}cal (target 2000cal)
    - Workout logged on {weekly_summary.get("workout_days", 0)} days out of {weekly_summary.get("total_days", 0)}
    - Water logged on {weekly_summary.get("water_days", 0)} days (avg {weekly_summary.get("avg_water", 0)}L, target 4L)
    - Sleep logged on {weekly_summary.get("sleep_days", 0)} days (avg {weekly_summary.get("avg_sleep", 0)}hrs, target 7hrs)
    - Days below protein target: {weekly_summary.get("days_below_protein", 0)}
    - Days with no workout: {weekly_summary.get("days_missing_workout", 0)}
    - Days with no water: {weekly_summary.get("days_missing_water", 0)}
    - Days with no sleep: {weekly_summary.get("days_missing_sleep", 0)}

    Generate a weekly report:
    1. What you did well
    2. What needs improvement
    3. Focus for next week

    Keep it short and actionable. No tables. No markdown. Plain text.

    """
    response = llm.invoke(weekly_report_generating_prompt)
    state["weekly_report"] = response.content

    return {"weekly_report": response.content}
