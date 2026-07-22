# KYH Agent Service (Python / FastAPI / LangGraph)

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-Stateful%20Agents-FF6F61?style=for-the-badge&logo=langchain)
![DeepSeek](https://img.shields.io/badge/LLM-DeepSeek-blue?style=for-the-badge)

The **KYH Agent Service** is an autonomous AI microservice built with **Python**, **FastAPI**, and **LangGraph**. It serves as the core intelligence engine of the platform, responsible for understanding natural language inputs, parsing macronutrients from food descriptions, performing daily fitness analysis, providing actionable coaching feedback, and generating 7-day habit trend reports.

---

## 🎯 Key Responsibilities

1. **Natural Language Intake**: Classifies user messages (meal logging, exercise logging, sleep/water intake, general questions).
2. **Macronutrient & Exercise Extraction**: Extracts structured JSON data (calories, protein, carbs, fats, weights, reps, sets) from conversational text using DeepSeek LLM prompts.
3. **State Machine Execution**: Controls conversation flow and state transitions using LangGraph state graphs.
4. **Daily Performance Analysis**: Calculates daily nutritional totals, evaluates macro targets, flags workout deficits, and plans upcoming workouts.
5. **Weekly Pattern Analysis**: Processes 7-day session histories to detect recurring habits, recovery trends, and progress insights.

---

## 🛠️ Tech Stack

* **Framework**: FastAPI & Uvicorn
* **Agent Framework**: LangGraph & LangChain Core
* **LLM Engine**: DeepSeek API (`deepseek-v4-flash`) via OpenAI / LangChain OpenAI integration
* **Validation**: Pydantic v2 schemas
* **Database Driver**: PyMongo / Mongo Engine (if direct DB access is needed)

---

## 🔑 Environment Variables

The agent service requires the following environment variable:

| Variable | Required | Description | Example |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | **Yes** | API key for DeepSeek LLM service | `sk-xxxxxxxxxxxxxxxx` |
| `DEEPSEEK_BASE_URL` | Optional | Custom base API URL for DeepSeek | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | Optional | Target model name | `deepseek-v4-flash` |

---

## 🔄 LangGraph State Machine Architecture

The agent logic is structured into main state graphs using **LangGraph**:

```
                  ┌─────────────────┐
                  │   User Input    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   intake_node   │  (Keyword matching & intent routing)
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  respond_node   │  (LLM entity extraction & response generation)
                  └────────┬────────┘
                           │
             ┌─────────────┴─────────────┐
             │ Is logging finished?      │
             ▼                           ▼
    ┌───────────────────┐       ┌─────────────────┐
    │  summary_generated│=False │   Return State  │
    └────────┬──────────┘       └─────────────────┘
             │
             ▼
    ┌───────────────────┐
    │daily_summary_node │  (Calculates daily nutrient & workout totals)
    └────────┬──────────┘
             │
             ▼
    ┌───────────────────┐
    │   feedback_node   │  (Generates personalized fitness coaching tips)
    └────────┬──────────┘
             │
             ▼
    ┌───────────────────┐
    │     plan_node     │  (Recommends tomorrow's nutrition & exercise plan)
    └───────────────────┘
```

### Graph Nodes Explanation

| Node | Purpose & Functionality |
|---|---|
| `intake_node` | Performs intent classification and keyword routing based on current `conversation_stage` and user text. |
| `respond_node` | Invokes DeepSeek LLM to extract structured data (e.g. food items and macros) and forms conversational replies. |
| `daily_summary_node` | Aggregates all logged meals, workouts, and lifestyle entries for the day into total calories, protein, carbs, and fats. |
| `feedback_node` | Compares daily achievements against targets, identifies mistakes (e.g., low protein, skipped sleep), and outputs coaching feedback. |
| `plan_node` | Formulates actionable recommendations and muscle group workout suggestions for the next day. |
| `weekly_analysis_node` | Subgraph node that evaluates 7 consecutive sessions to compute weekly macro averages and pattern trends. |
| `weekly_report_node` | Subgraph node that generates a comprehensive, human-readable 7-day habit and progress report. |

---

## 📡 API Endpoints

### 1. Process Daily Conversation (`POST /process`)
* **Description**: Executes the main LangGraph state machine on an incoming session state payload.
* **Request Body** (`ProcessRequest` Pydantic model):
  ```json
  {
    "user_id": "123",
    "date": "2026-07-22",
    "user_input": "Logged lunch: 150g chicken breast and 1 cup rice",
    "conversation_stage": "meal_logged",
    "logged_meals": [],
    "messages": []
  }
  ```
* **Response**: Updated `AgentState` containing extracted macros, bot reply text, daily totals, feedback, and tomorrow's plan.

### 2. Analyze Weekly Sessions (`POST /analyze`)
* **Description**: Executes the weekly subgraph workflow over an array of 7 daily session objects to generate a habit report.
* **Request Body** (`AnalyzeRequest` Pydantic model):
  ```json
  {
    "sessions": [ /* Array of 7 daily session objects */ ]
  }
  ```
* **Response**: Object containing aggregated `weekly_summary` numbers and markdown-formatted `weekly_report`.

### 3. Health Check (`GET /health`)
* **Description**: Simple health probe endpoint.
* **Response**: `{"status": "ok"}`

---

## 📁 Directory Structure

```
agent/
├── server.py                   # FastAPI application & entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build instructions
├── state/
│   └── state.py                # TypedDict definition of AgentState
├── llm/
│   └── deepseek.py             # DeepSeek LLM client wrapper & prompt templates
├── nodes/
│   ├── intake.py               # Intake node logic
│   ├── respond.py              # Response & extraction node logic
│   ├── summary.py              # Daily summary calculation node
│   ├── feedback.py             # Feedback generation node
│   ├── plan.py                 # Next-day planning node
│   └── weekly.py               # Weekly analysis & report nodes
└── graph/
    ├── graph.py                # Main LangGraph definition and compilation
    └── subgraphs/
        └── weekly_graph.py     # Subgraph for multi-day weekly analysis
```

---

## 🚀 Running Locally

### 1. Create Virtual Environment & Install Dependencies
```bash
cd agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Set your DeepSeek API key:
```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
```

### 3. Start the FastAPI Server
```bash
python server.py
```
The server will start at `http://localhost:8000`. You can test endpoints via Swagger UI at `http://localhost:8000/docs`.

---

## 🐳 Running with Docker

Build and run standalone:
```bash
docker build -t kyh-agent .
docker run -p 8000:8000 -e DEEPSEEK_API_KEY="your_api_key" kyh-agent
```
