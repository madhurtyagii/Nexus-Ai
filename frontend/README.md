# Nexus AI Frontend

The modern, responsive interface for the Nexus AI workspace. Built with **React 18**, **Vite**, and **TailwindCSS**.

## ✨ Features

- **Project Management Dashboard**:
  - View all active projects and their status.
  - "Project Wizard" for easy 3-step project creation (`Name -> Description -> Review`).
  
- **Detail View**:
  - **Dynamic Timeline**: Visualizes project phases and progress.
  - **Real-time Status**: Polls the backend to show live agent activity (e.g., "Researching", "Coding").
  - **Execution Control**: Start, pause, or delete projects.

- **Responsive Design**:
  - Beautiful dark mode UI with glassmorphism effects.
  - Fully responsive for various screen sizes.

---

## 🛠️ Setup & Run

### Prerequisites
- Node.js 18+
- NPM

### Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start Dev Server**:
   ```bash
   npm run dev
   ```
   Access the app at `http://localhost:5173`.

---

## 📂 Folder Structure

```
src/
├── components/
│   ├── projects/     # Project UI (Wizard, Timeline, Card)
│   ├── chat/         # Chat interface
│   └── agents/       # Agent visualization
├── pages/
│   ├── Projects.jsx      # Main dashboard
│   ├── ProjectDetail.jsx # Detailed execution view
│   └── Login.jsx         # Auth pages
├── services/         # API integration (axios)
└── context/          # Global state (AuthContext)
```
