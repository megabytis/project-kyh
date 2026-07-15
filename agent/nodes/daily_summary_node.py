from agent.state.agent_state import AgentState


def daily_summary_node(state: AgentState) -> dict:
    # =========== FOOD MACROS =========
    protein = carbs = fat = calories = 0

    # Extracting all macros from all meals
    meals = state.get("meals") or {}
    for meal_data in meals.values():
        if meal_data:
            m = meal_data.get("macros") or {}
            protein += m.get("protein") or 0
            carbs += m.get("carbs") or 0
            fat += m.get("fat") or 0
            calories += m.get("calories") or 0

    # ============ WEIGHT TRAINING TOTAL VOLUME =============
    workout_volume = 0

    workout_data = state.get("workout") or {}
    weight_training = workout_data.get("weight_training") or []
    for workout in weight_training:
        if workout:
            for s in workout.get("sets") or []:
                weight = s.get("weight") or 0
                reps = s.get("reps") or 0
                workout_volume += weight * reps

    # ============= CARDIO TOTAL DURATION =================
    total_cardio_duration = 0

    cardio_list = workout_data.get("cardio") or []
    for cardio in cardio_list:
        if cardio:
            total_cardio_duration += cardio.get("duration") or 0

    # =========== OTHERS ============
    others_data = state.get("others") or {}
    water_data = others_data.get("water") or {}
    water_intake = water_data.get("value") if isinstance(water_data, dict) else water_data
    
    sleep_data = others_data.get("sleep") or {}
    sleep_hours = sleep_data.get("total_hours") if isinstance(sleep_data, dict) else None

    daily_totals = {
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
    state["daily_totals"] = daily_totals
    state["summary_generated"] = True

    return state
