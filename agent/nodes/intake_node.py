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
        # let respond_node handle this
        return result

    if convo_stage == "awaiting_workout_type":
        return result

    if convo_stage == "awaiting_exercise_details":
        return result

    if convo_stage == "awaiting_others_category":
        return result

    if convo_stage == "report_generation":
        return result

    result["conversation_stage"] = "awaiting_category"
    return result
