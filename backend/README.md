# ⚙️ Nexus AI Backend

The backend of Nexus AI is a high-performance, asynchronous orchestration engine built with **FastAPI**. It manages agent personas, long-term memory, and real-time project execution.

---

## 🛠️ Core Technologies
- **Framework**: FastAPI (Asynchronous Python)
- **Task Management**: Redis-backed shared memory queue
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Vector Search**: ChromaDB / Sentence Transformers
- **WebSocket**: Real-time pub/sub manager

---

## 🏗️ Technical Highlights

### 1. Unified Agent Registry
All agents are registered via a singleton `AgentRegistry`. This allows the system to dynamically instantiate agents based on the task requirement, providing a scalable way to add new personas.

### 2. Semantic Memory Engine
The backend uses **Vector Embeddings** to store context. When an agent starts a task, it automatically "recalls" relevant past successes or user preferences, ensuring projects have continuity.

### 3. Integrated Tool Registry
Agents don't just "talk"—they "do." The `ToolRegistry` provides agents with access to:
- **WebSearch**: Real-time factual research via Tavily.
- **CodeExecutor**: Safe, isolated logic execution.
- **DataAnalysis**: High-speed processing via Pandas/NumPy.

---

## 🚀 Running Locally

1.  **Environment**: Ensure you have a `.env` file based on `.env.example`.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Launch**:
    ```bash
    python main.py
    ```

The API will be available at `http://localhost:8000`, and you can explore the interactive docs at `/docs`.
