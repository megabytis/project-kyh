"""

weekly_analysis_node — Takes array of 7 sessions, extracts patterns.

What it extracts:

Average protein per day

Days with protein < 90g

Average carbs, fat, calories

How many workouts logged (cardio + weight training)

How many days water was logged and average intake

How many days sleep was logged and average hours

Recurring missing habits

"""

import json

from agent.state.agent_state import AgentState


def weekly_analysis_node(state: AgentState) -> dict:
    sessions = state.get("sessions", [])

    if not sessions:
        return {"weekly_summary": {"error": "No sessions found"}}

    # with open("debug.json", "w") as f:
    #     json.dump(sessions, f, indent=2, default=str)
    # print("DEBUG - saved sessions to debug_sessions.json")

    # Loop through sessions and extract patterns
    for session in sessions:
        # Date
        date = session.get("date")

        # Meals - sum macros from all meals
        meals = session.get("meals", {})
        macros = protein = carbs = fat = calories = 0
        for meal_type, meal_data in meals.items():
            macros = meal_data.get("macros", {})
            protein += macros.get("protein", 0)
            carbs += macros.get("carbs", 0)
            fat += macros.get("fat", 0)
            calories += macros.get("calories", 0)

        # Workout
        workout = session.get("workout", {})
        workout_days = 0
        if workout.get("weight_training") or workout.get("cardio"):
            workout_days += 1

        # ======= OTHERS =========
        others = session.get("others", {})

        # Water
        water_days = 0
        water_total = 0
        if others.get("water", {}):
            water_days += 1
            water_total += others["water"].get("value", 0)

        # Sleep
        sleep_days = 0
        sleep_total = 0
        if others.get("sleep"):
            sleep_days += 1
            sleep_total += others["sleep"].get("total_hours", 0)

        # Track days below protein
        days_below_protein = []
        if protein < 90:
            days_below_protein.append(date)

    # Build summary
    # return {"weekly_summary": sessions}
