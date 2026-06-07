from typing import List
from typing_extensions import TypedDict


class AgentState(TypedDict):
    # Identity
    user_id:str
    date:str

    # Raw inputs (what user logs)
    user_input: str
    meals:dict # where each dict have meal_type and foods feild , like this 4 dicts for four type of meals
    workout:dict
    others:dict # contains screen-time, water-intake, sleep-duration

    # Derived data from nodes
    daily_totals:dict # protein, carbs, fat, calories
    feedback:str # today's misatkes + improvements
    plan:str # tomorrow's plan
    messages:List[str] # conversation history



"""
### Data Structure : ###

user_id: ""
date: ""

meals: {
    breakfast: {
        foods: [...foods goes here],
        macros: {
            carb:x,
            protein:y
            fat:z
            total_calories:a
        }
    },
    lunch:{},
    supper:{},
    dinner:{}
}


workout: {
    weight_training: [
        {
            "workout_name":"bench press",
            "total_weight":"60kg",
            "sets":4,
            "reps":10,
            "res_between_sets":"2min"
        }
    ],
    cardio: [{}]
}

others: {
    "sleep_hours":7,
    "water_glass":10,
    "screen_time_in_minutes:120
}

daily_totals: {}
feedback: "" #
plan: ""
messages:[""]



"""
