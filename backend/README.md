# ⚙️ Nexus AI Backend

<p align="center">
  <img src="https://img.shields.io/badge/Status-✅_Complete-success" alt="Status: Complete" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python" alt="Python" />
</p>

High-performance async orchestration engine built with FastAPI. Manages AI agents, semantic memory, and real-time project execution.

---

## 🔗 Local URLs
```
API:        http://localhost:8000
Docs:       http://localhost:8000/docs
WebSocket:  ws://localhost:8000/ws
Storage:    http://localhost:8000/storage
```

---

## ✨ Features

### 🤖 Multi-Agent System
- **8 specialized AI agents** (Manager, Research, Code, Content, QA, Data, Memory, Visual)
- Automatic agent selection based on task type
- Multi-phase project execution (Research → Implementation → QA)

### 🧠 Intelligence
- **RAG Endpoints** - `/files/{id}/index` and `/files/query`
- Vector search with ChromaDB + sentence-transformers
- Unified Visual Intelligence for image generation and analysis

### ⚡ Real-time
- WebSocket pub/sub for live task updates
- `/agents/chat` - Direct agent communication
- Agent metrics and performance tracking

### 👤 Account Management
- `PUT /auth/me` - Update username & email
- `PUT /auth/password` - Change password
- `GET /auth/me/api-key` - Retrieve API key

### 📤 Export
- `/exports/project/{id}` - PDF, Markdown, DOCX, JSON

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI (async Python) |
| Database | SQLite + SQLAlchemy |
| Vectors | ChromaDB + Sentence Transformers |
| LLM | Groq API |
| Auth | Direct Bcrypt (3.14 compatible) |

---

## 🚀 Setup

```bash
# Create environment
python -m venv new_venv
new_venv\Scripts\activate  # Windows

# Install & run
pip install -r requirements.txt
python main.py
```

Requires `.env` file (see `.env.example`).

---

## 📡 Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/signup` | Register new user |
| POST | `/auth/login` | Login & get JWT |
| GET | `/auth/me` | Get current user |
| PUT | `/auth/me` | Update username/email |
| PUT | `/auth/password` | Change password |
| GET | `/projects/` | List projects |
| POST | `/projects/` | Create project |
| POST | `/projects/{id}/execute` | Start execution |
| POST | `/agents/chat` | Direct agent chat |
| POST | `/files/{id}/index` | Index file for RAG |
| POST | `/files/query` | Semantic file search |
| GET | `/exports/project/{id}` | Export project |
| WS | `/ws` | Real-time updates |

---

## 📁 Project Structure

```
backend/
├── main.py           # FastAPI app entry
├── config.py         # Settings & environment
├── database.py       # Database connection
├── auth.py           # JWT & password utils
├── dependencies.py   # Dependency injection
├── routers/          # API endpoints
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
├── agents/           # AI agent definitions
├── orchestrator/     # Workflow engine
├── memory/           # RAG & vector store
├── llm/              # LLM integrations
└── tools/            # Agent tools
```

---

<p align="center">
  <strong>🎉 Project Completed — February 2026</strong>
</p>
