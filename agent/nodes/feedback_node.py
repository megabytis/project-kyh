from agent.llm.llm_client import llm
from agent.state.agent_state import AgentState


def feedback_node(state: AgentState) -> dict:
    daily_totals = state.get("daily_totals", {})

    # Compare against targets
    TARGETS = {
        "protein": 110,  # g
        "carbs": 200,  # g
        "fat": 60,  # g
        "calories": 2000,  # cal
        "water": 4,  # liters
        "sleep": 7,  # hours
    }

    # for protein
    protein = ""
    if daily_totals["protein"] >= TARGETS["protein"]:
        protein.join("protein: ✅ hit target")
    elif daily_totals["protein"] < 90:
        protein.join("protein: ❌ low (under 90g)")
    else:
        protein.join("protein: ⚠️ close but short of 110g")

    # for carbs
    carbs = ""
    if daily_totals["carbs"] >= 150 and daily_totals["carbs"] <= TARGETS["carbs"]:
        carbs.join("carbs: ✅ good")
    elif daily_totals["carbs"] > TARGETS["carbs"]:
        carbs.join("carbs: ❌ high")
    else:
        carbs.join("carbs: ❌ low")

    # for fat
    fat = ""
    if daily_totals["fat"] <= TARGETS["fat"]:
        fat.join("fat: ✅ good")
    else:
        fat.join("❌ high")

    # for calories
    calories = ""
    if (
        daily_totals["calories"] >= 1500
        and daily_totals["calories"] <= TARGETS["calories"]
    ):
        calories.join("calories: ✅ good")
    elif daily_totals["calories"] > TARGETS["calories"]:
        calories.join("calories: ❌ too high")
    else:
        calories.join("calories: ❌ too low")

    # for water
    water = ""
    water_value = daily_totals.get("water", 0)
    if water_value is not None and water_value >= TARGETS["water"]:
        water.join("water: ✅ good")
    else:
        water.join("water: ❌ low")

    # for sleep
    sleep = ""
    sleep_value = daily_totals.get("sleep_hours", 0)
    if sleep_value is not None and sleep_value >= 6 and sleep_value <= TARGETS["sleep"]:
        sleep.join("sleep: ✅ good")
    elif sleep_value is not None and sleep_value > TARGETS["sleep"]:
        sleep.join("sleep: ⚠️ too much")
    else:
        sleep.join("sleep: ❌ too little")

    # Call LLM to generate feedback
    prompt = f"""
    Today's nutrition and lifestyle summary:
    - Protein: {daily_totals["protein"]}g (target {TARGETS["protein"]}g)
    - Carbs: {daily_totals["carbs"]}g (target {TARGETS["carbs"]}g)
    - Fat: {daily_totals["fat"]}g (target {TARGETS["fat"]}g)
    - Calories: {daily_totals["calories"]}cal (target {TARGETS["calories"]}cal)
    - Water: {daily_totals["water"]}L (target {TARGETS["water"]}L)
    - Sleep: {daily_totals["sleep_hours"]} hours (target {TARGETS["sleep"]} hours)

    Based on these numbers, give specific, actionable feedback for tomorrow.
    Keep it short and direct. Focus on the biggest gaps.
    No tables. No markdown. No bullet points. Just 2-3 short sentences.
    Return ONLY plain text. No JSON. No extra formatting.
    """
    response = llm.invoke(prompt)

    # Store in state["feedback"]
    state["feedback"] = response.content

    return state
