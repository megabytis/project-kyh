from agent.state.agent_state import AgentState
from langchain_core.messages import HumanMessage, SystemMessage, content
from agent.llm.llm_client import llm


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

        # if user has not entered anything like breakfast, lunch liek that , i.e. user have enter food names
        # now i have to call llm to calculate the macros
        prompt = [
            SystemMessage(
                content="You are a certified and experienced nutrition tracker. Parse the food items and estimate macros."
            ),
            HumanMessage(content=user_input),
        ]
        response = llm.invoke(prompt)
        reply = f"✅ {meal_type.capitalize()} logged!\n{response.content}"
        updated_response = messages + [response]

        # now marking meal as logged and will return the main user_input
        new_logged = list(state.get("logged_meals".[]))
        if meal_type not in new_logged:
            new_logged.append(meal_type)

        return {"bot_reply":"What would you like to do ?"}
