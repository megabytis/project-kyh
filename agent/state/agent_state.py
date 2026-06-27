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

    # ---Logged Data---
    meals: Dict[str, Any]
    logged_meals: List[str]
    chosen_meal: str
    workout: Dict[str, Any]
    chosen_workout: str
    others: Dict[str, Any]

    # ---computed---
    daily_totals: Dict[str, Any]

    # ---output---
    feedback: str
    plan: str
    weekly_report: str


"""
        Example data for each field :
    
        user_id: "user_abc123"
        date: "2024-01-15"
    
        user_input: "3 eggs 2 roti"
        messages: [HumanMessage(...), AIMessage(...)]
    
        conversation_stage: "awaiting_meal_items"
        # Possible values: "idle" | "awaiting_category" | "awaiting_meal_type"
        # | "awaiting_meal_items" | "awaiting_workout_type"
        # | "awaiting_exercise_details" | "awaiting_others_category"
        # | "awaiting_sleep" | "awaiting_water" | "awaiting_screen_time"
        # | "report_generation"
    
        meals: {
            "breakfast": {
                "foods": [{"name": "eggs", "quantity": 3, "unit": "whole"}],
                "macros": {"protein": 24, "carbs": 30, "fat": 15, "calories": 350}
            }
        }
        logged_meals: ["breakfast", "lunch", "dinner"]
        chosen_meal: "breakfast"   # set temporarily when user picks a meal
    
        "workout": {
        "total_duration": 45,  # optional, user might not provide
        "cardio": [{"name": "treadmill", "duration": 15}],  # optional
        "weight_training": [
            {
                "exercise_name": "bench press",
                "sets": [
                    {"weight": 60, "reps": 10},
                    {"weight": 65, "reps": 8},
                    {"weight": 65, "reps": 7}
                ]
            }
        ]
}
    
        others: {
            "sleep": {"from": "23:00", "to": "06:00"},
            "water": 8,
            "screen_time": 120
        }
    
        daily_totals: {
            "protein": 95, "carbs": 200, "fat": 50, "calories": 1800,
            "workout_volume": 3300, "water_total": 8, "sleep_hours": 7
        }
    
        bot_reply: "✅ Breakfast logged!\n24g protein..."
    
        feedback: "5g short on protein target. Skip screen time before bed."
        plan: "Tomorrow: pull day. Start with 4 eggs breakfast."
        weekly_report: "Average 85g protein/week — consistently below 100g target."
"""
