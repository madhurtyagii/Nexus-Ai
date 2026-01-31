# 🧠 Nexus AI: The Autonomous Multi-Agent Workspace

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![FastAPI: 0.100+](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![React: 18.x](https://img.shields.io/badge/React-18.x-61DAFB?logo=react)](https://react.dev/)
[![Docker: Supported](https://img.shields.io/badge/Docker-Supported-2496ED?logo=docker)](https://www.docker.com/)

**Nexus AI** is a world-class, autonomous workspace that orchestrates a team of specialized AI agents to solve complex problems through collaboration, semantic memory, and multi-phase project planning.

---

## ✨ Key Features

- **🚀 Autonomous Orchestration**: A central "brain" that decomposes high-level goals into executable tasks.
- **🤖 Specialized Agent Team**: Six unique agent personas (Manager, Researcher, Coder, Content, QA, Memory) working in harmony.
- **🧠 Semantic Long-Term Memory**: Learns your writing style, preferences, and builds on past solutions using vector embeddings.
- **🌐 Real-time WebSocket Monitoring**: Watch your agents think, communicate, and execute in real-time.
- **📂 Integrated File Management**: Securely upload and manage project assets that agents can use as context.
- **📈 Advanced Analytics**: Track memory usage, model performance, and agent efficiency.

---

## 🏗️ High-Level Architecture

Nexus AI is built on a resilient, decoupled architecture:

- **Backend**: FastAPI (Python) for high-performance orchestration and async task handling.
- **Frontend**: React (Vite) with a premium, responsive dark-mode design.
- **Data Layer**: SQLAlchemy (SQL) for state and Vector Store (Chroma/Qdrant) for semantic memory.
- **Resiliency**: Built-in Circuit Breakers, Exponential Backoff Retries, and Audit Logging.

---

## 🚦 Quick Start

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your OPENAI_API_KEY
python main.py
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to start orchestrating!

---

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- [🚀 Quickstart Guide](docs/QUICKSTART.md)
- [👤 User Guide](docs/USER_GUIDE.md)
- [🤖 Agent Definitions](docs/AGENTS.md)
- [📋 Workflow Templates](docs/TEMPLATES.md)
- [👨‍💻 Developer Guide](docs/DEVELOPER_GUIDE.md)
- [🏛️ System Architecture](docs/ARCHITECTURE.md)
- [🔌 API Reference](backend/docs/API_GUIDE.md)

---

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guidelines](CONTRIBUTING.md) to get started.

## ⚖️ License

Nexus AI is released under the [MIT License](LICENSE).

---

Developed with ❤️ by [Madhur Tyagi](https://github.com/madhurtyagii)
