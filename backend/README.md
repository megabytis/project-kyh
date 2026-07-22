# KYH Backend Service (Node.js / Express API)

![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?style=for-the-badge&logo=nodedotjs)
![Express](https://img.shields.io/badge/Express.js-4.x-000000?style=for-the-badge&logo=express)
![MongoDB](https://img.shields.io/badge/Database-Mongoose-47A248?style=for-the-badge&logo=mongodb)

The **KYH Backend** is a Node.js & Express REST API server. It acts as the central orchestration layer and API gateway for the KYH platform: handling session management, user data persistence in MongoDB, proxying conversational requests to the Python AI agent, and serving the static frontend interface.

---

## 🎯 Key Responsibilities

1. **API Gateway & Routing**: Exposes REST endpoints for the client dashboard.
2. **Agent Proxying**: Routes user chat messages and natural language input to the Python FastAPI agent service (`/agent`).
3. **Session & Persistence Management**: Manages daily user session states, logs meals, workouts, sleep, and water metrics in MongoDB using Mongoose schemas.
4. **Weekly Reports Orchestration**: Fetches multi-day session data and requests comprehensive 7-day pattern analysis from the agent.
5. **Static File Serving**: Serves static HTML/CSS/JS frontend files when deployed without an external web proxy.

---

## 🛠️ Tech Stack

* **Runtime**: Node.js (ES Modules `import/export`)
* **Framework**: Express.js
* **Database ODM**: Mongoose / MongoDB
* **HTTP Client**: Axios (for agent service calls)
* **Middleware**: CORS, `dotenv`, `express.json()`

---

## 🔑 Environment Variables

The backend requires the following environment variables (stored in `.env` or passed via Docker):

| Variable | Required | Description | Default / Example |
|---|---|---|---|
| `MONGO_URI` | **Yes** | MongoDB connection string | `mongodb://mongo:27017/kyhDB` or Atlas URI |
| `FASTAPI_URL` | **Yes** | Internal HTTP URL for the Python AI agent service | `http://agent:8000` |
| `PORT` | Optional | Port on which the Express server listens | `3000` |

---

## 📡 API Endpoints

### 1. Chat & Agent Interaction (`/api/chat`)
* **`POST /api/chat`**
  * **Description**: Receives user natural language text, fetches/creates the active session, forwards the payload to the Python agent (`/process`), and updates session state in MongoDB with AI responses and parsed data.
  * **Body**:
    ```json
    {
      "user_id": "telegram_or_web_user_123",
      "user_input": "3 eggs and 2 roti for lunch"
    }
    ```
  * **Response**: Returns updated session state, parsed macros, and AI bot response.

### 2. Session Management (`/api/session`)
* **`GET /api/session`**
  * **Description**: Gets or initializes today's active session document for a given user (`user_id` & `date`).
  * **Query Params**: `?user_id=123&date=YYYY-MM-DD`
  * **Response**: Returns the current session state object (conversation stage, logged meals, workout data, daily totals, feedback).

### 3. Analytics & Weekly Reports (`/api/report`)
* **`GET /api/report/weekly`**
  * **Description**: Queries MongoDB for the past 7 days of session logs for a user, sends the consolidated sessions array to the agent's `/analyze` endpoint, and returns the generated 7-day weekly performance report.
  * **Query Params**: `?user_id=123`
  * **Response**: Returns 7-day summary metrics and structured AI weekly report text.

---

## 📁 Directory Structure

```
backend/
├── db/
│   └── mongo.js        # MongoDB connection setup via Mongoose
├── models/
│   ├── Session.js      # Main daily session schema (logs, totals, stage)
│   ├── Meal.js         # Food items & macro breakdown schema
│   ├── Workout.js      # Cardio & weight training refs schema
│   └── Others.js       # Sleep, water, and screen time schema
├── controllers/
│   ├── chat.js         # Business logic for proxying chat to agent & saving state
│   ├── session.js      # Session lookup and creation logic
│   └── report.js       # Weekly aggregation & report trigger logic
├── routes/
│   ├── chat.js         # Express router for /api/chat
│   ├── session.js      # Express router for /api/session
│   └── report.js       # Express router for /api/report
├── Dockerfile          # Docker container configuration
├── package.json        # Dependencies & scripts
└── server.js           # Server initialization and middleware entry point
```

---

## 🚀 Running Locally

### 1. Install Dependencies
```bash
cd backend
npm install
```

### 2. Configure Environment Variables
Ensure a `.env` file exists in `/backend` (or project root):
```ini
MONGO_URI=mongodb://localhost:27017/kyhDB
FASTAPI_URL=http://localhost:8000
PORT=3000
```

### 3. Start the Server
```bash
npm start
# or for development:
node server.js
```

---

## 🐳 Running with Docker

Build and run standalone:
```bash
docker build -t kyh-backend .
docker run -p 3000:3000 --env-file ../.env kyh-backend
```
