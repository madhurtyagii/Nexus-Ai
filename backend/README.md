# Nexus AI Backend

The robust API and Orchestration engine behind Nexus AI.

## 🏗️ Architecture

The backend is built on **FastAPI** and uses a modular architecture:

- **Orchestrator**: The heart of the system. The `WorkflowEngine` breaks projects into phases and tasks.
- **Task Queue**: **Redis** is used to persist tasks. The `worker.py` process consumes these tasks, ensuring reliable execution even if the main server restarts.
- **Agents**: Autonomous entities (Manager, QA, Code, Research, etc.) implemented with specific tools and prompts.
- **Memory**: ChromaDB vector store for retrieval-augmented generation (RAG).

## 🚀 Key Components

### 1. Workflow Engine (`orchestrator/workflow_engine.py`)
- Handles execution of complex dependency graphs.
- Supports **Parallel** (async) and **Sequential** execution types.
- Integrates with `ManagerAgent` for high-level planning.

### 2. Background Worker (`worker.py`)
- Runs independently from the API server.
- Polls Redis for "queued" subtasks.
- Instantiates agents, executes tools, and updates the database.

### 3. Project Management API (`routers/projects.py`)
- `POST /projects/`: Create a project (triggers background planning).
- `POST /projects/{id}/execute`: Dispatch tasks to the queue.
- `GET /projects/{id}/progress`: Real-time status updates.

---

## 🛠️ Setup & Run

### Prerequisites
- Python 3.11+
- Redis Server (Must be running locally or via Docker)

### Installation

1. **Virtual Env**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Env Config**:
   ```bash
   cp .env.example .env
   # Add your GROQ_API_KEY and other secrets
   ```

### Running the System

You need **two** terminal windows running simultaneously:

**Terminal 1: API Server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: Task Worker**
```bash
python worker.py
```

---

## 📂 Folder Structure

```
backend/
├── agents/           # Intelligence layer (Manager, QA, etc.)
├── tools/            # Functional capability tools
├── orchestrator/     # Workflow & Queue logic
├── routers/          # REST API endpoints
├── models/           # Database schema
├── services/         # Business logic
├── memory/           # RAG & Vector store
├── worker.py         # Task queue consumer
└── main.py           # App entry point
```
