# import json

from agent.state.agent_state import AgentState


def weekly_analysis_node(state: AgentState) -> dict:
    sessions = state.get("sessions", [])

    if not sessions:
        return {"weekly_summary": {"error": "No sessions found"}}

    # with open("debug.json", "w") as f:
    #     json.dump(sessions, f, indent=2, default=str)
    # print("DEBUG - saved sessions to debug_sessions.json")

    # all variables
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    total_calories = 0
    workout_days = 0
    water_days = 0
    water_total = 0
    sleep_days = 0
    sleep_total = 0
    days_below_protein = []
    days_missing_workout = []
    days_missing_water = []
    days_missing_sleep = []

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

        total_protein += protein
        total_carbs += carbs
        total_fat += fat
        total_calories += calories

        # Workout
        workout = session.get("workout", {})
        workout_days = 0
        if workout.get("weight_training") or workout.get("cardio"):
            workout_days += 1
        else:
            days_missing_workout.append(date)

        # ======= OTHERS =========
        others = session.get("others", {})

        # Water
        if others.get("water", {}):
            water_days += 1
            water_total += others["water"].get("value", 0)
        else:
            days_missing_water.append(date)

        # Sleep
        if others.get("sleep"):
            sleep_days += 1
            sleep_total += others["sleep"].get("total_hours", 0)
        else:
            days_missing_sleep.append(date)

        # Track days below protein
        if protein < 90:
            days_below_protein.append(date)

    # Build summary
    num_days = len(sessions)
    summary = {
        "total_days": num_days,
        "avg_protein": total_protein / num_days,
        "avg_carbs": total_carbs / num_days,
        "avg_fat": total_fat / num_days,
        "avg_calories": total_calories / num_days,
        "workout_days": workout_days,
        "water_days": water_days,
        "avg_water": water_total / water_days if water_days > 0 else 0,
        "sleep_days": sleep_days,
        "avg_sleep": sleep_total / sleep_days if sleep_days > 0 else 0,
        "days_below_protein": days_below_protein,
        "days_missing_workout": days_missing_workout,
        "days_missing_water": days_missing_water,
        "days_missing_sleep": days_missing_sleep,
    }

    return {"weekly_summary": summary}
