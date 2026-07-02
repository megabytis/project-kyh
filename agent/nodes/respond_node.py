from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm.llm_client import llm
from agent.state.agent_state import AgentState


def respond_node(state: AgentState) -> dict:
    convo_stage = state["conversation_stage"]
    messages = state.get("messages", [])
    bot_reply = state.get("bot_reply", "")

    # if intake node already set bot reaply, then use it first
    if bot_reply:
        updated_bot_reply = messages + [bot_reply]
        return {"messages": updated_bot_reply}

    # now stage specific reply by bot (no LLM now)
    stage_specific_replies = {
        "awaiting_meal_type": "Which meal? 🌅 Breakfast, ☀️ Lunch, 🌙 Dinner, 🍪Snacks",
        "awaiting_workout_type": "Cardio or 🏋️ Weight training?",
        "awaiting_others_category": "What to log? 😴 Sleep, 💧 Water, 📱 Screen time",
        "report_generation": "Report coming soon! keep logging daily.",
    }

    if convo_stage in stage_specific_replies:
        reply = stage_specific_replies[convo_stage]
        return {"bot_reply": reply}

    # now awaiting for meal items (parse food or ask for it)
    if convo_stage == "awaiting_meal_items":
        meal_type = state.get("chosen_meal", "meal")
        user_input = state["user_input"]

        if user_input in ("breakfast", "lunch", "dinner", "snacks"):
            return {"bot_reply": f"What did you eat for {meal_type}? 🍽️"}

        # if user has not entered anything like breakfast, lunch liek that , i.e. user have enter food names
        # now i have to call llm to calculate the macros
        prompt = [
            SystemMessage(
                content="You are a certified and experienced nutrition tracker. Parse the food items and estimate macros."
            ),
            HumanMessage(content=user_input),
        ]
        try:
            response = llm.invoke(prompt)
            reply = f"✅ {meal_type.capitalize()} logged!\n{response.content}"
            updated_response = messages + [response]
        except Exception as e:
            print(f"DeepSeek error: {e}")  # or logging
            reply = "Sorry, couldn't process that. Try again."

        # now marking meal as logged and will return the main user_input
        new_logged = list(state.get("logged_meals", []))
        if meal_type not in new_logged:
            new_logged.append(meal_type)

        meals_dict = state.get("meals", {})

        parsed_foods = []
        parsed_macros = {}

        meals_dict[meal_type] = {
            "foods": [],
            "macros": {},
            "raw_llm_response": response.content,
        }

        return {
            "meals": meals_dict,
            "logged_meals": new_logged,
            "bot_reply": reply,
            "conversation_stage": "idle",
            "messages": updated_response,
        }

    if convo_stage == "awaiting_exercise_details":
        user_input = state["user_input"]
        workout_type = state.get("chosen_workout_type")

        # Parsing with LLM
        prompt_content = """

        Parse the user given workout log into JSON.

        If workout_type is "cardio":
        - Parse into array of cardio exercises
        - Each exercise has "name" and "duration" (in minutes)
        - Example input: "treadmill 15 min, cycle 20"
        - Example output: [{"name":"treadmill","duration":15},{"name":"cycle","duration":20}]

        If workout_type is "weight_training":
        - Parse into array of exercises with sets
        - Each exercise has "exercise_name" and "sets" array
        - Each set has "weight" (in kg) and "reps"
        - Example input: "bench press: 60x10, 65x8 | squat: 100x5"
        - Example output: [{"exercise_name":"bench press","sets":[{"weight":60,"reps":10},{"weight":65,"reps":8}]},{"exercise_name":"squat","sets":[{"weight":100,"reps":5}]}]

        Return ONLY valid JSON. No explanations.
        """

        prompt = [
            SystemMessage(content=prompt_content),
            HumanMessage(content=user_input),
        ]

        try:
            response = llm.invoke(prompt)
            reply = f"✅ {workout_type} logged."
            updated_response = messages + [response]

        except Exception as e:
            print(f"DeepSeek error: {e}")
            reply = "Sorry, couldn't process that. Try again."

        workout_dict = state.get("workout", {})

        if workout_type == "weight_training" or workout_type == "cardio":
            workout_dict[workout_type] = response.content

        return {
            "workout": workout_dict,
            "bot_reply": reply,
            "conversation_stage": "idle",
            "messages": updated_response,
        }
