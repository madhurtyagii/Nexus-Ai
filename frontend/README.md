# Nexus AI Frontend

React + Vite frontend for the Nexus AI multi-agent workspace.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Folder Structure

```
src/
├── components/     # Reusable React components
│   ├── chat/       # Chat interface components
│   ├── agents/     # Agent-related components
│   ├── memory/     # Memory UI components (Phase 5)
│   ├── tasks/      # Task display components
│   ├── layout/     # Layout components (Navbar, Sidebar)
│   └── common/     # Common UI components
├── pages/          # Route pages
├── hooks/          # Custom React hooks
├── services/       # API service layer
├── context/        # React context providers
├── utils/          # Utility functions
└── assets/         # Static assets (images, icons)
```
