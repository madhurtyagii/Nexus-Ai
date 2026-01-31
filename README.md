# 🚀 Nexus AI

## Autonomous Multi-Agent AI Workspace

> Where specialized AI agents collaborate to solve complex ideas

![Status](https://img.shields.io/badge/status-live-green)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![React](https://img.shields.io/badge/React-18+-61DAFB)
![Redis](https://img.shields.io/badge/Redis-Queue-red)

---

## 🎯 Vision

Nexus AI is an autonomous multi-agent system where **7 specialized AI agents** work together to plan, execute, and verify complex tasks:

- 🔍 **Research Agent** - Web searching and information synthesis
- 💻 **Code Agent** - Code generation, debugging, and review
- ✍️ **Content Agent** - Writing documentation and copy
- 📊 **Data Agent** - Data analysis and visualization
- ✅ **QA Agent** - Quality assurance and validation (Phase 6)
- 📋 **Manager Agent** - Project planning, task breakdown, and coordination (Phase 6)
- 🧠 **Memory Agent** - Context retention and preference learning

---

## 🔥 Key Features

### 1. Advanced Workflow Orchestration
- **Project Planning**: The Manager Agent breaks down vague goals into detailed implementation plans.
- **Dependency Management**: Tasks are executed in parallel or sequentially based on dependencies.
- **Queue-Based Execution**: Robust, persistent background execution using Redis.

### 2. Multi-Agent Collaboration
- Agents communicate, share context, and hand off tasks.
- **QA Feedback Loop**: Every output is reviewed by the QA Agent; if it fails, the worker retries with feedback.

### 3. Memory & Context
- **RAG System**: Retrieval Augmented Generation for deep context awareness.
- **Long-term Memory**: ChromaDB vector store remembers past interactions.

### 4. Project Management Suite (New)
- **File Management**: Upload, analyze, and process file assets (`.pdf`, `.txt`, `.docx`).
- **Export System**: Generate professional PDF, Word, and JSON reports of project outcomes.
- **Workflow Templates**: One-click setup for common use cases (Content Marketing, Software Dev, etc.).
- **Smart Re-planning**: Dynamic adjustment of project plans based on progress.

### 5. Modern UI/UX
- Real-time progress tracking with dynamic progress bars.
- Timeline and Accordion views for project phases.
- "Project Wizard" for easy creation.

---

## 📁 Project Structure

```
nexus-ai/
├── backend/
│   ├── agents/           # Agent implementations (Manager, QA, Code, etc.)
│   ├── tools/            # Capability tools (WebSearch, FileWrite, etc.)
│   ├── orchestrator/     # WorkflowEngine & Task Queue logic
│   ├── memory/           # Vector store & RAG system
│   ├── llm/              # LLM client wrappers (Groq/Ollama)
│   ├── messaging/        # Inter-agent communication
│   ├── routers/          # FastAPI endpoints (Projects, Tasks, Auth)
│   ├── models/           # SQLAlchemy database models
│   ├── schemas/          # Pydantic data schemas
│   ├── worker.py         # Redis queue consumer (Background Worker)
│   ├── main.py           # Application entry point
│   └── config.py         # Environment configuration
├── frontend/
│   ├── src/
│   │   ├── components/   # React components (ProjectWizard, Timeline, etc.)
│   │   ├── pages/        # Application pages (Projects, Detail, Login)
│   │   ├── services/     # API client
│   │   └── context/      # Auth & Theme context
├── docs/                 # Documentation
└── docker-compose.yml    # Deployment config
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis Server (Required for Task Queue)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv (Windows: venv\Scripts\activate, Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
cp .env.example .env  # Configure your keys in .env
python main.py        # Starts API on localhost:8000
```

### 2. Worker Setup (New Terminal)
The worker is essential for processing the task queue.
```bash
cd backend
# Activate venv
python worker.py
```

### 3. Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev           # Starts UI on localhost:5173
```

---

## 🚧 Development Status

**Completed Phases:**
- ✅ Phase 1-5: Foundation & Core Agents
- ✅ Phase 6: Project Management, QA, & Workflows
- ✅ Phase 7: File System, Exports & Stability (Current)

**Next Steps:**
- [ ] Phase 8: Advanced AI Features (Voice Mode, Vision, Deep Research)

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

*Built with 💜 by Madhur Tyagi*
