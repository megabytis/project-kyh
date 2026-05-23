# Project KYH — Know Your Habit
### AI Fitness Telegram Bot — Project Blueprint

---

## Tech Stack
- **Bot Interface**: Telegram (python-telegram-bot)
- **Agent Logic**: Python + LangGraph
- **Database**: MongoDB (pymongo — Python only until V4)
- **Backend API** (V4 only): Node.js + Express
- **Frontend** (V4 only): React / Next.js

---

## Version Breakdown

---

## V1 — The Brain (Pure LangGraph, No Telegram Yet)

> Goal: Learn LangGraph properly by building the core agent logic in isolation.

### What you build:
A standalone Python script (no bot, no DB yet) where you manually feed input and the agent processes it.

### Parts:

**1.1 — Project Setup**
- Create separate repo: `project-kyh`
- Setup virtual env inside `agent/`, install: `langgraph`, `langchain`, `langchain-openai` (or any LLM provider)
- Create folder structure as per the full project tree above (only `agent/` folder for now — `server/` and `client/` are V4)

**1.2 — Define State**
- Design your `AgentState` TypedDict
- Fields: `user_id`, `date`, `meals`, `workout`, `water_intake`, `analysis`, `suggestions`, `messages`
- LangGraph concept: **State**

**1.3 — Build Nodes**
- `intake_node` → parses raw user input into structured data
- `analysis_node` → calculates calories, macros, workout volume
- `feedback_node` → generates today's mistakes + improvements
- `planning_node` → generates next day plan
- LangGraph concept: **Nodes**

**1.4 — Connect with Edges**
- Linear flow first: intake → analysis → feedback → planning → END
- LangGraph concept: **Edges**

**1.5 — Add Conditional Routing**
- After intake, route: is this a meal log? workout log? water log? or a question?
- LangGraph concept: **Conditional Edges**

**1.6 — Test the Graph**
- Hardcode a sample day's input (meals, workout, water)
- Run the graph, see the output
- Tweak prompts in each node until output quality is good

### V1 Done = You understand State, Nodes, Edges, Conditional Routing

---

## V2 — Memory + Telegram (The Real Bot)

> Goal: Add persistence so agent remembers across days + wire to Telegram.

### Parts:

**2.1 — MongoDB Setup**
- Setup MongoDB Atlas (free tier)
- 4 collections based on your DB design (you already have this in your diary)
- Write basic CRUD functions as Python tools

**2.2 — LangGraph Tools**
- Convert your CRUD functions into LangGraph tools
- `save_meal_log_tool`, `save_workout_tool`, `fetch_history_tool`
- LangGraph concept: **Tool Calling**

**2.3 — Persistence / Memory**
- Add LangGraph checkpointer (MongoDB or SQLite based)
- Agent now remembers previous days per user
- LangGraph concept: **Persistence + Checkpointers**

**2.4 — Telegram Bot Setup**
- Setup bot via BotFather, get token
- Install `python-telegram-bot`
- Wire message handler → runs your LangGraph graph → sends response back

**2.5 — Conversation Flow**
- Bot asks questions one by one (breakfast? lunch? dinner? workout? water?)
- User replies naturally
- Agent stores, processes, responds with daily analysis

**2.6 — Daily Summary**
- After all logs received, agent sends:
  - Total calories + macros breakdown
  - Workout analysis (volume, muscles hit)
  - Today's mistakes in diet + workout
  - Tomorrow's plan

### V2 Done = Fully working Telegram bot with memory. This alone is portfolio-ready.

---

## V3 — Intelligence Layer (Pattern Recognition)

> Goal: Agent gets smarter over time by analyzing weekly/monthly patterns.

### Parts:

**3.1 — Weekly Analysis Node**
- Every Sunday, agent auto-triggers weekly summary
- Detects patterns: consistently low protein, skipping legs, poor hydration
- LangGraph concept: **Scheduled / triggered subgraphs**

**3.2 — Trend Detection Tools**
- `analyze_week_tool` → fetches last 7 days, finds trends
- `compare_to_goal_tool` → compares actual vs target macros over time

**3.3 — Adaptive Suggestions**
- Agent adjusts next week's plan based on patterns
- Not static suggestions — personalized based on YOUR history

### V3 Done = Agent that actually learns your patterns. Big differentiator.

---

## V4 — Dashboard (Web Frontend)

> Goal: Visual representation of all logged data.

### Parts:

**4.1 — Node.js API Layer**
- Express server exposing REST endpoints
- Auth via Telegram user ID (seamless, no separate login)
- Endpoints: `/logs`, `/weekly-summary`, `/macros`, `/workout-history`

**4.2 — React / Next.js Frontend**
- Login via Telegram widget (official Telegram login)
- Dashboard: macro breakdown charts, workout volume over time, water intake, weekly trends
- Calendar view: each day color-coded (green = good day, red = missed targets)

**4.3 — Telegram ↔ Web Sync**
- Same MongoDB, same user ID
- Log on Telegram, see it instantly on web dashboard

### V4 Done = Full product. Showcase-worthy publicly.

---

## LangGraph Concepts Coverage

| Concept | Covered In |
|---|---|
| State | V1.2 |
| Nodes | V1.3 |
| Edges | V1.4 |
| Conditional Routing | V1.5 |
| Tool Calling | V2.2 |
| Persistence / Checkpointers | V2.3 |
| Scheduled Triggers | V3.1 |
| Multi-node Reasoning | V1.3 + V3 |

---

## Rules While Building
1. Read docs / LangChain Academy first for each new concept
2. Build it yourself — no copy-paste from AI
3. Stuck on concept → read docs again, then ask for direction (not code)
4. Stuck on bug → debug yourself first 30 min, then ask
5. Ship each version before moving to next

---

## Full Project Folder Structure

```
project-kyh/
│
├── agent/                          # Everything Python / LangGraph
│   ├── graph/
│   │   ├── graph.py                # Main graph definition (nodes + edges wired here)
│   │   └── subgraphs/
│   │       └── weekly_graph.py     # Weekly analysis subgraph (V3)
│   │
│   ├── nodes/
│   │   ├── intake_node.py          # Parses raw user input into structured data
│   │   ├── analysis_node.py        # Calculates calories, macros, workout volume
│   │   ├── feedback_node.py        # Today's mistakes + improvement suggestions
│   │   ├── planning_node.py        # Next day plan generation
│   │   └── weekly_node.py          # Weekly pattern analysis (V3)
│   │
│   ├── state/
│   │   └── agent_state.py          # AgentState TypedDict definition
│   │
│   ├── tools/
│   │   ├── db_tools.py             # save_meal, save_workout, fetch_history tools
│   │   ├── analysis_tools.py       # analyze_week, compare_to_goal tools (V3)
│   │   └── notification_tools.py   # scheduled summary trigger tools (V3)
│   │
│   ├── db/
│   │   ├── mongo_client.py         # MongoDB connection
│   │   └── models/
│   │       ├── user.py             # User schema
│   │       ├── meal_log.py         # Meal log schema
│   │       ├── workout_log.py      # Workout log schema
│   │       └── daily_summary.py    # Daily summary schema
│   │
│   ├── bot/
│   │   ├── telegram_handler.py     # Telegram bot message handler
│   │   └── conversation_flow.py    # Conversation state machine (ask meal → workout → water)
│   │
│   ├── config/
│   │   └── settings.py             # Env vars, constants, LLM config
│   │
│   ├── main.py                     # Entry point — starts bot
│   ├── requirements.txt
│   └── .env
│
├── server/                         # Node.js API (V4 only)
│   ├── src/
│   │   ├── routes/
│   │   │   ├── logs.js
│   │   │   ├── summary.js
│   │   │   └── auth.js
│   │   ├── controllers/
│   │   ├── middleware/
│   │   └── db/
│   │       └── mongoose_models/
│   ├── app.js
│   ├── package.json
│   └── .env
│
├── client/                         # React / Next.js Frontend (V4 only)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.jsx           # Login / landing
│   │   │   └── dashboard.jsx       # Main dashboard
│   │   ├── components/
│   │   │   ├── MacroChart.jsx
│   │   │   ├── WorkoutVolume.jsx
│   │   │   ├── WaterTracker.jsx
│   │   │   └── CalendarView.jsx
│   │   └── services/
│   │       └── api.js              # API calls to Node server
│   ├── package.json
│   └── .env
│
├── .gitignore
└── README.md
```

---

**Start with V1.1. Nothing else.**
