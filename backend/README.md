# ⚙️ Nexus AI Backend

High-performance async orchestration engine built with FastAPI. Manages agents, memory, and real-time execution.

---

## 🔗 Local URLs
```
API:        http://localhost:8000
Docs:       http://localhost:8000/docs
WebSocket:  ws://localhost:8000/ws
```

---

## ✨ v2.0 Features

### Real-time
- 📡 WebSocket pub/sub for live task updates
- 💬 `/agents/chat` - Direct agent communication endpoint
- 📊 Agent metrics and performance tracking

### Intelligence
- 🧠 **RAG Endpoints** - `/files/{id}/index` and `/files/query`
- 🔍 Vector search with ChromaDB + sentence-transformers
- 📄 Text extraction for PDF, DOCX, TXT files

### Export
- 📤 `/exports/project/{id}` - PDF, Markdown, DOCX, JSON

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI (async Python) |
| Database | PostgreSQL + SQLAlchemy |
| Cache | Redis |
| Vectors | ChromaDB + Sentence Transformers |
| LLM | Groq API / Ollama |
| Auth | JWT (python-jose) |

---

## 🚀 Setup

```bash
# Create environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install & run
pip install -r requirements.txt
python main.py
```

Requires `.env` file (see `.env.example`).

---

## 📡 Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/tasks/` | Create AI task |
| GET | `/tasks/{id}` | Get task status |
| POST | `/agents/chat` | Direct agent chat |
| POST | `/files/{id}/index` | Index file for RAG |
| POST | `/files/query` | Semantic file search |
| GET | `/exports/project/{id}` | Export project |
| WS | `/ws` | Real-time updates |
