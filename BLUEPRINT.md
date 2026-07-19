# Project KYH — Know Your Habit
## Build Blueprint (Node.js + Python Dual Service)

---

**Author:** 2nd year BCA student, Bhubaneswar
**Stack:**
- **Frontend:** HTML/CSS/JS (later React)
- **Backend:** Node.js + Express (API layer, sessions, cron)
- **Agent:** Python + FastAPI + LangGraph (AI logic)
- **LLM:** DeepSeek V3 (direct API)
- **DB:** MongoDB + Mongoose (Node) + PyMongo (Python)
**Time:** ~5 hours per weekend

**Goal:** AI fitness web app — log meals, workouts, sleep, water via chat.
Remembers patterns, coaches you, runs 24/7. Portfolio piece showing both
JavaScript API skills and Python AI skills.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Folder Structure](#2-folder-structure)
3. [Weekend 1 — Fix AgentState + Keyword Matching + Wire Services](#3-weekend-1)
4. [Weekend 2 — Store Meals + LLM Macro Parsing + MongoDB](#4-weekend-2)
5. [Weekend 3 — Workout + Sleep + Water](#5-weekend-3)
6. [Weekend 4 — Daily Summary + Feedback](#6-weekend-4)
7. [Weekend 5 — Weekly Reports & Patterns](#7-weekend-5)
8. [Weekend 6 — Frontend UI Polish](#8-weekend-6)
9. [Weekend 7 — Reminders + Deploy](#9-weekend-7)
10. [MongoDB Schemas](#10-mongodb-schemas)
11. [API Reference](#11-api-reference)
12. [Stage Map](#12-stage-map)
13. [Golden Rules](#13-golden-rules)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────┐
│              BROWSER                          │
│  HTML/CSS/JS at localhost:3000                │
│  User types → fetch() to Express             │
└──────────────────┬──────────────────────────┘
                   │ POST /api/chat
                   ▼
┌─────────────────────────────────────────────┐
│    NODE.JS EXPRESS (backend/)                │
│    Port 3000                                 │
│                                              │
│  Routes:                                     │
│    POST /api/chat      → chatController      │
│    GET  /api/session   → sessionController   │
│    GET  /api/report/*  → reportController    │
│                                              │
│  Each controller:                            │
│    1. Load/save session in MongoDB           │
│    2. Call Python FastAPI via axios          │
│    3. Return JSON to browser                 │
│                                              │
│  Cron: 10:30 PM via node-cron                │
└──────────────────┬──────────────────────────┘
                   │ axios POST /process
                   ▼
┌─────────────────────────────────────────────┐
│    PYTHON FASTAPI (agent/)                   │
│    Port 8000                                 │
│                                              │
│  POST /process                               │
│    → receives full state dict                │
│    → graph.ainvoke(state)                    │
│    → returns updated state                   │
│                                              │
│  POST /analyze (Weekend 5)                   │
│    → runs weekly_graph subgraph              │
│    → returns pattern report                  │
│                                              │
│  ONLY LangGraph. No web serving.             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│    MONGODB ATLAS                             │
│  Collections:                                │
│  sessions         ← Active conversation state│
│  meal_logs        ← Permanent meal records   │
│  workout_logs     ← Permanent workout records│
│  weight_training_logs ← Individual exercises │
│  others_logs      ← Sleep/water/screen       │
└─────────────────────────────────────────────┘
```

### Data flow (one message):

```
1. User types "food" in browser
2. Browser fetch() → POST /api/chat { userId, message: "food" }
3. Express routes to chatController
4. chatController loads session from MongoDB (or creates new)
5. Sets state["user_input"] = "food"
6. axios.post(FASTAPI_URL + "/process", state)
7. FastAPI runs graph.ainvoke(state)
   → intake_node: keyword match food → stage = "awaiting_meal_type"
   → respond_node: no LLM → "Which meal?"
8. FastAPI returns updated state to Express
9. chatController saves state to MongoDB
10. Returns { reply: "Which meal?", stage: "awaiting_meal_type" } to browser
11. Browser displays reply in chat
```

### What each service owns:

| Service | Owns | Does NOT own |
|---------|------|-------------|
| **Node Express** | User sessions, MongoDB CRUD, HTTP routing, cron jobs, serving frontend | LangGraph logic, LLM calls, stage transitions |
| **Python FastAPI** | LangGraph agent, LLM calls, macro parsing, feedback generation | Web serving, sessions, MongoDB CRUD |
| **MongoDB** | All persistence | Application logic |

---

## 2. Folder Structure

```
project-kyh/
├── backend/                          ← Node.js Express (YOUR PORTFOLIO FOLDER)
│   ├── server.js                     ← Entry point (app setup + listen)
│   ├── routes/
│   │   ├── chat.js                   ← POST /api/chat
│   │   ├── session.js                ← GET /api/session
│   │   └── report.js                 ← GET /api/report/daily, /weekly
│   ├── controllers/
│   │   ├── chatController.js         ← Calls FastAPI, manages state
│   │   ├── sessionController.js      ← Init/load user session
│   │   └── reportController.js       ← Aggregates from MongoDB
│   ├── db/
│   │   └── mongo.js                  ← Mongoose connection
│   ├── models/
│   │   ├── Session.js                ← User session state schema
│   │   ├── MealLog.js
│   │   ├── WorkoutLog.js
│   │   ├── WeightTrainingLog.js
│   │   └── OthersLog.js
│   ├── package.json
│   └── .env
│
├── agent/                            ← Python FastAPI + LangGraph
│   ├── server.py                     ← FastAPI app (POST /process, /analyze)
│   ├── state/
│   │   └── agent_state.py            ← AgentState TypedDict
│   ├── graph/
│   │   ├── graph.py                  ← LangGraph definition
│   │   └── subgraphs/
│   │       └── weekly_graph.py       ← Weekend 5
│   ├── nodes/
│   │   ├── intake_node.py            ← Keyword matching + stage routing
│   │   ├── respond_node.py           ← Stage replies + LLM macros
│   │   ├── daily_summary_node.py     ← Weekend 4
│   │   ├── feedback_node.py          ← Weekend 4
│   │   └── plan_node.py              ← Weekend 4
│   ├── llm/
│   │   └── llm_client.py             ← DeepSeek connection
│   ├── config/
│   │   └── settings.py               ← Env vars
│   ├── requirements.txt
│   └── .env
│
├── client/                           ← Frontend (Weekend 6+)
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── BLUEPRINT.md
├── BLUEPRINT-telegram-backup.md
└── README.md
```

---

## 3. Weekend 1 — Fix AgentState + Keyword Matching + Wire Services

### Goal
User types "food" in browser → Express → FastAPI → graph → "Which meal?" back.
No LLM. All three services talking to each other.

### What you build (8 files total)

### 3.1 Add chosen_meal to AgentState

**File:** `agent/state/agent_state.py`

Add one line after `logged_meals`:

```python
chosen_meal: str     # "breakfast" | "lunch" | "dinner" | "snacks" | ""
```

### 3.2 Rewrite intake_node (Python)

**File:** `agent/nodes/intake_node.py`

Purpose: Read `conversation_stage`, match keywords using if-elif, update stage.
Every return must set `bot_reply` (even empty string) and `conversation_stage`.

```
If stage is "idle" or "awaiting_category":
    Match "food" → set stage = "awaiting_meal_type"
    Match "workout" → set stage = "awaiting_workout_type"
    Match "others" → set stage = "awaiting_others_category"
    Match "report" → set stage = "report_generation"
    No match → stay in same stage

If stage is "awaiting_meal_type":
    Match "breakfast" | "lunch" | "dinner" | "snacks"
    If in logged_meals → reply "Already logged" + set stage = "idle"
    Else → set chosen_meal, stage = "awaiting_meal_items"

All other stages: return result (bot_reply="") → let respond_node handle
```

### 3.3 Rewrite respond_node (Python)

**File:** `agent/nodes/respond_node.py`

```
If intake_node already set bot_reply → return it directly (no LLM)

Stage-based hardcoded replies (no LLM):
    "awaiting_meal_type" → "Which meal? (breakfast / lunch / dinner / snacks)"
    "awaiting_workout_type" → "Cardio or weight training?"
    "awaiting_others_category" → "Sleep, water, or screen time?"
    "idle" → "What would you like to do?"

Special — "awaiting_meal_items":
    If user_input is a single meal keyword → "What did you eat for {meal_type}?" (no LLM)
    Else → Call DeepSeek for macro parsing → Store in state → Reset stage to idle
```

### 3.4 Create FastAPI server (Python)

**File:** `agent/server.py`

Single-purpose: receive state, run graph, return state.

```python
from fastapi import FastAPI
from pydantic import BaseModel
from graph.graph import graph

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
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.5 Create Express entry point (Node.js)

**File:** `backend/server.js`

```javascript
const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
require('dotenv').config();

const app = express();
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/chat', require('./routes/chat'));
app.use('/api/session', require('./routes/session'));
app.use('/api/report', require('./routes/report'));

const PORT = process.env.PORT || 3000;
mongoose.connect(process.env.MONGO_URI)
  .then(() => {
    app.listen(PORT, () => console.log(`✅ Backend running on port ${PORT}`));
  })
  .catch(err => console.error('MongoDB connection error:', err));
```

### 3.6 Create Session model (Node.js)

**File:** `backend/models/Session.js`

```javascript
const mongoose = require('mongoose');

const sessionSchema = new mongoose.Schema({
  userId: { type: String, required: true },
  date: { type: String, required: true },
  conversationStage: { type: String, default: 'idle' },
  chosenMeal: { type: String, default: '' },
  loggedMeals: { type: [String], default: [] },
  meals: { type: mongoose.Schema.Types.Mixed, default: {} },
  workout: { type: mongoose.Schema.Types.Mixed, default: {} },
  others: { type: mongoose.Schema.Types.Mixed, default: {} },
  dailyTotals: { type: mongoose.Schema.Types.Mixed, default: {} },
  messages: { type: [Object], default: [] },
  botReply: { type: String, default: '' },
  feedback: { type: String, default: '' },
  plan: { type: String, default: '' }
}, { timestamps: true });

// Compound index: one session per user per day
sessionSchema.index({ userId: 1, date: 1 }, { unique: true });

module.exports = mongoose.model('Session', sessionSchema);
```

### 3.7 Create chat controller (Node.js)

**File:** `backend/controllers/chatController.js`

```javascript
const axios = require('axios');
const Session = require('../models/Session');

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

exports.handleChat = async (req, res) => {
  try {
    const { userId, message } = req.body;
    if (!userId || !message) {
      return res.status(400).json({ reply: 'userId and message required', stage: 'idle' });
    }

    const today = new Date().toISOString().split('T')[0];

    // 1. Load or create session
    let session = await Session.findOne({ userId, date: today });
    if (!session) {
      session = new Session({ userId, date: today, conversationStage: 'awaiting_category' });
    }

    // 2. Update with current message
    const state = session.toObject();
    state.user_input = message;
    delete state._id;
    delete state.__v;
    delete state.updatedAt;
    delete state.createdAt;

    // 3. Send to FastAPI
    const response = await axios.post(`${FASTAPI_URL}/process`, state, {
      timeout: 30000
    });
    const result = response.data;

    // 4. Save updated state to MongoDB
    Object.assign(session, {
      conversationStage: result.conversation_stage || result.conversationStage || 'idle',
      chosenMeal: result.chosen_meal || result.chosenMeal || '',
      loggedMeals: result.logged_meals || result.loggedMeals || [],
      meals: result.meals || {},
      workout: result.workout || {},
      others: result.others || {},
      dailyTotals: result.daily_totals || result.dailyTotals || {},
      botReply: result.bot_reply || result.botReply || '',
      messages: result.messages || []
    });
    await session.save();

    // 5. Return to browser
    res.json({
      reply: session.botReply,
      stage: session.conversationStage
    });

  } catch (error) {
    console.error('Chat error:', error.message);
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json({
        reply: 'Agent service is offline. Start the Python FastAPI server.',
        stage: 'idle'
      });
    }
    res.status(500).json({
      reply: 'Something went wrong. Please try again.',
      stage: 'idle'
    });
  }
};
```

### 3.8 Create session controller (Node.js)

**File:** `backend/controllers/sessionController.js`

```javascript
const Session = require('../models/Session');

exports.initSession = async (req, res) => {
  try {
    const { userId } = req.query;
    if (!userId) return res.status(400).json({ error: 'userId required' });

    const today = new Date().toISOString().split('T')[0];

    let session = await Session.findOne({ userId, date: today });
    if (!session) {
      session = new Session({
        userId,
        date: today,
        conversationStage: 'awaiting_category'
      });
      await session.save();
    }

    res.json({
      sessionId: session._id,
      stage: session.conversationStage,
      loggedMeals: session.loggedMeals
    });
  } catch (error) {
    console.error('Session init error:', error.message);
    res.status(500).json({ error: 'Failed to initialize session' });
  }
};
```

### 3.9 Create chat route (Node.js)

**File:** `backend/routes/chat.js`

```javascript
const express = require('express');
const router = express.Router();
const { handleChat } = require('../controllers/chatController');

router.post('/', handleChat);

module.exports = router;
```

### 3.10 Create session route (Node.js)

**File:** `backend/routes/session.js`

```javascript
const express = require('express');
const router = express.Router();
const { initSession } = require('../controllers/sessionController');

router.get('/', initSession);

module.exports = router;
```

### 3.11 Create MongoDB connection (Node.js)

**File:** `backend/db/mongo.js`

```javascript
const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI);
    console.log('✅ MongoDB connected');
  } catch (err) {
    console.error('MongoDB connection error:', err.message);
    process.exit(1);
  }
};

module.exports = connectDB;
```

### 3.12 Test with Postman (not browser yet)

Before writing a single line of frontend code, test the entire pipeline with Postman:

**Step 1:** Start Python FastAPI
```bash
cd agent
pip install -r requirements.txt
python server.py
# → FastAPI running on http://localhost:8000
```

**Step 2:** Start Node Express
```bash
cd backend
npm install
node server.js
# → Backend running on http://localhost:3000
```

**Step 3:** Test with Postman

**Request 1 — Init session:**
```
GET http://localhost:3000/api/session?userId=test1
```
Expected: `{ "sessionId": "...", "stage": "awaiting_category", "loggedMeals": [] }`

**Request 2 — Send "food":**
```
POST http://localhost:3000/api/chat
Body (JSON): { "userId": "test1", "message": "food" }
```
Expected: `{ "reply": "Which meal? (breakfast / lunch / dinner / snacks)", "stage": "awaiting_meal_type" }`

**Request 3 — Send "breakfast":**
```
POST http://localhost:3000/api/chat
Body: { "userId": "test1", "message": "breakfast" }
```
Expected: `{ "reply": "What did you eat for breakfast?", "stage": "awaiting_meal_items" }`

**Request 4 — Send "3 eggs 2 roti":**
```
POST http://localhost:3000/api/chat
Body: { "userId": "test1", "message": "3 eggs 2 roti" }
```
Expected: `{ "reply": "✅ Breakfast logged!\n24g protein...", "stage": "idle" }`

**Request 5 — Verify duplicate detection:**
```
POST http://localhost:3000/api/chat
Body: { "userId": "test1", "message": "breakfast" }
```
Expected: `{ "reply": "Breakfast already logged today ✅", "stage": "idle" }`

**Request 6 — Verify random text doesn't trigger LLM:**
```
POST http://localhost:3000/api/chat
Body: { "userId": "test1", "message": "hi" }
```
Expected: `{ "reply": "What would you like to do?", "stage": "idle" }`

**Request 7 — Verify offline agent handling:**
Stop the Python FastAPI server, then send another request.
Expected: `{ "reply": "Agent service is offline. Start the Python FastAPI server.", "stage": "idle" }`

If ALL 7 requests pass, Weekend 1 is done. You have a working backend.
Only then, create `client/index.html` and wire the frontend.

---

## 4. Weekend 2 — Store Meals + LLM Macro Parsing

### Goal
User logs "3 eggs 2 roti" → DeepSeek calculates macros → stored in MongoDB.
Duplicate meal detection works. User can log multiple meals in one session.

### What to build

### 4.1 Store meal data in respond_node (Python)

After LLM parses food, store in state and add to logged list:

```python
# In respond_node, when stage == "awaiting_meal_items" and it's actual food:
meals = dict(state.get("meals", {}))
meals[meal_type] = {
    "foods": parsed_foods,      # [{"name": "eggs", "quantity": 3, ...}]
    "macros": parsed_macros     # {"protein": 24, "carbs": 30, ...}
}
logged = list(state.get("logged_meals", []))
if meal_type not in logged:
    logged.append(meal_type)

return {
    "meals": meals,
    "logged_meals": logged,
    "bot_reply": f"✅ {meal_type.capitalize()} logged!\n{macro_text}",
    "conversation_stage": "idle"
}
```

### 4.2 Nothing changes in Express

The chatController already saves the full state to MongoDB. Meals and logged_meals
persist automatically with no Express changes needed.

### Weekend 2 Success Check (Postman)

```
POST /api/chat { message: "food" }
→ "Which meal?"

POST /api/chat { message: "breakfast" }
→ "What did you eat for breakfast?"

POST /api/chat { message: "3 eggs 2 roti" }
→ "✅ Breakfast logged!\n24g protein, 30g carbs, 15g fat, 350 cal"

POST /api/chat { message: "food" }
→ "Which meal?"

POST /api/chat { message: "lunch" }
→ "What did you eat for lunch?"

POST /api/chat { message: "200g chicken rice" }
→ "✅ Lunch logged!\n46g protein, 60g carbs, 8g fat, 500 cal"

POST /api/chat { message: "breakfast" }
→ "Breakfast already logged today ✅"

Check MongoDB → sessions collection has all meals stored
```

---

## 5. Weekend 3 — Workout + Sleep + Water

### Goal
Bot handles all 4 input types: food, workout, others. User can log an entire day.

### What to build

### 5.1 Add workout stages in intake_node (Python)

```python
if stage == "awaiting_workout_type":
    if user_text in ("weight training", "cardio", "weights", "running"):
        result["conversation_stage"] = "awaiting_exercise_details"
        result["bot_reply"] = "Describe your exercise (format: name | sets × reps @ weight)"
        return result

if stage == "awaiting_exercise_details":
    if user_text.lower() == "done":
        result["bot_reply"] = "💪 Workout complete!"
        result["conversation_stage"] = "idle"
        return result
    # Pass to respond_node for LLM parsing
    return result
```

### 5.2 Add others stages in intake_node (Python)

```python
if stage == "awaiting_others_category":
    if user_text in ("sleep", "water", "screen time", "screen"):
        stage_map = {
            "sleep": "awaiting_sleep",
            "water": "awaiting_water",
            "screen time": "awaiting_screen_time",
            "screen": "awaiting_screen_time"
        }
        result["conversation_stage"] = stage_map.get(user_text, "awaiting_others_category")
        return result
```

### Weekend 3 Success Check (Postman)

```
POST /api/chat { message: "workout" }
→ "Cardio or weight training?"

POST /api/chat { message: "weight training" }
→ "Describe your exercise..."

POST /api/chat { message: "bench press | 4 × 10 @ 60kg" }
→ "✅ Logged: bench press — 4 × 10 @ 60kg (2400kg volume)"

POST /api/chat { message: "done" }
→ "💪 Workout complete!"

POST /api/chat { message: "others" }
→ "Sleep, water, or screen time?"

POST /api/chat { message: "water" }
→ "How many glasses?"

POST /api/chat { message: "8" }
→ "✅ 8 glasses logged"
```

---

## 6. Weekend 4 — Daily Summary + Feedback

### Goal
After dinner logged, auto-generate daily summary + improvement tips + tomorrow plan.

### New Python nodes

**daily_summary_node.py** — Calculate totals from state:
- Sum protein/carbs/fat/calories across all meals
- Sum workout volume across all exercises
- Total sleep hours, water intake
- Store in `state["daily_totals"]`

**feedback_node.py** — Call DeepSeek:
```
"Today: 85g protein, 200g carbs, 1800 cal.
 Targets: 100g protein, 2000 cal.
 What did I do wrong? Give specific tips."
```

**plan_node.py** — Call DeepSeek:
```
"Today's gaps: low protein, skipped water.
 Generate 1-sentence plan for tomorrow."
```

### Add to graph.py

```python
graph.add_conditional_edges("respond", should_auto_summary, {
    True: "daily_summary",
    False: END
})
graph.add_edge("daily_summary", "feedback")
graph.add_edge("feedback", "plan")
graph.add_edge("plan", END)

def should_auto_summary(state):
    return "dinner" in state.get("logged_meals", [])
```

---

## 7. Weekend 5 — Weekly Reports & Patterns

### Goal
`GET /api/report/weekly?userId=xxx` → Express fetches 7 days → Python analyzes → patterns returned.

### New Python endpoint

**File:** `agent/server.py`

```python
@app.post("/analyze")
async def analyze(data: dict):
    result = weekly_graph.ainvoke(data)
    return result
```

### New Express route + controller

**File:** `backend/routes/report.js`

```javascript
const express = require('express');
const router = express.Router();
const { getWeeklyReport } = require('../controllers/reportController');
router.get('/weekly', getWeeklyReport);
module.exports = router;
```

**File:** `backend/controllers/reportController.js`

```javascript
const Session = require('../models/Session');
const axios = require('axios');

exports.getWeeklyReport = async (req, res) => {
  const { userId } = req.query;
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

  const sessions = await Session.find({
    userId,
    updatedAt: { $gte: sevenDaysAgo }
  }).sort({ date: 1 });

  const analysis = await axios.post(`${FASTAPI_URL}/analyze`, { sessions });
  res.json(analysis.data);
};
```

---

## 8. Weekend 6 — Frontend UI Polish

### Goal
Clean, usable web interface. Build ONLY after all APIs work in Postman.

### What to build

Create `client/index.html` with:

- Chat message bubbles (user left, bot right)
- Input box + Send button at bottom
- "Today's Totals" sidebar showing macros
- Simple, mobile-friendly CSS

**Do NOT touch this until Postman tests pass.**
Frontend is just a form that calls your APIs. If APIs work, frontend is trivial.

---

## 9. Weekend 7 — Reminders + Deploy

### Goal
10:30 PM check for missing logs. Deploy to Railway.

### 9.1 Nightly reminder

In `backend/server.js`:

```javascript
const cron = require('node-cron');

cron.schedule('30 22 * * *', async () => {
  const today = new Date().toISOString().split('T')[0];
  const sessions = await Session.find({ date: today });

  for (const session of sessions) {
    const missing = [];
    if (!session.loggedMeals?.length) missing.push('meals');
    if (!session.workout?.weight_training?.length && !session.workout?.cardio?.length)
      missing.push('workout');
    if (!session.others?.water) missing.push('water');
    if (!session.others?.sleep) missing.push('sleep');

    if (missing.length) {
      console.log(`Reminder: User ${session.userId} missing: ${missing.join(', ')}`);
      // Later: send email via nodemailer
    }
  }
});
```

### 9.2 Deploy to Railway

Two services:

| Service | Folder | Start command | Visibility |
|---------|--------|--------------|------------|
| Python Agent | agent/ | `uvicorn server:app --host 0.0.0.0 --port $PORT` | Internal (Express talks to it) |
| Node Backend | backend/ | `node server.js` | Public on port 3000 |

Both connect to MongoDB Atlas (free tier).
Frontend is served by Express as static files.

---

## 10. MongoDB Schemas

### sessions

```json
{
  "userId": "user_abc123",
  "date": "2024-01-15",
  "conversationStage": "idle",
  "chosenMeal": "",
  "loggedMeals": ["breakfast", "lunch"],
  "meals": {
    "breakfast": {
      "foods": [{"name": "eggs", "quantity": 3, "unit": "whole"}],
      "macros": {"protein": 24, "carbs": 30, "fat": 15, "calories": 350}
    }
  },
  "workout": {},
  "others": {},
  "dailyTotals": {},
  "messages": [],
  "botReply": ""
}
```

### meal_logs

```json
{
  "userId": "user_abc123",
  "date": "2024-01-15",
  "mealType": "breakfast",
  "items": [{"foodName": "eggs", "quantity": 3, "unit": "whole"}],
  "macros": {"protein": 24.0, "carbs": 30.0, "fat": 15.0, "calories": 350.0},
  "createdAt": ISODate
}
```

### workout_logs

```json
{
  "userId": "user_abc123",
  "date": "2024-01-15",
  "totalDuration": 60,
  "cardio": [{"name": "treadmill", "duration": 15}],
  "weightTraining": [ObjectId("...")],
  "createdAt": ISODate
}
```

### weight_training_logs

```json
{
  "userId": "user_abc123",
  "date": "2024-01-15",
  "exerciseName": "bench press",
  "totalWeight": 60.0,
  "totalReps": 10,
  "totalSets": 4,
  "restBetweenSets": 120,
  "createdAt": ISODate
}
```

### others_logs

```json
{
  "userId": "user_abc123",
  "date": "2024-01-15",
  "sleep": {"from": "23:00", "to": "06:00"},
  "waterIntake": 8,
  "screenTime": 120,
  "createdAt": ISODate
}
```

---

## 11. API Reference

| Method | Route | Service | Purpose |
|--------|-------|---------|---------|
| POST | `/process` | Python FastAPI | Run LangGraph on state, return updated state |
| GET | `/health` | Python FastAPI | Check if agent is running |
| POST | `/api/chat` | Node Express | Send message, get reply (main endpoint) |
| GET | `/api/session` | Node Express | Init or load today's session for a user |
| GET | `/api/report/weekly` | Node Express | Get 7-day pattern analysis |
| POST | `/analyze` | Python FastAPI | Run weekly analysis subgraph |

---

## 12. Stage Map

| Stage | Matched keywords | Next stage |
|-------|-----------------|------------|
| idle / awaiting_category | food, meal, breakfast, lunch, dinner, workout, gym, others, sleep, water, report | awaiting_meal_type, awaiting_workout_type, awaiting_others_category, report_generation |
| awaiting_meal_type | breakfast, lunch, dinner, snacks | awaiting_meal_items (or idle if logged) |
| awaiting_meal_items | Any text (food items) | idle (after LLM) |
| awaiting_workout_type | weight, cardio | awaiting_exercise_details |
| awaiting_exercise_details | Exercise text or "done" | Stay until "done" |
| awaiting_others_category | sleep, water, screen | awaiting_sleep / awaiting_water / awaiting_screen_time |
| awaiting_sleep | Sleep time text | idle |
| awaiting_water | Number (glasses) | idle |
| awaiting_screen_time | Number (minutes) | idle |
| report_generation | Any text | idle |

---

## 14. Interview-Relevant Features (Add Before Weekend 3)

These are features that don't add user-facing functionality but make the
project interview-ready. Add them before or during Weekend 3.

### 14.1 LLM Error Boundary (10 minutes)

**File:** `agent/nodes/respond_node.py`

Wrap the DeepSeek call in try/except:

```python
try:
    response = llm.invoke(prompt)
    reply = f"✅ {meal_type.capitalize()} logged!\n{response.content}"
except Exception as e:
    logging.error(f"DeepSeek failed: {e}")
    reply = "Sorry, couldn't process that. Please try again."
```

Without this, a DeepSeek timeout crashes the graph and Express returns 500.

---

### 14.2 Structured Logging (Node.js — 15 minutes)

**Install:**
```bash
cd backend
npm install pino
```

**File:** `backend/server.js` — Add logger:

```javascript
const pino = require('pino');
const logger = pino({ level: process.env.LOG_LEVEL || 'info' });
```

Replace `console.log()` with `logger.info()` and `console.error()` with `logger.error()`.
Add request IDs to trace conversations across services:

```javascript
const requestId = `${userId}_${Date.now()}`;
logger.info({ requestId, userId, message }, 'chat request');
```

---

### 14.3 Structured Logging (Python — 10 minutes)

**File:** `agent/server.py` — Add before app:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

Log every request:

```python
logger.info(f"user={state['user_id']}, input={state['user_input']}, stage={state['conversation_stage']}")
```

---

### 14.4 Real Mongoose Sub-Schemas

**File:** `backend/models/Session.js`

Replace `Mixed` with real sub-schemas:

```javascript
const foodItemSchema = new mongoose.Schema({
  name: String, quantity: Number, unit: String
}, { _id: false });

const macrosSchema = new mongoose.Schema({
  protein: Number, carbs: Number, fat: Number, calories: Number
}, { _id: false });

const mealEntrySchema = new mongoose.Schema({
  foods: [foodItemSchema], macros: macrosSchema, raw_llm_response: String
}, { _id: false });

// In sessionSchema:
meals: { type: Map, of: mealEntrySchema, default: {} },
```

**Interview answer:** "I use real sub-schemas for known data shapes and
Mixed only for the wrapper. This gives validation without losing flexibility."

---

### 14.5 Service Layer Separation (Node.js)

Create `backend/services/sessionService.js` and `backend/services/agentService.js`.
Controllers become thin — they handle req/res only. Services handle business logic.

**Interview value:** Shows you understand separation of concerns.

---

### 14.6 Auth — JWT

Create `backend/middleware/auth.js` that validates JWT from Authorization header.
Apply to all protected routes.

**Interview answer:** "JWT is stateless — no server-side session storage.
The Python agent never sees auth. Express validates before forwarding."

---

### 14.7 Docker Setup

Three containers: `node-backend`, `python-agent`, `mongodb`.
Docker Compose with shared network and healthchecks.

**Interview answer:** "Anyone can run `docker-compose up` for the full stack.
This is production deployment at any company using containers."

---

## 15. Resume Bullet Template

```
KYH — AI Fitness Coach
Node.js, Express, Python, FastAPI, LangGraph, MongoDB, Docker

• Architected dual-service system: Node.js/Express API layer orchestrating
  a Python/FastAPI LangGraph agent over HTTP
• Designed finite-state conversation engine with keyword routing —
  reduced LLM costs by 80% vs naive AI-only approaches
• Implemented JWT auth, structured logging (pino), Docker containerization
• Integrated DeepSeek V3 for real-time macro calculation from natural
  food descriptions
• Built MongoDB schema with session-state docs and permanent log collections
```

---

## 16. Keywords for Resume

Backend: `Node.js`, `Express`, `REST API`, `MongoDB`, `Mongoose`, `JWT`,
`Middleware`, `Service Layer`, `Docker`, `Docker Compose`

AI: `Python`, `FastAPI`, `LangGraph`, `LangChain`, `DeepSeek`, `LLM`,
`Agent Architecture`, `State Machine`

---

## 17. Golden Rules

1. **One weekend, one feature.** Weekend 1 must work before Weekend 2.
2. **Test with Postman before frontend.** If Postman tests pass, bugs are in the UI, not the backend.
3. **Build APIs first. Frontend last.** Frontend is just a form calling your APIs.
4. **No LLM for menu choices.** Keyword match only. LLM costs money.
5. **LLM only for:** macro parsing, feedback generation, weekly analysis.
6. **Both services running, always.** Python + Node + MongoDB must all be up for testing.
7. **Deploy ugly. A working product > beautiful UI.** Ship first, polish later.
8. **30-minute rule.** Stuck > 30 min? Ask for direction, not code.
9. **Commit every weekend.** `git commit -m "Weekend X: what shipped"`
10. **This is your portfolio.** The Node Express code gets you JavaScript jobs.
   The LangGraph Python code gets you AI jobs. Two skills, one project.

---

## Quick Start (This Weekend — 5 Hours)

| Step | File | Time |
|------|------|------|
| 1 | `agent/state/agent_state.py` — add `chosen_meal` | 5 min |
| 2 | `agent/nodes/intake_node.py` — keyword matching | 30 min |
| 3 | `agent/nodes/respond_node.py` — stage replies | 30 min |
| 4 | `agent/server.py` — FastAPI endpoint | 20 min |
| 5 | `backend/models/Session.js` — Mongoose schema | 10 min |
| 6 | `backend/controllers/chatController.js` | 30 min |
| 7 | `backend/controllers/sessionController.js` | 15 min |
| 8 | `backend/routes/chat.js`, `routes/session.js` | 10 min |
| 9 | `backend/server.js` — Express entry + cron | 20 min |
| 10 | Test all 7 Postman requests | 30 min |
| 11 | `client/index.html` — Only if Postman passes | 1 hr |

**Your position: Weekends 1-3 done. Food, workout, sleep/water flows all working.**
**Next: Interview features (section 14) OR Weekend 4 — Daily Summary + Feedback. Your call.**
