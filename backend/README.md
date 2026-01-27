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

## Folder Structure

```
backend/
├── agents/           # AI Agent implementations
├── tools/            # Agent tools (web search, code exec, etc.)
├── orchestrator/     # Task planning & coordination
├── memory/           # Vector store & context management
├── llm/              # LLM integrations (Ollama, Groq)
├── messaging/        # Inter-agent communication
├── routers/          # API endpoints
├── models/           # SQLAlchemy database models
├── schemas/          # Pydantic schemas
├── alembic/          # Database migrations
├── tests/            # Test files
├── main.py           # FastAPI app entry point
├── database.py       # Database connection
├── config.py         # Configuration settings
└── requirements.txt  # Python dependencies
```
