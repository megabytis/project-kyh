from agent.llm.llm_client import llm
from agent.state.agent_state import AgentState


def plan_node(state: AgentState) -> dict:
    daily_totals = state.get("daily_totals", {})
    feedback = state.get("feedback", "")

    prompt = f"""
    Based on today's gaps and feedback below, generate ONE sentence plan for tomorrow.

    Today's totals:
    Protein: {daily_totals["protein"]}g (target 110g)
    Carbs: {daily_totals["carbs"]}g (target 200g)
    Fat: {daily_totals["fat"]}g (target 60g)
    Calories: {daily_totals["calories"]}cal (target 2000cal)
    Water: {daily_totals["water"]}L (target 4L)
    Sleep: {daily_totals["sleep_hours"]} hours (target 7 hours)

    Feedback: {feedback}

    Plan: Return ONLY one sentence. No extra text.
    """

    response = llm.invoke(prompt)

    plan_text = response.content
    state["conversation_stage"] = "idle"

    return {
        "plan": plan_text,
        "bot_reply": f"""
        📊 Daily Summary:
        Protein: {daily_totals["protein"]}g, Carbs: {daily_totals["carbs"]}g, Fat: {daily_totals["fat"]}g, Calories: {daily_totals["calories"]}cal
        Workout Volume: {daily_totals["workout_volume"]}kg, Cardio: {daily_totals["cardio_duration"]}min
        Water: {daily_totals["water"]}L, Sleep: {daily_totals["sleep_hours"]}hrs

        💡 Feedback:
        {feedback}

        📅 Tomorrow's Plan:
        {plan_text}
        """,
        "conversation_stage": "idle",
    }
