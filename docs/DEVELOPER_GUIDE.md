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
To add a new specialized agent (e.g., `AnalystAgent`):
1. **Create Class**: Inherit from `BaseAgent` in `backend/agents/base_agent.py`.
2. **Define Prompt**: Create a `SYSTEM_PROMPT` emphasizing the agent's unique skills and tone.
3. **Add Tools**: Integrate specialized tools in `backend/tools/` and link them.
4. **Register**: Use the `@AgentRegistry.register` decorator on your class.
5. **LLM Config**: If specific models are needed, adjust `backend/llm/llm_manager.py`.

### 2. Multi-Provider LLM Integration
Nexus AI uses a unified `LLMManager` to wrap multiple providers:
- **Groq**: Primary provider for sub-second inference.
- **OpenAI**: Secondary provider for advanced multimodal/embedding needs.
- **Caching**: The `LLMManager` handles response caching for repeated agent thoughts.

### 3. Customizing Resiliency
Nexus AI uses advanced monitoring patterns:
- **Circuit Breaker**: Managed in `backend/utils/circuit_breaker.py` to prevent cascading failures.
- **Retries**: Configurable exponential backoff for API calls.
- **Sanitization**: XSS protection for all agent-generated markdown.

### 4. Project Planning
The ManagerAgent's planning logic is defined in `backend/agents/manager_agent.py`. You can adjust the "Brainstorming" phase by modifying the `system_prompt` or the reasoning chains.

## Background Processing
Standard tasks use FastAPI's `BackgroundTasks`. 
For heavy tasks (like SDXL image generation), the system uses subprocess workers to avoid blocking the event loop.

## WebSocket Protocol
The system uses WebSockets for live status updates.
- **Endpoint**: `/ws?token=<JWT>`
- **Events**: `agent_progress`, `task_complete`, `project_update`.

## Debugging
- **Logs**: Backend logs are in `backend/backend.log`.
- **Registry**: Inspect `AgentRegistry` to see all active agent instances.
- **Circuit State**: Monitor the circuit breaker status via the system logs during API outages.

## Testing
Research-driven testing is encouraged.
```bash
cd backend
pytest tests/
```

We aim for at least 80% coverage on core services and utility functions.
