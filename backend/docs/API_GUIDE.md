# Nexus AI - API Guide

Welcome to the Nexus AI API documentation. This guide provides an overview of how to interact with the Nexus AI backend services programmatically.

## Base URL

All API requests should be made to:
`http://localhost:8000`

## Authentication

Nexus AI uses JWT (JSON Web Token) for authentication. To access protected endpoints, you must include the token in the `Authorization` header:

`Authorization: Bearer <your_access_token>`

### Auth Flow
1. **Signup**: `POST /auth/signup`
2. **Login**: `POST /auth/login` -> Returns `access_token`
3. **Use Token**: Include in subsequent requests.

## Core Endpoints

### 📝 Tasks
Manage individual AI tasks and agent orchestrations.
- `POST /tasks/`: Submit a natural language prompt.
- `GET /tasks/{id}`: Get task status and output.
- `GET /tasks/queue`: View current processing queue.

### 🚀 Projects
Orchestrate complex, multi-phase AI projects.
- `POST /projects/`: Create a project (triggers AI planning).
- `POST /projects/{id}/execute`: Start executing the project workflow.
- `GET /projects/{id}/progress`: Get real-time progress metrics.

### 🧠 Memory
Interact with the semantic context and conversation history.
- `GET /memory/conversations`: Search past interactions.
- `GET /memory/preferences`: View learned user preferences.
- `GET /memory/related`: Find similar past tasks using vector embeddings.

### 🛡️ Agents
Monitor agent status and inter-agent communication.
- `GET /agents/`: List available agents and their roles.
- `GET /agents/messages`: View the message log between agents.

## Real-time Updates (WebSockets)

For live status updates (task progress, agent messages, etc.), connect to the WebSocket endpoint:

`ws://localhost:8000/ws?token=<your_access_token>`

### Event Types
- `task_started`: Initial task processing began.
- `agent_started`: A specific agent took over a subtask.
- `agent_progress`: Real-time percentage update from an agent.
- `task_completed`: Final results are ready.

## Error Handling

The API uses standard HTTP status codes:
- `200 OK`: Success.
- `201 Created`: Resource created successfully.
- `400 Bad Request`: Validation error or invalid input.
- `401 Unauthorized`: Missing or invalid authentication token.
- `403 Forbidden`: Insufficient permissions.
- `404 Not Found`: Resource does not exist.
- `529 Too Many Requests`: Rate limit exceeded.

## Best Practices
- **Rate Limiting**: Limit your requests to 100 per minute to avoid throttles.
- **Input Sanitization**: The API automatically sanitizes inputs, but ensure your data is well-formatted.
- **Background Processing**: Most complex operations return immediately with a `task_id`; use WebSockets or polling to track completion.
