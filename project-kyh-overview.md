# Project KYH — Know Your Habit
### Full Project Overview Document

---

## What is Project KYH?

Project KYH (Know Your Habit) is a personal AI fitness agent delivered via a Telegram bot. Instead of opening an app and manually filling forms, you simply chat with the bot daily — log what you ate, what you lifted, how long you slept — and the agent tracks everything, analyzes your patterns over time, and acts like a personal coach that actually knows your history.

The core idea: a generic AI model can answer fitness questions, but it doesn't know *you*. KYH does. It remembers every day, detects your patterns, calls out your recurring mistakes, and gives personalized guidance — not generic advice.

---

## The Problem It Solves

- Generic AI models have no memory of your past days
- Fitness apps require manual form filling — tedious
- Personal coaches are expensive
- No tool combines daily logging + pattern detection + personalized coaching in one simple chat interface

KYH solves all of this via a Telegram bot powered by a LangGraph agent with persistent memory.

---

## Who Is It For?

Initially: the builder himself — hostel student, PPL gym split, budget diet, targeting 100g+ protein daily.

Later: anyone serious about tracking their fitness without the overhead of complex apps.

---

## How The System Works — Full Overview

### Step 1: User Opens Telegram Bot
Bot greets the user and asks what they want to log today:
1. Meal
2. Workout
3. Others (sleep, water, screen time)

User selects one by one and feeds data conversationally.

### Step 2: Meal Logging
Bot asks: which meal?
1. Breakfast
2. Lunch
3. Supper
4. Other

User selects and describes what they ate with quantity (e.g. "3 eggs, 100g soya chunks, 2 roti").

Agent automatically calculates and stores:
- Macronutrients (protein, carbs, fat)
- Micronutrients
- All AI-calculated based on quantity provided

### Step 3: Workout Logging
Bot asks what type of workout:
- Cardio → user provides name + duration (embedded inside workout)
- Weight Training → user logs each exercise separately:
  - Exercise name
  - Total weight
  - Total reps
  - Total sets
  - Rest between sets

Each weight training exercise is stored as a separate document, referenced by the main Workout document.

Total workout duration is stored at the Workout Schema level.

### Step 4: Others Logging
- Sleep timing (from → to)
- Water intake count
- Screen time

### Step 5: Daily Analysis
After all logs received, the LangGraph agent:
- Calculates total calories, macros, micronutrients for the day
- Analyzes workout volume per muscle group
- Identifies today's mistakes in diet and workout
- Gives specific improvement suggestions
- Generates next day's plan

### Step 6: Memory & Pattern Detection (V3)
Agent remembers every logged day per user.
Over weeks it detects:
- Consistently low protein days
- Muscle groups being skipped
- Poor hydration patterns
- Sleep deficit trends
- Screen time impact on recovery

Every Sunday: automated weekly summary sent via Telegram.

### Step 7: Dashboard (V4)
Web frontend (React/Next.js) connected to the same MongoDB.
Login via Telegram widget — no separate auth needed.
Shows:
- Macro breakdown charts
- Workout volume over time
- Water intake trends
- Weekly pattern graphs
- Calendar view (color-coded: green = hit targets, red = missed)

---

## Database Design — 4 Schemas

### 1. Meal Schema
```
{
  user_id,
  date,
  meal_type,        // breakfast | lunch | supper | other
  items: [
    { food_name, quantity, unit }
  ],
  macros: {
    protein,        // AI calculated
    carbs,          // AI calculated
    fat             // AI calculated
  },
  micronutrients: { // AI calculated
    // vitamins, minerals etc.
  },
  created_at
}
```

### 2. Workout Schema
```
{
  user_id,
  date,
  total_duration,        // total workout time in minutes
  cardio: [
    { name, duration }   // embedded array
  ],
  weight_training: [ ObjectId refs → Weight Training Schema ],
  created_at
}
```

### 3. Weight Training Schema
```
{
  user_id,
  date,
  exercise_name,
  total_weight,          // in kg
  total_reps,
  total_sets,
  rest_between_sets,     // in seconds
  created_at
}
```

### 4. Others Schema
```
{
  user_id,
  date,
  sleep: {
    from,                // time
    to                   // time
  },
  water_intake,          // count (glasses or ml)
  screen_time,           // in minutes
  created_at
}
```

---

## Tech Stack

| Layer | Tech |
|---|---|
| Bot Interface | Telegram (python-telegram-bot) |
| Agent Logic | Python + LangGraph |
| LLM | OpenAI / DeepSeek (via API) |
| Database | MongoDB (pymongo) |
| Backend API (V4) | Node.js + Express |
| Frontend (V4) | React / Next.js |

---

## Primary Learning Goal

This project is built to learn LangGraph by building — not by following tutorials passively.

| LangGraph Concept | Where It's Used |
|---|---|
| State | AgentState holding daily log data |
| Nodes | intake, analysis, feedback, planning nodes |
| Edges | Linear flow between nodes |
| Conditional Routing | Route: meal log? workout? question? |
| Tool Calling | DB save/fetch tools |
| Persistence / Checkpointers | Memory across days per user |
| Scheduled Triggers | Weekly summary every Sunday |
| Multi-node Reasoning | Analysis + feedback + planning chain |

---

## Version Roadmap

| Version | What Ships |
|---|---|
| V1 | Pure LangGraph agent — no bot, no DB. Test graph logic with hardcoded input |
| V2 | Telegram bot + MongoDB. Real logging, daily analysis, persistent memory |
| V3 | Pattern detection, weekly summaries, adaptive suggestions |
| V4 | Node.js API + React dashboard with charts and calendar view |

---

## Portfolio Signal This Project Sends

- Not a tutorial clone
- Real agentic architecture (LangGraph, not just API wrapper)
- Persistent memory across sessions
- Multi-service system (Python agent + Telegram + MongoDB + Node.js + React)
- Solves a real personal problem
- Built from scratch without courses
