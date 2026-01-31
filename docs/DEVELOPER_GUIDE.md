# Nexus AI - Developer Guide

This guide is for engineers looking to extend, modify, or debug the Nexus AI project.

## Project Structure

```text
nexus-ai/
├── backend/                # FastAPI application
│   ├── agents/             # Agent logic & prompt engineering
│   ├── models/             # SQLAlchemy database models
│   ├── orchestrator/       # Task routing and project planning
│   ├── routers/            # API endpoint definitions
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # Core business logic
│   └── utils/              # Resiliency and security helpers
├── frontend/               # React application (Vite)
│   ├── src/
│   │   ├── components/     # UI components (TaskCards, Wizard, etc.)
│   │   ├── context/        # Authentication & Global state
│   │   └── services/       # API integration layer
├── docs/                   # Markdown documentation
└── storage/                # User-uploaded files
```

## Core Workflows

### 1. Adding a New Agent
To add a new specialized agent (e.g., `DesignerAgent`):
1. **Create Class**: Inherit from `BaseAgent` in `backend/agents/base_agent.py`.
2. **Define Prompt**: Create a `SYSTEM_PROMPT` emphasizing the agent's unique skills.
3. **Add Tools**: (Optional) Add specialized tools in `backend/tools/` and link them to the agent.
4. **Register**: Add the agent to `backend/agents/agent_registry.py`.

### 2. Customizing Resiliency
Nexus AI uses advanced patterns in `backend/utils/`:
- **Circuit Breaker**: Managed in `circuit_breaker.py`. Protects against external service outages.
- **Retries**: Configurable exponential backoff in `retries.py`.
- **Sanitization**: XSS and injection protection in `security.py`.

### 3. Modifying the project structure
The ManagerAgent's planning logic is defined in `backend/agents/manager_agent.py`. You can adjust how projects are decomposed by modifying the `system_prompt` or the `_generate_plan` method.

## Background Processing
Standard tasks use FastAPI's `BackgroundTasks`. 
For heavy production loads, it's recommended to migrate to a dedicated worker system. See the `run_worker.py` script for the experimental worker implementation.

## WebSocket Protocol
The system uses WebSockets for live status updates.
- **Endpoint**: `/ws?token=<JWT>`
- **Message Format**: 
  ```json
  {
    "event": "agent_progress",
    "data": {
      "task_id": 12,
      "agent": "CodeAgent",
      "progress": 45,
      "message": "Generating API schema..."
    }
  }
  ```

## Debugging
- **Logs**: Detailed logs are written to `backend/backend.log`.
- **Dev Mode**: Set `DEBUG=True` in `.env` to enable verbose error responses and hot-reloading.
- **Database**: Use `python debug_db.py` to inspect the local SQLite state.

## Testing
Research-driven testing is encouraged.
```bash
cd backend
pytest tests/
```

We aim for at least 80% coverage on core services and utility functions.
