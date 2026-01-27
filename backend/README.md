# Nexus AI Backend

This is the FastAPI backend for Nexus AI - the multi-agent AI workspace.

## Prerequisites

- Python 3.10+
- **Redis Server** (Critical for messaging & task queue)
  - Windows: [Download Memurai](https://www.memurai.com/get-memurai) or [Redis for Windows](https://github.com/microsoftarchive/redis/releases)
  - Linux/Mac: `sudo apt install redis-server` or `brew install redis`

## Setup

1. Create virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment file:
   ```bash
   cp .env.example .env
   ```

5. Configure `.env` with your settings

6. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

7. Run the worker (separate terminal):
   ```bash
   python worker.py
   ```

## 🧠 Memory System

The backend includes a comprehensive memory and context system:

### Components

| Module | Purpose |
|--------|---------|
| `memory/vector_store.py` | ChromaDB wrapper for vector storage |
| `memory/embeddings.py` | Embedding generation with Redis caching |
| `memory/rag.py` | Retrieval Augmented Generation engine |
| `memory/conversation_tracker.py` | Track user/agent interactions |
| `memory/preference_learner.py` | Learn from feedback |
| `memory/context_manager.py` | Task reference resolution |
| `memory/memory_analytics.py` | Usage statistics |

### Memory API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/memory/conversations` | Get conversation history |
| GET | `/memory/preferences` | Get learned preferences |
| GET | `/memory/related?prompt=...` | Find similar tasks |
| GET | `/memory/stats` | Get memory statistics |
| GET | `/memory/analytics` | Full analytics |
| GET | `/memory/search?query=...` | Semantic search |
| DELETE | `/memory/{id}` | Delete a memory |
| POST | `/tasks/{id}/feedback` | Submit task rating |

### Seed Domain Knowledge

```bash
python seed_knowledge.py
```

## Folder Structure

```
backend/
├── agents/           # AI Agent implementations
│   ├── base_agent.py       # Base class with memory methods
│   ├── research_agent.py   # Web research
│   ├── code_agent.py       # Code generation
│   ├── content_agent.py    # Content writing
│   ├── data_agent.py       # Data analysis
│   └── memory_agent.py     # Memory operations
├── tools/            # Agent tools (web search, code exec, etc.)
├── orchestrator/     # Task planning & coordination
├── memory/           # Vector store & context management
│   ├── vector_store.py
│   ├── embeddings.py
│   ├── rag.py
│   ├── conversation_tracker.py
│   ├── preference_learner.py
│   ├── context_manager.py
│   └── memory_analytics.py
├── llm/              # LLM integrations (Ollama, Groq)
├── messaging/        # Inter-agent communication
├── routers/          # API endpoints
│   ├── auth.py
│   ├── tasks.py
│   ├── agents.py
│   ├── memory.py         # Memory API
│   └── feedback.py       # Task feedback API
├── models/           # SQLAlchemy database models
├── schemas/          # Pydantic schemas
├── alembic/          # Database migrations
├── tests/            # Test files
├── main.py           # FastAPI app entry point
├── worker.py         # Background task processor
├── database.py       # Database connection
├── config.py         # Configuration settings
└── requirements.txt  # Python dependencies
```

## Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./nexus.db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key

# LLM
GROQ_API_KEY=your-groq-key

# Memory System (Phase 5)
CHROMADB_DIR=./data/chromadb
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_CACHE_TTL=604800
```

