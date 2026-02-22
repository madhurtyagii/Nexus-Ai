# Nexus AI - Quickstart Guide

Get up and running with Nexus AI in less than 5 minutes.

## Prerequisites
- **Python**: 3.9 or higher
- **Node.js**: 18.x or higher
- **Redis**: Running locally or via Docker
- **LLM Account**: An API key from Groq (recommended) or OpenAI

## 1. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (or OPENAI_API_KEY)
python main.py
```

## 2. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

## 3. Your First Task

1. Open `http://localhost:5173` in your browser.
2. Sign up and log in.
3. In the chat box, type:
   > "Write a professional email inviting a client to a project kickoff meeting on Monday at 10 AM."
4. Watch as the **Manager** picks up the task and assigns it to the **ContentAgent**.
5. View the formatted result in the chat!

## 4. Your First Project

1. Click on **Projects** in the sidebar.
2. Click **Create Project**.
3. Name it "Launch New Feature" and describe it as:
   > "Research market trends for AI chatbots and create a technical specification for a new feature."
4. Click **Plan Project**. The **ManagerAgent** will brainstorm a multi-phase execution plan.
5. Review the plan and click **Execute Project**.
6. Track the real-time progress of all agents as they work together!

## 5. Visual Intelligence

Try generating an image directly in the chat:
> "Generate a futuristic cyberpunk office with neon lighting."

The **VisualAgent** will create the image and display it instantly.

## Next Steps
- Read the [User Guide](USER_GUIDE.md) for detailed features.
- Explore [Agent Roles](AGENTS.md) to understand who's doing what.
- Check the [Developer Guide](DEVELOPER_GUIDE.md) for technical deep-dives.
