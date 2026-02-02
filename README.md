# 🧠 Nexus AI: The Autonomous Multi-Agent Workspace

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![FastAPI: 0.100+](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React: 18.x](https://img.shields.io/badge/React-18.x-61DAFB?logo=react)](https://react.dev/)
[![Docker: Required](https://img.shields.io/badge/Docker-Required-2496ED?logo=docker)](https://www.docker.com/)

**Nexus AI** is a cutting-edge, autonomous workspace that orchestrates a team of specialized AI agents to solve complex challenges through intelligent collaboration, semantic memory, and robust project orchestration.

---

## 🔥 The Value Proposition
Unlike standard chat interfaces, Nexus AI treats AI as a **workforce**. You provide a high-level goal, and the orchestrator breaks it down into actionable sub-tasks, assigns them to the most qualified agents, and manages the entire execution lifecycle in real-time.

---

## 🤖 The Specialist Team
Each agent in Nexus AI is a distinct persona with specialized tools and refined prompts:

*   **👑 The Manager**: The central orchestrator. Decomposes goals, creates project plans, and ensures quality.
*   **🔍 The Researcher**: Scours the web using Tavily to provide deep-dive insights and factual data.
*   **💻 The Coder**: Specialized in logic, debugging, and software architecture across multiple languages.
*   **✍️ The Content Lead**: Expert in creative writing, professional emails, and high-impact documentation.
*   **🧪 The QA Analyst**: Rigorously tests outputs and validates that user requirements are met.
*   **🧠 Memory Guardian**: Manages semantic context using vector embeddings for long-term project continuity.

---

## 🏗️ Technical Architecture
Nexus AI is built on a high-performance, resilient stack designed for local-first excellence:

- **Backend**: FastAPI (Python) with an asynchronous task orchestration engine.
- **Frontend**: Premium React (Vite) dashboard with real-time WebSocket monitoring.
- **Cache & Messaging**: Redis (via Docker) for lightning-fast task queuing and pub/sub updates.
- **Database**: PostgreSQL (via Docker) for robust relational state management.
- **LLM Engine**: Blazing-fast generation via **Groq API** or privacy-focused local models via **Ollama**.

---

## 🚀 Quick Start (Docker-First)

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 2. Launching the Workspace
```bash
# Clone the repository
git clone https://github.com/madhurtyagii/nexus-ai.git
cd nexus-ai

# Start local databases (Postgres & Redis)
docker-compose up -d

# Start the Backend
cd backend
python -m venv venv
# Activate venv (Windows: venv\Scripts\activate | Linux: source venv/bin/activate)
pip install -r requirements.txt
python main.py

# Start the Frontend
cd ../frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to start orchestrating!

---

## 📊 Documentation Roadmap
- [🏗️ System Architecture](docs/ARCHITECTURE.md)
- [🤖 Agent Deep-Dives](docs/AGENTS.md)
- [🔌 API Reference](backend/docs/API_GUIDE.md)
- [🛠️ Tooling System](docs/TOOLS.md)

---

## 🤝 Contributing & License
Nexus AI is released under the [MIT License](LICENSE). Contributions that advance the goal of autonomous collaboration are always welcome.

Developed with ❤️ by [Madhur Tyagi](https://github.com/madhurtyagii)
