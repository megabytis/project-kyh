import uvicorn
from fastapi import FastAPI
from graph.graph import graph
from pydantic import BaseModel

app = FastAPI(title="KYH Agent")


# this is a pydantic class based on AgentState to validate the user input json body feilds
# it's exactly liek TypeScript : strict typechecking
class ProcessRequest(BaseModel):
    user_id: str
    date: str
    user_input: str
    conversation_stage: str
    chosen_meal: str = ""
    logged_meals: list = []
    meals: dict = {}
    workout: dict = {}
    chosen_workout_type: str = ""
    others: dict = {}
    chosen_others_type: str = ""
    daily_totals: dict = {}
    messages: list = []
    bot_reply: str = ""
    feedback: str = ""
    plan: str = ""
    weekly_report: str = ""


@app.post("/process")
async def process(req: ProcessRequest):
    state = req.model_dump()  # so here it is ensuring and checkign wheather our input feild data type matching with pydantic class feild's datatype or not, if yes then pass it else throw error, but witout this also we can directly pass our input dict to graph , but this is more SECURE.
    result = await graph.ainvoke(state)
    return result


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
