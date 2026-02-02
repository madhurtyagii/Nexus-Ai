# 📖 Nexus AI: User Manual & Local Setup Guide

This guide provides a straightforward, step-by-step process for setting up and using Nexus AI on your local machine.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Git**: To clone the repository.
- **Docker & Docker Compose**: To run the database and cache.
- **Python (3.11 or higher)**: For the backend server.
- **Node.js (18 or higher)** & **npm**: For the frontend dashboard.
- **API Keys**: 
    - [OpenAI API Key](https://platform.openai.com/) (Required for GPT models)
    - [Tavily API Key](https://tavily.com/) (Optional, but recommended for the Researcher agent)
    - [Groq API Key](https://console.groq.com/) (Optional, used for high-speed inference)

---

## 🚀 Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/madhurtyagii/nexus-ai.git
cd nexus-ai
```

### 2. Configure Environment Variables
Inside the `backend` folder, create a `.env` file from the example:
```bash
cd backend
cp .env.example .env
```
Open the `.env` file and add your API keys:
- `OPENAI_API_KEY=sk-...`
- `TAVILY_API_KEY=tvly-...` (Optional)
- `GROQ_API_KEY=gsk_...` (Optional)

### 3. Start the Infrastructure (Docker)
Nexus AI requires PostgreSQL and Redis. Start them using Docker Compose:
```bash
# From the project root
docker-compose up -d
```
*Note: This will start two containers: `nexus_postgres` and `nexus_redis`.*

### 4. Setup the Backend
```bash
cd backend
python -m venv venv

# Activate the virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```
*The backend is now running at `http://localhost:8000`.*

### 5. Setup the Frontend
```bash
cd ../frontend
npm install
npm run dev
```
*The dashboard is now running at `http://localhost:5173`.*

---

## 🖥️ Basic Usage

### 1. Initial Access
Open your browser and navigate to `http://localhost:5173`. You will see the login screen. Click "Sign Up" to create your local account.

### 2. Creating Your First Task
- Go to the **Dashboard** or **Tasks** section.
- Enter a high-level goal (e.g., "Research the latest trends in autonomous agents and write a 500-word summary").
- Click **Submit**.

### 3. Monitoring Execution
- Once submitted, you will see your task in the list. 
- Click on the task to view the **Orchestration View**.
- You can watch the "Orchestrator" break down the goal and see agents communicating via the live logs.

### 4. Exploring Memory
- As you use the system, agents will store useful information in "Long-Term Memory".
- Visit the **Memory** section to see what your workspace has learned.

---

## 🛠️ Troubleshooting

- **Port Conflict**: If `8000` or `5173` is taken, the servers will fail to start. You can change the ports in `.env` (backend) or the Vite config (frontend).
- **Database Connection**: If you get an error saying "Database not found", ensure the Docker containers are running (`docker ps`).
- **Missing Dependencies**: Ensure you are inside the Python virtual environment (`venv`) before running the backend.

---

## 🛑 Stopping the System
To stop everything:
1. Close the terminal windows running the backend and frontend.
2. Stop the Docker containers: `docker-compose down`.
