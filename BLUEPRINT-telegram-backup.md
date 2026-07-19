# Project KYH — Know Your Habit
## Build Blueprint

---

**Author:** 2nd year BCA student, Bhubaneswar
**Stack:** Python + LangGraph + Telegram Bot + MongoDB
**LLM:** DeepSeek V3 (direct API)
**Time:** ~5 hours per weekend
**Approach:** Keyword matching for menus, LLM only for macro calculation

**Goal:** AI fitness agent in Telegram that tracks daily meals, workouts, sleep,
water — remembers patterns, coaches you, runs 24/7.

---

## Table of Contents

1. [Current Status (What Exists Now)](#1-current-status-what-exists-now)
2. [The Core Bridge — How Telegram Talks to LangGraph](#2-the-core-bridge--how-telegram-talks-to-langgraph)
3. [Weekend 1 — Fix State + Keyword Matching](#3-weekend-1--fix-state--keyword-matching)
4. [Weekend 2 — Store Meals + LLM Macro Parsing](#4-weekend-2--store-meals--llm-macro-parsing)
5. [Weekend 3 — Workout + Sleep + Water](#5-weekend-3--workout--sleep--water)
6. [Weekend 4 — MongoDB Persistence](#6-weekend-4--mongodb-persistence)
7. [Weekend 5 — Daily Summary + Feedback](#7-weekend-5--daily-summary--feedback)
8. [Weekend 6 — Weekly Reports & Patterns](#8-weekend-6--weekly-reports--patterns)
9. [Weekend 7 — Reminders + Polish](#9-weekend-7--reminders--polish)
10. [Folder Structure Reference](#10-folder-structure-reference)
11. [Final MongoDB Schemas](#11-final-mongodb-schemas)

---

## 1. Current Status (What Exists Now)

### Files in your repo:

| File | What it does | Status |
|------|-------------|--------|
| `agent/state/agent_state.py` | AgentState TypedDict | Mostly correct — missing `chosen_meal` field |
| `agent/nodes/intake_node.py` | Wraps user text as HumanMessage | Too simple — needs stage-based keyword matching |
| `agent/nodes/respond_node.py` | Sends everything to DeepSeek | Wrong — burns money on menu choices |
| `agent/graph/graph.py` | 2-node graph: intake → respond | Correct structure, stays as-is |
| `agent/bot/telegram_handler.py` | Handles /start + messages | Has stale state bug (user_input not updated) |
| `agent/config/settings.py` | Loads env vars | OK |
| `agent/llm/llm_client.py` | DeepSeek connection | OK |
| `agent/main.py` | Entry point | OK |

### What your bot currently does:

1. User sends /start → welcome message
2. User types anything → passes to DeepSeek → AI replies (costs money every time)
3. State does NOT persist user_input between messages (bug)
4. No stage tracking works
5. No data is stored

### What needs to change:

Everything between Telegram and DeepSeek. The graph should **route** input based on
`conversation_stage`, not dump everything into DeepSeek.

---

## 2. The Core Bridge — How Telegram Talks to LangGraph

This is the single most important concept in this project. Master this and everything
else falls in place.

```
┌──────────────────────────────────────────────────┐
│                  TELEGRAM                         │
│  User types "food"                                │
│  handle_messages() runs                           │
│    → loads state                                  │
│    → sets state["user_input"] = "food"            │
│    → calls graph.ainvoke(state)                   │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│                  LANGGRAPH                         │
│  intake_node runs first:                          │
│    reads user_input = "food"                      │
│    reads conversation_stage = "idle"              │
│    matches "food" → stage = "awaiting_meal_type"  │
│    returns {conversation_stage, bot_reply}        │
│                                                   │
│  respond_node runs second:                        │
│    reads stage = "awaiting_meal_type"             │
│    returns hardcoded: "Which meal?"               │
│    NO LLM CALL                                    │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│                  TELEGRAM                         │
│  Reads final_state["bot_reply"]                   │
│  Sends to user                                    │
│  Saves final_state for next message               │
└──────────────────────────────────────────────────┘
```

### The 8-line handler pattern (telegram_handler.py):

```
1. Load state for this user
2. Set state["user_input"] = user_text
3. Set state["conversation_stage"] (preserve previous)
4. final_state = await graph.ainvoke(state)
5. Save final_state
6. reply = final_state["bot_reply"]
7. Send reply to Telegram
8. Wait for next message → repeat from step 1
```

**The graph NEVER directly touches Telegram.** It reads `user_input` and writes
`bot_reply` + `conversation_stage`. That's it. Telegram handler does the actual send/receive.

---

## 3. Weekend 1 — Fix State + Keyword Matching

### Goal
User types "food" → bot replies "Which meal?" — no LLM involved.

### LangGraph Concept
State + Nodes + Edges — already known. Conditional stage routing — new.

### Files to change

### 3.1 Add `chosen_meal` to AgentState

**File:** `agent/state/agent_state.py`

Add one line after `logged_meals`:

```python
chosen_meal: str     # "breakfast" | "lunch" | "dinner" | "snacks" | ""
```

Also add to `initial_state()` in telegram_handler.py: `"chosen_meal": ""`

**Why:** When user picks "breakfast" from the menu, intake_node needs to remember
WHICH meal they chose before asking "what did you eat?"

---

### 3.2 Rewrite intake_node — Keyword Stage Router

**File:** `agent/nodes/intake_node.py`

Current code just wraps user text as HumanMessage. Replace entirely.

**What intake_node should do:**

```
Read conversation_stage
Read user_input

If stage is "idle" or "awaiting_category":
    Check if user_input matches: "food", "workout", "others", "report"
    Set stage accordingly
    Return {conversation_stage, bot_reply: ""}

If stage is "awaiting_meal_type":
    Check "breakfast" | "lunch" | "dinner" | "snacks"
    If logged_meals already has this meal → return "Already logged" + reset to idle
    Else: set chosen_meal, set stage to "awaiting_meal_items"
    Return {chosen_meal, conversation_stage}

All other stages: just pass through (let respond_node handle)
```

**Every return must set bot_reply** — even if empty string. This prevents stale
bot_reply from a previous run leaking into the current reply.

**Every return must explicitly set conversation_stage** — even if unchanged.

---

### 3.3 Rewrite respond_node — Stage-Based Replies

**File:** `agent/nodes/respond_node.py`

Current code sends everything to DeepSeek. Replace with stage-based replies.

**What respond_node should do:**

```
If intake_node already set bot_reply → return it directly (no LLM)

Check conversation_stage:
    "awaiting_meal_type" → return "Which meal? (breakfast / lunch / dinner / snacks)"
    "awaiting_workout_type" → return "Cardio or weight training?"
    "awaiting_others_category" → return "Sleep, water, or screen time?"
    "report_generation" → return "Report coming soon"
    "idle" → return "What would you like to do?"

Special case — "awaiting_meal_items":
    If user_input is a meal keyword (breakfast/lunch/dinner/snacks):
        → "What did you eat for {meal_type}?" (no LLM)
    Else: it's actual food items
        → Call DeepSeek to parse macros
        → Return ✅ Meal logged! + macro breakdown
        → Set conversation_stage back to "idle"
        → Add meal_type to logged_meals
```

---

### 3.4 Fix telegram_handler — Update user_input

**File:** `agent/bot/telegram_handler.py`

One-line fix in `handle_messages()` — before running graph:

```python
state = user_states[user_id]
state["user_input"] = user_text    # ← FIX: update input
state["conversation_stage"] = state.get("conversation_stage", "idle")
```

Without this line, every message uses the first message's text forever.

Also remove the commented-out old bot code at the bottom (lines 91-138).

---

### Weekend 1 Success Check

Run the bot from project root (`python agent/main.py`) and test:

| You type | Bot should reply | LLM used? |
|----------|-----------------|-----------|
| `/start` | Welcome message | No |
| `food` | "Which meal? (breakfast / lunch / dinner / snacks)" | No |
| `breakfast` | "What did you eat for breakfast?" | No |
| `3 eggs 2 roti` | Macro estimate from DeepSeek | **Yes** |
| `hi` | "What would you like to do?" | No |

If LLM fires on "food", "breakfast", or "hi" — your respond_node still has wrong stage handling.

---

## 4. Weekend 2 — Store Meals + LLM Macro Parsing

### Goal
User logs breakfast → macros calculated by DeepSeek → stored in state. Duplicate meals detected.

### LangGraph Concept
Tool calling — Node calls LLM, gets structured response, stores in state.

### What to build

### 4.1 LLM prompt for macro parsing

The prompt should ask for structured data:

```
Parse these food items and return:
Foods: [{name, quantity, unit}]
Macros: {protein, carbs, fat, calories}

Items: "3 eggs 2 roti"
```

### 4.2 Store in state (respond_node)

After LLM returns macros, store in state:

```python
state["meals"][meal_type] = {"foods": [...], "macros": {...}}
```

Add meal to `logged_meals` list for duplicate detection.

### 4.3 Continue session

After logging a meal, user can immediately log another meal or workout:

```
Bot: ✅ Breakfast logged: 24g P, 32g C, 15g F, 350 cal
User: lunch
Bot: Which meal? (breakfast / lunch / dinner / snacks)  [breakfast dimmed]
User: lunch  →  continues session
```

### Weekend 2 Success Check

```
User: breakfast
Bot: What did you eat for breakfast?
User: 3 eggs 2 roti
Bot: ✅ Breakfast logged! 24g protein, 30g carbs, 15g fat, 350 cal

User: breakfast
Bot: Breakfast already logged today ✅

User: lunch
Bot: What did you eat for lunch?
User: 200g chicken rice
Bot: ✅ Lunch logged! 46g protein, 60g carbs, 8g fat, 500 cal
```

---

## 5. Weekend 3 — Workout + Sleep + Water

### Goal
Bot handles all 4 input types: food, workout, others (sleep/water/screen), and questions.

### What to build

### 5.1 Workout flow in intake_node

Stages: `awaiting_workout_type` → `awaiting_exercise_details`

```
User: workout
Bot: Cardio or weight training?
User: weight training
Bot: Describe your exercise (format: exercise | sets × reps @ weight)
User: bench press | 4 × 10 @ 60kg
Bot: ✅ Logged: bench press — 4 × 10 @ 60kg (2400kg volume)
User: done
Bot: 💪 Workout complete! Added 2 exercises.
```

### 5.2 Others flow

Stages: `awaiting_others_category` → `awaiting_sleep/water/screen`

```
User: others
Bot: Sleep, water, or screen time?
User: water
Bot: How many glasses?
User: 8
Bot: ✅ 8 glasses logged
```

For sleep, parse "11pm to 6am" via LLM.

---

## 6. Weekend 4 — MongoDB Persistence

### Goal
Bot remembers everything across sessions. Close bot, restart, it remembers yesterday.

### LangGraph Concept
Persistence — save state after each node execution.

### What to build

### 6.1 MongoDB setup

Create `agent/db/mongo_client.py`:

```python
from pymongo import MongoClient
from config.settings import MONGO_URI, MONGO_DB_NAME

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

def get_collection(name):
    return db[name]
```

### 6.2 Save on each log

In respond_node, after LLM processes food:

```python
meal_doc = {
    "user_id": ...,
    "date": ...,
    "meal_type": meal_type,
    "items": foods,
    "macros": macros,
    "created_at": datetime.utcnow()
}
get_collection("meal_logs").insert_one(meal_doc)
```

### 6.3 Load on start

Replace empty state with DB-loaded data in telegram_handler.

---

## 7. Weekend 5 — Daily Summary + Feedback

### Goal
After dinner logged, bot auto-sends daily summary with improvement tips.

### New nodes

- `daily_summary_node.py` — Calculate totals from state
- `feedback_node.py` — Call DeepSeek for critique
- `plan_node.py` — Call DeepSeek for tomorrow's plan

### Flow

```
User logs dinner
  → Bot auto-triggers summary
  → daily_summary: "Total: 1800 cal, 95g protein, 200g carbs"
  → feedback: "5g short on protein, hit water target"
  → plan: "Tomorrow: pull day, focus on back, 4 eggs breakfast"
```

---

## 8. Weekend 6 — Weekly Reports & Patterns

### Goal
User types "report" → bot fetches 7 days from MongoDB, detects patterns.

### What to build

### 8.1 weekly_graph.py

Subgraph that:
1. Fetches last 7 days
2. Calculates averages
3. Calls DeepSeek for pattern detection
4. Returns human-readable report

### Pattern examples

```
- Average 65g protein/day — consistently below 100g target
- Skipped leg day 2 weeks in a row
- Best day: Wednesday (hit all targets)
```

---

## 9. Weekend 7 — Reminders + Polish

### Goal
10:30 PM auto reminder for missing logs. Error handling. Deploy.

### What to build

### 9.1 Nightly reminder

Using python-telegram-bot's JobQueue:

```python
async def nightly_check(context):
    for user_id in active_users:
        state = load_today(user_id, today)
        missing = []
        if not state.get("logged_meals"):
            missing.append("meals")
        if not state.get("workout"):
            missing.append("workout")
        if not state.get("others", {}).get("sleep"):
            missing.append("sleep")
        if missing:
            msg = f"⏰ Missing today: {', '.join(missing)}"
            await context.bot.send_message(chat_id=int(user_id), text=msg)

job_queue.run_daily(nightly_check, time=datetime.time(hour=22, minute=30))
```

### 9.2 Skip feature

User types "skip sleep" → marks as skipped, don't ask again.

### 9.3 Error handling

Wrap all LLM calls in try-catch. Fallback reply if DeepSeek fails.

### 9.4 Deploy

Deploy on a VPS or free-tier Railway. Use systemd for auto-restart.

---

## 10. Folder Structure Reference

```
project-kyh/
├── agent/
│   ├── state/
│   │   └── agent_state.py
│   ├── graph/
│   │   ├── graph.py
│   │   └── subgraphs/
│   │       └── weekly_graph.py          (Weekend 6)
│   ├── nodes/
│   │   ├── intake_node.py
│   │   ├── respond_node.py
│   │   ├── daily_summary_node.py        (Weekend 5)
│   │   ├── feedback_node.py             (Weekend 5)
│   │   └── plan_node.py                 (Weekend 5)
│   ├── llm/
│   │   └── llm_client.py
│   ├── db/
│   │   ├── mongo_client.py              (Weekend 4)
│   │   └── models/
│   │       ├── meal_log.py
│   │       ├── workout_log.py
│   │       ├── weight_training_log.py
│   │       └── others_log.py
│   ├── bot/
│   │   └── telegram_handler.py
│   ├── config/
│   │   └── settings.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── BLUEPRINT.md
└── README.md
```

---

## 11. Final MongoDB Schemas

### meal_logs

```json
{
  "user_id": "123456789",
  "date": "2024-01-15",
  "meal_type": "breakfast",
  "items": [{"food_name": "eggs", "quantity": 3, "unit": "whole"}],
  "macros": {"protein": 24.0, "carbs": 30.0, "fat": 15.0, "calories": 350.0},
  "created_at": ISODate
}
```

### workout_logs

```json
{
  "user_id": "123456789",
  "date": "2024-01-15",
  "total_duration": 60,
  "cardio": [{"name": "treadmill", "duration": 15}],
  "weight_training": [ObjectId("...")],
  "created_at": ISODate
}
```

### weight_training_logs

```json
{
  "user_id": "123456789",
  "date": "2024-01-15",
  "exercise_name": "bench press",
  "total_weight": 60.0,
  "total_reps": 10,
  "total_sets": 4,
  "rest_between_sets": 120,
  "created_at": ISODate
}
```

### others_logs

```json
{
  "user_id": "123456789",
  "date": "2024-01-15",
  "sleep": {"from": "23:00", "to": "06:00"},
  "water_intake": 8,
  "screen_time": 120,
  "created_at": ISODate
}
```

---

## Quick Reference — Stage Map

| Stage | When | Keywords | Next stage |
|-------|------|----------|------------|
| idle / awaiting_category | After /start or reply | food, meal, breakfast, lunch, dinner, workout, gym, others, sleep, water, report | awaiting_meal_type, awaiting_workout_type, awaiting_others_category, report_generation |
| awaiting_meal_type | User chose food | breakfast, lunch, dinner, snacks | awaiting_meal_items (or idle if logged) |
| awaiting_meal_items | User chose a meal | Any text (food items) | idle (after LLM) |
| awaiting_workout_type | User chose workout | weight, cardio | awaiting_exercise_details |
| awaiting_exercise_details | Chose weight/cardio | Exercise text or "done" | Stay until "done" |
| awaiting_others_category | User chose others | sleep, water, screen | awaiting_sleep/water/screen |
| awaiting_sleep/water/screen | Specific others type | Text input | idle |
| report_generation | User asked report | Any | idle |

---

## Golden Rules

1. **One weekend, one feature.** Don't start Weekend 2 until Weekend 1 works.
2. **No LLM for menu choices.** Keyword match "food", "breakfast", "workout".
3. **LLM only for:** macro parsing, feedback, weekly analysis.
4. **Test after every change.** Run bot, send message, verify.
5. **30-minute rule.** Stuck > 30 min? Ask for direction, not code.
6. **You are the only user.** Build for how YOU talk.

---

**Your position: Before Weekend 1.** All files exist but need changes.
Open Weekend 1 section (Section 3) and start with file 3.1 — add `chosen_meal` to AgentState.
