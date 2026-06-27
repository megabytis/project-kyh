# KYH — Interview Preparation Guide

## How to use this document

Before any backend/AI interview, read through these questions.
Practice answering out loud. Each answer should take **1-2 minutes**.
Don't memorize — understand the concept enough to explain it naturally.

---

## Section 1: Architecture & Design Decisions

### Q1: Why two services (Node.js + Python) instead of one?

**Bad answer:** "I just like both languages."

**Good answer:**
"Node.js is the right tool for the web layer — it handles concurrent HTTP
requests efficiently, manages WebSocket connections, and the npm ecosystem
has everything for API development. Python is the right tool for the AI
layer — LangGraph, LangChain, and the entire LLM ecosystem are Python-first.
Splitting them means each service does one thing well. Node handles
sessions, routing, and persistence. Python handles agent orchestration
and LLM calls. They communicate over HTTP with a clean contract."

**Interviewer follow-up:** "What's the downside?"
"Latency — every chat message makes an HTTP call between services.
For a single user it's negligible. At scale, you'd use message queues
or gRPC."

---

### Q2: Why LangGraph instead of plain LangChain?

**Bad answer:** "It's newer and cooler."

**Good answer:**
"LangGraph gives me a state machine — each message goes through defined
nodes (intake → respond) with a shared state dict. I can track
conversation_stage, add conditional routing, and insert nodes like
daily_summary or weekly_analysis without rewriting the flow. LangChain
is linear chains. LangGraph is a graph — better for multi-step agents."

---

### Q3: Why MongoDB instead of PostgreSQL?

**Bad answer:** "I already know MongoDB from MERN."

**Good answer:**
"The data is document-shaped — meals have nested foods and macros,
workouts have embedded exercise arrays. MongoDB stores these naturally
without JOINs. Session state is schemaless by nature (different fields
get written at different stages). For a single-user app with varied
document shapes, MongoDB is simpler. If I needed complex aggregations
or relational queries, I'd use PostgreSQL."

**Interviewer follow-up:** "Have you faced any MongoDB-specific problems?"
"Duplicate session creation was an issue early on — fixed with a
compound unique index on userId + date."

---

### Q4: Why keyword matching instead of LLM for menu choices?

**Bad answer:** "LLMs are expensive."

**Good answer:**
"Two reasons. First, cost — classifying 'breakfast' or 'food' doesn't
need a 70B parameter model. Second, reliability — keyword matching
returns exactly one result every time. LLMs can hallucinate, return
different formats, or timeout. LLM calls are reserved for tasks that
need reasoning (macro calculation, feedback generation). Navigation
is deterministic — use deterministic code."

---

### Q5: Why DeepSeek V3 instead of OpenAI / Claude?

**Bad answer:** "It's cheaper."

**Good answer:**
"DeepSeek V3 offers competitive reasoning at significantly lower cost
— roughly 1/10th of GPT-4-turbo for comparable quality on structured
tasks like macro parsing. For a personal project where I'm paying
API costs, it's the practical choice. The abstraction layer
(LangChain's ChatOpenAI with custom base_url) means I can swap
providers without changing a line of agent code."

---

## Section 2: Backend Engineering

### Q6: How does authentication work?

**Answer:**
"Currently, the app uses userId as a query parameter for development.
Before opening to other users, I'll implement JWT — user logs in,
gets a token, sends it in Authorization header. Express middleware
validates the token on every protected route. The Python agent
service doesn't handle auth — it trusts the Node layer to authenticate
before forwarding requests."

---

### Q7: How do you manage conversation state?

**Answer:**
"Each user gets one session document per day in MongoDB. The session
stores conversation_stage, logged_meals, and current meal/workout data.
On every message, Express loads the session, sends it to Python, gets
the updated state back, and saves it. This is stateless from Python's
perspective — the full state travels with every request. That keeps
the agent service simple and horizontally scalable."

---

### Q8: How do you handle errors?

**Answer:**
"Three layers. First, the Python agent has try/except around every
LLM call — if DeepSeek times out, it returns a friendly fallback
message. Second, Express catches axios errors — if Python is down,
it returns 'Agent offline' instead of crashing. Third, every route
has a global error handler that logs the error and returns a 500.
No uncaught exceptions escape."

---

### Q9: How does your logging work?

**Answer:**
"Node.js uses pino for structured JSON logging — each log line has
timestamp, level, request ID, and message. Python uses the built-in
logging module. When debugging, I can filter by request ID to trace
a single conversation across both services."

---

### Q10: How would you scale this for 1000 users?

**Answer:**
"Stateless Python agent scales horizontally — add more FastAPI instances
behind a load balancer. Node.js Express scales too, but the bottleneck
is MongoDB. I'd add read replicas for session loading and shard by
userId. For the LLM, DeepSeek has rate limits — I'd add a queue with
retry logic. The current architecture supports this because the
services are already separated."

---

## Section 3: AI & LLM Integration

### Q11: How do you minimize LLM costs?

**Answer:**
"Keyword matching handles all menu navigation — zero LLM calls for
choosing categories or meal types. LLM only fires for macro parsing
from food descriptions, and later for daily feedback and weekly
analysis. For a typical day with 3 meals + 1 feedback, that's ~4 LLM
calls per day at roughly 500 tokens each. At DeepSeek pricing, that's
about 1 paisa per day."

---

### Q12: How does the conversation flow work?

**Answer:**
"It's a finite state machine. User input goes through intake_node
which matches keywords to transition between stages. respond_node
reads the current stage and generates the appropriate reply — either
hardcoded text for menus or an LLM call for data parsing. The stages
form a directed graph: idle → awaiting_meal_type → awaiting_meal_items
→ idle, with similar branches for workouts and sleep."

---

### Q13: What happens if DeepSeek returns bad data?

**Answer:**
"The try/except catches the exception. The bot replies: 'Sorry,
couldn't process that. Please try again.' The user stays in the same
stage and can retry. The error is logged with the input that caused
it so I can debug later. In a future version, I'd add retry logic
with exponential backoff for transient failures."

---

### Q14: How would you add RAG to this?

**Answer:**
"If I wanted the agent to answer questions about nutrition science
or workout plans, I'd add a vector store (Chroma or Qdrant) with
curated fitness knowledge. When the user asks a question, the system
retrieves relevant chunks and injects them into the LLM prompt as
context. The agent's intent router would detect questions vs log
entries and route to the RAG node instead of the meal parser."

---

## Section 4: Database Design

### Q15: Why two collections — sessions and meal_logs?

**Answer:**
"Sessions are ephemeral — they store active conversation state and
disappear when the conversation ends (daily reset). meal_logs are
permanent records. Sessions use Mixed schemas for flexibility during
conversation. Logs have strict schemas with indexed fields for querying.
Separating them means I can query 'what did I eat last week' without
parsing session blobs."

---

### Q16: Why are you storing meal data inside sessions AND in meal_logs?

**Answer:**
"During the conversation, meals are stored in the session for quick
access (duplicate detection, stage checks). After the meal is confirmed,
a separate step writes the permanent record to meal_logs. This avoids
losing data if the session expires while keeping fast in-conversation
access. It's a small data duplication that handles two different
access patterns efficiently."

---

## Section 5: Deployment & DevOps

### Q17: How is this deployed?

**Answer:**
"Two services on Railway. The Python FastAPI service is internal —
only the Node Express service can reach it. Express is public-facing
and serves both the API and the frontend. Both connect to MongoDB
Atlas (free tier). Docker Compose orchestrates everything locally
and on the server."

---

### Q18: What's in your Docker setup?

**Answer:**
"Three containers: node-app (Express), python-agent (FastAPI),
and mongodb (local development). Docker Compose wires them together
on a shared network. Python has a healthcheck endpoint that Docker
uses to verify readiness. This lets anyone run the full stack with
`docker-compose up`."

---

### Q19: How do you handle secrets?

**Answer:**
"Environment variables loaded from .env files. DeepSeek API key,
Telegram token (for backup), MongoDB URI. In production, Railway
manages these through its dashboard. Never committed to git."

---

## Section 6: Personal & Career

### Q20: Why this project?

**Answer:**
"I wanted to learn LangGraph. The best way was to build something I'd
actually use. I track my meals and workouts anyway — having an AI
agent do the math and remember patterns is genuinely useful. The
project also let me demonstrate both my Node.js backend skills and
my Python AI skills in one system, which maps to the roles I'm
targeting: Backend Engineer with AI capabilities."

---

### Q21: What was the hardest part?

**Answer:**
"The conversation state machine. Getting the stage transitions right
— knowing when to call the LLM vs when to use a hardcoded reply,
handling the 'already logged' case, resetting state properly after
each meal. It took more iteration than expected because a single
wrong stage transition breaks the entire conversation."

---

### Q22: What would you do differently?

**Answer:**
"I'd add error handling around the LLM call earlier — the first
version crashed silently when DeepSeek timed out. Also, I'd define
the Mongoose schemas properly upfront instead of using Mixed types
everywhere. Schema validation would have caught data shape bugs
earlier."

---

### Q23: Why should we hire you?

**Answer:**
"I build things that work. I understand backend architecture —
service boundaries, API design, database choices — and I understand
AI integration — LangGraph, LLM orchestration, cost optimization.
Most candidates have one or the other. I have both in a single
shipped project."
