# 🎨 Nexus AI Frontend

<p align="center">
  <img src="https://img.shields.io/badge/Status-✅_Complete-success" alt="Status: Complete" />
  <img src="https://img.shields.io/badge/React-18.x-61DAFB?logo=react" alt="React" />
  <img src="https://img.shields.io/badge/Vite-5.x-646CFF?logo=vite" alt="Vite" />
  <img src="https://img.shields.io/badge/PWA-Installable-8b5cf6" alt="PWA" />
</p>

A premium, reactive dashboard for orchestrating an AI workforce. Built with React 18 and Vite.

---

## 🔗 Local URL
```
http://localhost:5173
```

---

## ✨ Features

### 🎨 Premium UI
- 🌟 **Glassmorphism Design** - Frosted glass effects with backdrop blur
- 🖱️ **6 Cursor Effects** - Ring, Particles, Ribbon, Aurora, Stardust, Orbit
- 🌓 **Global Theme System** - Dark/Light mode with radial transitions
- ⌨️ **Command Palette** - Ctrl+K quick navigation
- 🔔 **Toast Notifications** - Beautiful feedback with react-hot-toast

### ⚡ Real-time
- 📡 WebSocket live task updates with "Live" indicator
- 💬 Direct Agent Chat modal
- 📊 Agent performance metrics

### 🧠 Intelligence
- 🧠 **Ask Your Files** - RAG-powered semantic search
- 🔀 **Visual Workflow Builder** - Drag-and-drop agent orchestration
- 📤 Export projects to PDF/Markdown/DOCX/JSON

### 📱 Mobile
- 📱 PWA - Installable as standalone app
- 🔽 Bottom navigation for mobile
- 💅 Touch-optimized with safe-area support

### ⚙️ Settings
- 👤 **Editable Profile** - Change username & email
- 🎨 **Appearance** - Theme & cursor effect preferences
- 🔐 **Security** - Password management
- 🔑 **API Keys** - Groq provider switching

---

## 🧩 Key Views

| Page | Description |
|------|-------------|
| **Dashboard** | Command center with Quick Actions, Live status |
| **Tasks** | Searchable task list with real-time updates |
| **Agents** | **8 AI agents** with stats and direct chat |
| **Projects** | Project management with multi-phase execution |
| **Files** | File browser with RAG indexing & unified chat |
| **Settings** | Premium account & appearance preferences |
| **Workflow** | Visual node-based designer |

---

## 🚀 Setup

```bash
npm install
npm run dev
```

Expects backend at `http://localhost:8000`.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | React 18 (Vite) |
| Styling | Custom CSS + Glassmorphism |
| State | React Hooks + Context |
| Animation | Framer Motion |
| Icons | Lucide React |
| PWA | Service Worker + Manifest |
| Markdown | React Markdown + Syntax Highlighter |

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/       # MarkdownRenderer, Skeleton, etc.
│   │   ├── layout/       # Navbar, Sidebar
│   │   ├── projects/     # PhaseAccordion, Timeline, ActivityFeed
│   │   └── files/        # FileUpload, FileManager
│   ├── pages/            # Route pages
│   ├── context/          # AuthContext, ThemeContext
│   ├── services/         # API client
│   └── styles/           # Global CSS
└── public/               # Static assets
```

---

<p align="center">
  <strong>🎉 Project Completed — February 2026</strong>
</p>
