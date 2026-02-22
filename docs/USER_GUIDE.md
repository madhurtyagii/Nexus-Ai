# Nexus AI - User Guide

Nexus AI is your autonomous AI workspace where agents collaborate to solve complex problems. This guide covers everything you need to know as a user.

## Core Concepts

### 1. The Manager
The Manager is the "brain" of Nexus AI. When you submit a request, it analyzes the complexity and decides whether to handle it as a single **Task** or a multi-phase **Project**.

### 2. Specialized Agents
You have a workforce of **8 specialized agents** with different skills:
- **ManagerAgent**: Plans and coordinates project workflows.
- **ResearcherAgent**: Gathers data from the web.
- **CodeAgent**: Writes and debugs high-quality code.
- **VisualAgent**: Analyzes and generates images/art.
- **ContentAgent**: Drafts emails, blogs, and reports.
- **DataAgent**: Provides statistical insights from your datasets.
- **QAAgent**: Verifies quality and logic across all outputs.
- **MemoryAgent**: Manages long-term context and preferences.

### 3. Semantic Memory
Nexus AI remembers your preferences and past interactions. This means:
- It learns your preferred writing tone and coding style.
- It can reference solutions from similar tasks you've done before.
- It understands your project context without you re-explaining it.

## Key Features

### ✨ Smart Tasks
Submit any natural language prompt. The system will:
- Determine which agent is best suited for the job.
- Execute the work in real-time.
- Automatically format code blocks, tables, and images.

### 🚀 Autonomous Projects
For complex goals, use Projects.
- **AI Planning**: The ManagerAgent breaks your goal into logical phases.
- **Workflow Execution**: Agents work sequentially or in parallel based on dependencies.
- **Real-time Monitoring**: Watch every step of the process through the Project Timeline.

### 🎨 Visual Intelligence
Describe any image you want to see, or upload a sketch for analysis. The **VisualAgent** uses state-of-the-art models (SDXL) to create art or provide deep visual insights directly in your chat.

### 🧠 Memory Exploration
Use the **Memory & Context** panel to:
- Browse your **Conversation History**.
- Configure **Learned Preferences**.
- Find **Related Tasks** using semantic search.

### 📂 File Management
Upload documents, images, or code files to projects. Agents can use these files as context for RAG-powered (Retrieval Augmented Generation) awareness.

## Tips for Success
- **Be Specific**: Detailed prompts give agents better context for higher accuracy.
- **Use Projects for Big Goals**: If a task seems like it has multiple steps, create a Project instead of a single Chat message.
- **Check Task Details**: Click on any task in the sidebar to see the full execution log and agent thinking process.

## Support
For technical issues, check the [Developer Guide](DEVELOPER_GUIDE.md) or the [Help Page](http://localhost:5173/help) in the app.
