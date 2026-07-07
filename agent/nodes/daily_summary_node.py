from agent.state.agent_state import AgentState


def daily_summary_node(state: AgentState) -> dict:
    # =========== FOOD MACROS =========
    protein = carbs = fat = calories = 0

    # Extracting all macros from all meals
    meals = state.get("meals")
    for meal_data in meals.values():
        m = meal_data.get("macros", {})
        protein += m.get("protein", 0)
        carbs += m.get("carbs", 0)
        fat += m.get("fat", 0)
        calories += m.get("calories", 0)

    # ============ WEIGHT TRAINING TOTAL VOLUME =============
    workout_volume = 0

    weight_training = state.get("workout", {}).get("weight_training", [])
    for workout in weight_training:
        for s in workout.get("sets", []):
            weight = s.get("weight", 0)
            reps = s.get("reps", 0)
            workout_volume += weight * reps

    # ============= CARDIO TOTAL DURATION =================
    total_cardio_duration = 0

    cardio_list = state.get("workout", {}).get("cardio", [])
    for cardio in cardio_list:
        total_cardio_duration += cardio.get("duration", 0)

    # =========== OTHERS ============
    water_intake = state.get("others", {}).get("water", {}).get("value")
    sleep_hours = state.get("others", {}).get("sleep", {}).get("total_hours")

    daily_total = {
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "calories": calories,
        "workout_volume": workout_volume,
        "cardio_duration": total_cardio_duration,
        "water": water_intake,
        "sleep_hours": sleep_hours,
    }

    # now storing everything in dailytotal of state
    state["daily_totals"] = daily_total

    return state
