# Nexus AI - Environment Configuration

This document covers the environment variables and configuration settings required to run Nexus AI.

## .env File

Create a `.env` file in the `backend/` directory. You can use `.env.example` as a template.

### API Configuration
- `PORT`: The port the backend server will run on (default: `8000`).
- `HOST`: The host for the server (default: `0.0.0.0`).
- `DEBUG`: Set to `True` for development, `False` for production.

### Security
- `SECRET_KEY`: A strong secret key for JWT token generation. (Required)
- `ALGORITHM`: The JWT algorithm (default: `HS256`).
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: `1440`).

### LLM & Search Orchestration
- `GROQ_API_KEY`: Your Groq API key (Recommended for speed).
- `OPENAI_API_KEY`: Your OpenAI API key (Optional).
- `TAVILY_API_KEY`: API key for web research (Used by ResearcherAgent).
- `DEFAULT_MODEL`: The primary model for agents (e.g., `llama-3.3-70b-versatile`).
- `FAST_MODEL`: The model for simpler tasks (e.g., `llama3-8b-8192`).
- `VISION_MODEL`: Model used for visual analysis (e.g., `llama-3.2-11b-vision-preview`).

### Database
- `DATABASE_URL`: SQLAlchemy database connection string (default: `sqlite:///./nexus.db`).

### Redis & Caching
- `REDIS_HOST`: Redis server host (default: `localhost`).
- `REDIS_PORT`: Redis server port (default: `6379`).
- `REDIS_DB`: Redis database number (default: `0`).

### Workspace
- `STORAGE_DIR`: Directory for uploaded files (default: `./storage`).
- `MAX_UPLOAD_SIZE`: Maximum file size in bytes (default: `10485760` - 10MB).

## Frontend Configuration

The frontend uses environment variables defined in `frontend/.env`.

- `VITE_API_BASE_URL`: The URL of the backend API (e.g., `http://localhost:8000`).
- `VITE_WS_URL`: The WebSocket URL (e.g., `ws://localhost:8000/ws`).

## Best Practices for Production
- **Secrets**: Never commit your `.env` file to version control.
- **Scaling**: Use a production-grade database like PostgreSQL and a cluster for Redis.
- **Monitoring**: Enable `enable_metrics=True` in `config.py` to track API performance.
