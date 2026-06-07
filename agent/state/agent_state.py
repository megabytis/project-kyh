from typing import Any, Dict, List

from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    # ---Identity---
    user_id: str
    date: str

    # ---From Telegram---
    user_input: str
    messages: List[BaseMessage]
    bot_reply: str

    # ---Conversation Flow---
    conversation_stage: str

    # "idle" | "awaiting_category" | "awaiting_meal_type" | "awaiting_meal_items" | "awaiting_workout_type" | "awaiting_exercise_details" | "awaiting_others_category" | "awaiting_sleep" | "awaiting_water" | "awaiting_screen_time" | "awaiting_correction" | "report_generation"

    # ---Logged Data---
    meals: Dict[str, Any]
    logged_meals: List[str]
    workout: Dict[str, Any]
    others: Dict[str, Any]

    # ---computed---
    daily_totals: Dict[str, Any]

    # ---output---
    feedback: str
    plan: str
    weekly_report: str
