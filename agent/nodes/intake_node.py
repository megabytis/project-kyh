from langchain_core import runnables

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
        # checking if workout already exists
        if state.get("workout", {}).get("weight_training") or state.get(
            "workout", {}
        ).get("cardio"):
            result["bot_reply"] = "Wokrout already logged today ✅."
            result["conversation_stage"] = "idle"
            return result

        valid_weight_training_keywords = ("weight training", "weights")
        valid_cardio_keywords = ("cardio", "running")



        if (
            user_text.lower() in valid_cardio_keywords
            or user_text.lower() in valid_weight_training_keywords
        ):
            result["conversation_stage"] = "awaiting_exercise_details"

            if user_text.lower() == "weight training" or user_text.lower() == "weights":
                result["chosen_workout_type"] = "weight_training"
                result["bot_reply"] = (
                    "Describe your exercise (workout name : weight x reps, weight x reps, ... : total duration)"
                )
            if user_text.lower() == "cardio" or user_text.lower() == "running":
                result["chosen_workout_type"] = "cardio"
                result["bot_reply"] = (
                    "Describe your exercise (workout name : total duration)"
                )

            return result

        return result

    if convo_stage == "awaiting_exercise_details":
        return result

    if convo_stage == "awaiting_others_category":
        return result

    if convo_stage == "report_generation":
        return result

    result["conversation_stage"] = "awaiting_category"
    return result
