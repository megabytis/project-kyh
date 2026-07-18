import json

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
        food_parsing_prompt = """
        You are a nutrition tracker. Parse the given food items and return ONLY valid JSON.

        Format:
        {
          "foods": [{"name": string, "quantity": number, "unit": string}],
          "macros": {"protein": number, "carbs": number, "fat": number, "calories": number}
        }

        Rules:
        - Estimate macros for each food item first
        - Sum them to get total macros
        - Include fiber if applicable (optional)

        Example input: "3 eggs, 2 roti"
        Example output: {"foods": [{"name":"eggs","quantity":3,"unit":"whole"},{"name":"roti","quantity":2,"unit":"pieces"}], "macros": {"protein":24,"carbs":30,"fat":15,"calories":350}}

        Return ONLY valid JSON. No explanations. No tables. No markdown.

        """
        prompt = [
            SystemMessage(content=food_parsing_prompt),
            HumanMessage(content=user_input),
        ]
        try:
            response = llm.invoke(prompt)
            updated_response = messages + [response]
        except Exception as e:
            print(f"DeepSeek error: {e}")
            return {
                "bot_reply": "Sorry, couldn't process that food. Please try again.",
                "conversation_stage": "awaiting_meal_items",
            }

        # now marking meal as logged and will return the main user_input
        new_logged = list(state.get("logged_meals", []))
        if meal_type not in new_logged:
            new_logged.append(meal_type)

        meals_dict = state.get("meals", {}) or {}

        try:
            content = response.content.strip()
            # Strip markdown fences if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = json.loads(content)
            parsed_foods = parsed.get("foods", [])
            parsed_macros = parsed.get("macros", {})
        except (json.JSONDecodeError, Exception) as e:
            print(f"Food JSON parse error: {e} | raw: {response.content!r}")
            return {
                "bot_reply": f"✅ {meal_type.capitalize()} logged! (macros could not be estimated)",
                "logged_meals": new_logged,
                "conversation_stage": "idle",
                "messages": updated_response,
            }

        meals_dict[meal_type] = {
            "foods": parsed_foods,
            "macros": parsed_macros,
        }

        reply = f"✅ {meal_type.capitalize()} logged!"

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

        Return ONLY valid JSON array. No explanations. No markdown.
        """

        prompt = [
            SystemMessage(content=prompt_content),
            HumanMessage(content=user_input),
        ]

        try:
            response = llm.invoke(prompt)
            updated_response = messages + [response]
        except Exception as e:
            print(f"DeepSeek error: {e}")
            return {
                "bot_reply": "Sorry, couldn't process that workout. Please try again.",
                "conversation_stage": "awaiting_exercise_details",
            }

        workout_dict = state.get("workout", {}) or {}

        try:
            content = response.content.strip()
            # Strip markdown fences if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Workout JSON parse error: {e} | raw: {response.content!r}")
            return {
                "bot_reply": "✅ Workout logged! (could not fully parse details)",
                "conversation_stage": "idle",
                "messages": updated_response,
            }

        if workout_type in ("weight_training", "cardio"):
            workout_dict[workout_type] = parsed

        return {
            "workout": workout_dict,
            "bot_reply": f"✅ {workout_type.replace('_', ' ').capitalize()} logged.",
            "conversation_stage": "idle",
            "messages": updated_response,
        }

    if convo_stage == "awaiting_other_details":
        user_input = state["user_input"]
        other_type = state["chosen_others_type"]

        others_parsing_prompt = f"""
        The user is logging: {other_type}
        Parse the user input and return ONLY valid JSON. No explanations.

        If type is "water":
        - Extract total glasses or liters
        - Example: "8 glasses" → {{"value": 8, "unit": "glasses"}}
        - Example: "2 liters" → {{"value": 2, "unit": "liters"}}

        If type is "screen_time":
        - Extract total minutes
        - Example: "2 hours" → {{"value": 120, "unit": "minutes"}}
        - Example: "120 min" → {{"value": 120, "unit": "minutes"}}

        If type is "sleep":
        - If user gives duration only (e.g. "6.5 hours", "7 hours") → {{"total_hours": 6.5}}
        - If user gives time range (e.g. "11pm to 6am") → {{"from": "23:00", "to": "06:00", "total_hours": 7}}

        Return ONLY valid JSON. No explanations.
        """

        prompt = [
            SystemMessage(content=others_parsing_prompt),
            HumanMessage(content=user_input),
        ]

        updated_response = messages

        try:
            response = llm.invoke(prompt)
            updated_response = messages + [response]
        except Exception as e:
            print(f"DeepSeek error: {e}")
            return {
                "bot_reply": "Sorry, couldn't process that. Please try again.",
                "conversation_stage": "awaiting_other_details",
            }

        others_dict = state.get("others", {}) or {}

        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed_others = json.loads(content)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Others JSON parse error: {e} | raw: {response.content!r}")
            return {
                "bot_reply": f"✅ {other_type.replace('_', ' ').capitalize()} logged! (details could not be parsed)",
                "conversation_stage": "idle",
                "messages": updated_response,
            }

        if other_type in ("sleep", "water", "screen_time"):
            others_dict[other_type] = parsed_others

        return {
            "others": others_dict,
            "bot_reply": f"✅ {other_type.replace('_', ' ').capitalize()} logged.",
            "conversation_stage": "idle",
            "messages": updated_response,
        }

    if convo_stage == "report_generation":
        return {}

