from agent.state.agent_state import AgentState


def intake_node(state: AgentState) -> dict:
    # read user input & conversation_stage from state
    user_text = state["user_input"]
    convo_stage = state["conversation_stage"]
    logged_meals = state.get("logged_meals", [])

    result = {"bot_reply": ""}

    if convo_stage in ("idle", "awaiting_category"):
        mapping_user_input = {
            "food": "awaiting_meal_type",
            "workout": "awaiting_workout_type",
            "others": "awaiting_others_category",
            "report": "report_generation",
        }
        new_convo_stage = mapping_user_input.get(user_text, "awaiting_category")
        result["conversation_stage"] = new_convo_stage
        return result

    if convo_stage == "awaiting_meal_type":
        valid_meals = ("breakfast", "lunch", "dinner", "snacks")
        if user_text in valid_meals:
            if user_text in logged_meals:
                result["bot_reply"] = (
                    f"🌅 {user_text.capitalize()} already logged today!"
                )
                result["conversation_stage"] = "awaiting_category"
                return result

            result["chosen_meal"] = user_text
            result["conversation_stage"] = "awaiting_meal_items"
            return result

        result["conversation_stage"] = "awaiting_meal_type"
        return result

    if convo_stage == "awaiting_meal_items":
        return result

    if convo_stage == "awaiting_workout_type":
        # refinign user input
        valid_weight_training_keywords = (
            "weight training",
            "weights",
            "weight lifting",
        )
        valid_cardio_keywords = (
            "cardio",
            "running",
        )

        refined_user_text = ""

        if user_text in valid_weight_training_keywords:
            refined_user_text = "weight_training"
        if user_text in valid_cardio_keywords:
            refined_user_text = "cardio"

        # checking if workout already exists
        if state.get("workout", {}).get(refined_user_text):
            result["bot_reply"] = f"{refined_user_text} already logged today ✅."
            result["conversation_stage"] = "idle"
            return result

        if refined_user_text == "cardio" or refined_user_text == "weight_training":
            result["conversation_stage"] = "awaiting_exercise_details"
            result["chosen_workout_type"] = refined_user_text

            result["bot_reply"] = (
                "Describe your exercise (workout name : total duration)"
                if refined_user_text == "cardio"
                else "Describe your exercise (workout name : weight x reps, weight x reps, ... : total duration)"
            )

            return result

        return result

    if convo_stage == "awaiting_exercise_details":
        return result

    if convo_stage == "awaiting_others_category":
        # refinign user input
        valid_screen_time_keywords = ("screen time", "screen")
        valid_sleep_keywords = ("sleep", "sleep duration", "sleep timing")
        valid_water_keywords = (
            "water",
            "water intake",
            "water amount",
        )

        refined_user_text = ""

        if user_text in valid_screen_time_keywords:
            refined_user_text = "screen_time"
        if user_text in valid_sleep_keywords:
            refined_user_text = "sleep"
        if user_text in valid_water_keywords:
            refined_user_text = "water"

        if state.get("others", {}).get(refined_user_text):
            result["bot_reply"] = f"{refined_user_text} already logged today ✅."
            result["conversation_stage"] = "idle"
            return result

        if (
            refined_user_text == "screen_time"
            or refined_user_text == "sleep"
            or refined_user_text == "water"
        ):
            result["conversation_stage"] = "awaiting_other_details"
            result["chosen_others_type"] = refined_user_text

            if refined_user_text == "water":
                result["bot_reply"] = (
                    "How many glasses / bottle of water u have consumed total today ?"
                )
            if refined_user_text == "screen_time":
                result["bot_reply"] = "What's your today's total mobile screen time ?"

            if refined_user_text == "sleep":
                result["bot_reply"] = "How many hours u have slept today ?"

            return result

        return result

    if convo_stage == "awaiting_other_details":
        return result

    if convo_stage == "report_generation":
        return result

    result["conversation_stage"] = "awaiting_category"
    return result
