import uvicorn
from fastapi import FastAPI
from graph.graph import graph
from pydantic import BaseModel

app = FastAPI(title="KYH Agent")


class ProcessRequest(BaseModel):
    user_id: str
    date: str
    user_input: str
    conversation_stage: str
    chosen_meal: str = ""
    logged_meals: list = []
    meals: dict = {}
    workout: dict = {}
    others: dict = {}
    daily_totals: dict = {}
    messages: list = []
    bot_reply: str = ""
    feedback: str = ""
    plan: str = ""
    weekly_report: str = ""


@app.post("/process")
async def process(req: ProcessRequest):
    state = req.model_dump()
    result = await graph.ainvoke(state)
    return result


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
