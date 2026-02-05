<p align="center">
  <img src="frontend/public/logo2.png" width="140" />
</p>

<h1 align="center">Nexus AI</h1>

<p align="center">
  <strong>Intelligence v2.0 — The Autonomous Multi-Agent Workspace</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.1-blueviolet" alt="Version: 2.1" />
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python" alt="Python: 3.11+" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi" alt="FastAPI: 0.100+" />
  <img src="https://img.shields.io/badge/React-18.x-61DAFB?logo=react" alt="React: 18.x" />
  <img src="https://img.shields.io/badge/PWA-Installable-8b5cf6" alt="PWA: Installable" />
</p>

**Nexus AI** is a cutting-edge, autonomous workspace that orchestrates a team of specialized AI agents to solve complex challenges through intelligent collaboration, semantic memory, and robust project orchestration.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Launch Commands
```bash
# Clone the repository
git clone https://github.com/madhurtyagii/nexus-ai.git
cd nexus-ai

# Start databases (Postgres & Redis)
docker-compose up -d

# Backend (Terminal 1)
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python main.py

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

### 🔗 Local URLs
| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |
| **PostgreSQL** | localhost:5432 |
| **Redis** | localhost:6379 |

---

## ✨ v2.1 Features

### 🎨 Premium UI/UX
- 🌟 **Ultra-Premium Dashboard** - Glassmorphism with animated gradients
- 🖱️ **Cursor Effects** - 6 customizable effects (Ring, Particles, Ribbon, Aurora, Stardust, Orbit)
- 🌓 **Global Theme System** - Dark/Light mode with radial transitions
- ⌨️ **Command Palette** - Ctrl+K for quick navigation
- 🔔 **Real-time Toasts** - Beautiful notifications with react-hot-toast

### ⚡ Real-time & Interactivity
- 📡 **WebSocket Live Mirroring** - Instant task updates with visual "Live" indicator
- 💬 **Direct Agent Chat** - Communicate directly with any agent
- 📊 **Agent Metrics** - Performance stats and activity charts
- 🎯 **Animated Components** - Framer Motion throughout

### 🧠 Intelligence & Workflow
- 🧠 **RAG for Files** - Semantic search: "Ask Your Files" natural language queries
- 🔀 **Visual Workflow Builder** - Drag-and-drop agent orchestration
- 📤 **Export Engine** - PDF, Markdown, DOCX, JSON exports

### 📱 Accessibility
- 📱 **PWA Support** - Install as standalone mobile/desktop app
- 🔽 **Mobile Bottom Nav** - Touch-friendly navigation
- 💅 **Responsive Design** - Safe-area support for notched phones

### ⚙️ Settings & Account
- 👤 **Editable Profile** - Change username & email in Settings
- 🔐 **Password Management** - Secure password updates
- 🎨 **Appearance Controls** - Theme & cursor effect preferences
- 🔑 **API Key Management** - View and manage API keys

---

## 🤖 The Specialist Team

| Agent | Role |
|-------|------|
| 👑 **Manager** | Orchestrates goals, creates plans, ensures quality |
| 🔍 **Researcher** | Web research via Tavily for deep insights |
| 💻 **Coder** | Logic, debugging, software architecture |
| ✍️ **Content Lead** | Creative writing, documentation |
| 🧪 **QA Analyst** | Tests outputs, validates requirements |
| 📊 **Data Agent** | Data analysis, visualization |
| 🧠 **Memory Guardian** | Semantic context and long-term memory |

---

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  React (Vite)   │────▶│  FastAPI        │
│  PWA Frontend   │     │  Backend        │
└─────────────────┘     └────────┬────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────┐      ┌───────────────┐       ┌───────────────┐
│  PostgreSQL   │      │     Redis     │       │   ChromaDB    │
│  (Database)   │      │ (Queue/Cache) │       │ (Vectors/RAG) │
└───────────────┘      └───────────────┘       └───────────────┘
```

---

## 🎨 Design Highlights

- **Glassmorphism** - Frosted glass effects with backdrop blur
- **Animated Gradients** - Mesh backgrounds with subtle animations
- **Neon Accents** - Cyan/purple color scheme with glow effects
- **Spring Animations** - Smooth, physics-based transitions
- **Dark Mode First** - Deep space theme with high contrast

---

## 📖 Documentation
- [📖 User Manual](USER_MANUAL.md)
- [🏗️ Architecture](docs/ARCHITECTURE.md)
- [🤖 Agents Guide](docs/AGENTS.md)
- [🔌 API Reference](backend/docs/API_GUIDE.md)
- [🔒 Security](SECURITY.md)
- [📝 Changelog](CHANGELOG.md)
- [🤝 Contributing](CONTRIBUTING.md)

---

## 🤝 Contributing & License
Nexus AI is released under the [MIT License](LICENSE). Contributions welcome!

Developed with ❤️ by [Madhur Tyagi](https://github.com/madhurtyagii)
