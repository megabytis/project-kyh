# KYH — Know Your Habit (AI Fitness Coach)

![Live Demo](https://img.shields.io/badge/Live%20Demo-kyh.bhuktatech.in-brightgreen?style=for-the-badge&logo=nginx)
![Dockerized](https://img.shields.io/badge/Docker-Containerized-blue?style=for-the-badge&logo=docker)
![Node.js](https://img.shields.io/badge/Backend-Node.js%20%7C%20Express-339933?style=for-the-badge&logo=nodedotjs)
![Python](https://img.shields.io/badge/AI%20Agent-Python%20%7C%20LangGraph-3776AB?style=for-the-badge&logo=python)
![MongoDB](https://img.shields.io/badge/Database-MongoDB%20Atlas-47A248?style=for-the-badge&logo=mongodb)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

**KYH (Know Your Habit)** is a production-grade, full-stack AI fitness coaching platform. Users interact with an intuitive dashboard to log daily meals, workouts, sleep, and hydration using simple natural language. Powered by a stateful **LangGraph** AI agent, KYH parses food macronutrients, analyzes training volume, detects habit patterns, provides daily feedback, and generates actionable weekly reports.

---

## 🌐 Live Demo

Visit the live production deployment:  
👉 **[https://kyh.bhuktatech.in](https://kyh.bhuktatech.in)**

### What you can do on the live app:
* 🥗 **Natural Language Meal Logging**: Enter meals like *"3 eggs, 100g soya chunks, 2 roti"* and let the AI extract calories, protein, carbs, and fats automatically.
* 🏋️ **Workout Tracking**: Log cardio sessions or weight training exercises (sets, reps, weights, rest duration).
* 💧 **Daily Habits Monitoring**: Track sleep duration, water consumption, and screen time.
* 🤖 **AI Coaching & Feedback**: Receive real-time AI feedback on your daily nutrition and training, plus personalized recommendations for tomorrow.
* 📊 **Analytics & Reports**: Review automated daily summaries and weekly habit progress reports.

---

## ✨ Features

- **Natural Language Parsing**: Conversational intake of food and workout entries using DeepSeek LLM.
- **Stateful AI Agent (LangGraph)**: Multi-step graph architecture for intake processing, macro calculation, pattern identification, feedback generation, and workout planning.
- **Full-Stack Microservices Architecture**: Express REST backend, FastAPI AI agent server, MongoDB persistence, and an Nginx-served single-page app.
- **Modular Database Schemas**: Relational references in MongoDB connecting daily user logs, meal details, weight training exercises, and lifestyle metrics.
- **One-Command Container Deployment**: Entire stack containerized with Docker & Docker Compose for immediate local execution or cloud deployment.

---

## 🏗️ Architecture & Tech Stack

### System Architecture Flow

```
┌───────────────────────────────────────────────────────────┐
│                      Client (Browser)                     │
│                  (HTML / Vanilla CSS / JS)                │
└─────────────────────────────┬─────────────────────────────┘
                              │ HTTP / REST (Port 80 / 3000)
                              ▼
┌───────────────────────────────────────────────────────────┐
│                   Backend (Node.js / Express)             │
│   • Session & Log Management                           │
│   • MongoDB Aggregations & REST Endpoints                 │
└──────────────┬─────────────────────────────┬──────────────┘
               │                             │
               │ PyMongo / Mongoose          │ REST API (Port 8000)
               ▼                             ▼
┌──────────────────────────────┐ ┌──────────────────────────┐
│   Database (MongoDB Atlas)   │ │  Agent (FastAPI/LangGraph)│
│  • Meals, Workouts, Others   │ │  • LLM Macro Extraction  │
│  • Session Checkpoints       │ │  • Graph State Machine   │
└──────────────────────────────┘ └─────────────┬────────────┘
                                               │
                                               │ DeepSeek API
                                               ▼
                                 ┌──────────────────────────┐
                                 │ DeepSeek-v4-flash Model │
                                 └──────────────────────────┘
```

### Core Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Nginx | Lightweight dashboard served via Nginx web server |
| **Backend API** | Node.js, Express.js, Cors, Axios | REST API handling client requests, orchestration, and database operations |
| **AI Agent** | Python 3.11+, FastAPI, LangGraph, LangChain | Autonomous graph-based agent performing entity extraction and feedback |
| **LLM Provider** | DeepSeek (`deepseek-v4-flash`) | Natural language understanding and nutrient extraction model |
| **Database** | MongoDB Atlas / MongoDB 7 | NoSQL document database storing meals, workouts, lifestyle, and agent states |
| **Containerization** | Docker, Docker Compose | Multi-container setup orchestrating frontend, backend, agent, and database |

---

## 📁 Project Structure

```
project-kyh/
├── compose.yaml                # Production Docker Compose orchestration file
├── README.md                   # Project documentation
├── .env.example                # Environment variable template file
├── client/                     # Frontend Application
│   ├── Dockerfile              # Container definition for Nginx web server
│   ├── index.html              # Main HTML dashboard layout
│   ├── style.css               # Modern dark-mode custom stylesheet
│   └── app.js                  # Frontend API client and DOM logic
├── backend/                    # Node.js REST API Server
│   ├── Dockerfile              # Container definition for Node.js backend
│   ├── package.json            # Node.js dependencies and scripts
│   ├── server.js               # Express application entry point
│   ├── routes/                 # Express REST API routes
│   ├── controllers/            # Route handlers & business logic
│   ├── models/                 # Mongoose schemas (Meal, Workout, Others, Session)
│   └── db/                     # MongoDB connection configuration
└── agent/                      # Python AI Agent Service
    ├── Dockerfile              # Container definition for FastAPI agent
    ├── requirements.txt        # Python dependencies (LangGraph, FastAPI, etc.)
    ├── server.py               # FastAPI server exposing AI endpoints
    ├── graph/                  # LangGraph state graph definition & compilation
    ├── nodes/                  # Graph node handlers (intake, respond, summary, feedback)
    ├── llm/                    # DeepSeek LLM wrapper and prompt templates
    └── state/                  # AgentState schema definitions
```

---

## 🚀 Getting Started (For Developers)

### Prerequisites

* [Docker](https://docs.docker.com/get-docker/) (v24.0+)
* [Docker Compose](https://docs.docker.com/compose/install/) (v2.20+)
* A **DeepSeek API Key** ([Get one here](https://platform.deepseek.com))
* A **MongoDB Atlas Connection URI** (or local MongoDB instance)

---

### Local Setup Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/your-username/project-kyh.git
cd project-kyh
```

#### 2. Create the Environment Configuration
Create a `.env` file in the root directory based on the following template:

```ini
# DeepSeek LLM Credentials
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash

# MongoDB Database Configuration
MONGO_URI=mongodb://mongo:27017/kyhDB
MONGO_DB_NAME=kyhDB

# Service URLs
FASTAPI_URL=http://agent:8000
PORT=3000
```

> **Note:** When running with Docker Compose, `mongodb://mongo:27017/kyhDB` uses the internal Docker network container name. If using MongoDB Atlas, replace `MONGO_URI` with your connection string (e.g., `mongodb+srv://<user>:<password>@cluster.mongodb.net/kyhDB`).

#### 3. Build and Run the Stack
Spin up all microservices with Docker Compose:

```bash
docker compose up --build -d
```

#### 4. Access the Services

Once the containers are running, access the services locally:

* 🌐 **Frontend Application**: `http://localhost` (Port 80)
* ⚙️ **Backend API Server**: `http://localhost:3000`
* 🤖 **AI Agent Server**: `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`)
* 🍃 **MongoDB Instance**: `localhost:27017`

To view container logs:
```bash
docker compose logs -f
```

To stop all services:
```bash
docker compose down
```

---

## 🛠️ Service Documentation

### 1. Backend Service (`/backend`)
Built with **Node.js** and **Express.js**, the backend acts as the central API gateway and database controller.
* **Responsibilities**:
  * Exposes RESTful endpoints for meals, workouts, sleep, and water logs.
  * Proxies natural language queries to the Python FastAPI agent service.
  * Handles database persistence with Mongoose/MongoDB.
* **Key Endpoints**:
  * `POST /api/logs/meal` — Create or append a meal entry.
  * `POST /api/logs/workout` — Save cardio or weight training exercise entries.
  * `POST /api/logs/others` — Log sleep duration, water intake, and screen time.
  * `POST /api/agent/chat` — Send user text input to the LangGraph AI agent for parsing & feedback.
  * `GET  /api/summary/daily?date=YYYY-MM-DD` — Retrieve consolidated metrics for a specific day.

### 2. Agent Service (`/agent`)
Built with **Python**, **FastAPI**, and **LangGraph**, the agent forms the intelligence layer of KYH.
* **Responsibilities**:
  * Implements a stateful graph workflow to process natural language.
  * Performs structural extraction of food items, quantities, and macronutrients.
  * Analyzes training parameters and generates adaptive daily coaching feedback.
* **LangGraph Nodes**:
  * `intake`: Identifies user intent (meal log, workout log, lifestyle metrics, general question).
  * `respond`: Formulates contextual natural language conversational responses.
  * `daily_summary`: Calculates daily total calories, protein, carbs, and fat.
  * `feedback`: Evaluates daily performance against target goals and flags nutrition/exercise mistakes.
  * `plan`: Generates actionable suggestions and workout plans for the upcoming day.

### 3. Database Schemas (`MongoDB`)
KYH utilizes 4 main MongoDB collection schemas:
1. **Meals Schema (`meals`)**:
   `{ user_id, date, meal_type, items: [{ food_name, quantity, unit }], macros: { protein, carbs, fat, calories } }`
2. **Workout Schema (`workouts`)**:
   `{ user_id, date, total_duration, cardio: [{ name, duration }], weight_training: [ObjectId refs] }`
3. **Weight Training Schema (`weight_trainings`)**:
   `{ user_id, date, exercise_name, total_weight, total_reps, total_sets, rest_between_sets }`
4. **Others Schema (`others`)**:
   `{ user_id, date, sleep: { from, to }, water_intake, screen_time }`

### 4. Frontend Service (`/client`)
A lightweight, modern web interface served by **Nginx**.
* **Responsibilities**:
  * Renders a responsive dark-themed dashboard.
  * Allows interactive natural language logging for meals and workouts.
  * Visualizes daily macro totals, progress bars, and historical logs.

---

## 🚢 Production Deployment

The repository includes a ready-to-deploy `compose.yaml` configuration suitable for any Cloud VM instance (e.g., **AWS EC2**, **DigitalOcean Droplet**, or **Linode**).

### Deployment Steps:
1. Provision a Linux Server (e.g., Ubuntu 22.04 LTS on AWS EC2).
2. Install Docker and Docker Compose.
3. Clone this repository onto the server.
4. Configure your `.env` file with production credentials (including your MongoDB Atlas URI).
5. Run `docker compose up --build -d`.
6. Configure **Nginx** or **Traefik** on the host server to handle SSL certificates (Let's Encrypt / Certbot) and reverse-proxy domain requests (e.g. `kyh.bhuktatech.in`) to Port 80.

---

## 🔑 Environment Variables

The application relies on the following environment variables:

| Variable | Required | Description | Example |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | **Yes** | Secret API key for DeepSeek LLM service | `sk-xxxxxxxxxxxxxxxx` |
| `DEEPSEEK_BASE_URL` | Optional | API base URL endpoint for DeepSeek | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | Optional | Target LLM model name | `deepseek-v4-flash` |
| `MONGO_URI` | **Yes** | MongoDB connection string (Local or Atlas) | `mongodb://mongo:27017/kyhDB` |
| `MONGO_DB_NAME` | Optional | Target MongoDB database name | `kyhDB` |
| `FASTAPI_URL` | **Yes** | Internal network URL for Express to reach Agent | `http://agent:8000` |
| `PORT` | Optional | Port for Express backend server | `3000` |

---

## 🗺️ Roadmap & Future Enhancements

- [ ] **Multi-User Authentication**: JWT / OAuth2 authentication for individual user accounts.
- [ ] **Telegram Bot Interface**: Native integration with `python-telegram-bot` for conversational logging directly inside Telegram.
- [ ] **Mobile App**: Cross-platform React Native / Flutter application.
- [ ] **Wearable Sync**: Import heart rate, step count, and active calories from Apple Health and Google Fit.
- [ ] **Visual Micronutrient Breakdown**: Detailed vitamins and minerals tracking from food entries.

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Crafted with ❤️ by the KYH Team
</p>
