# Nexus AI - Agents Guide

Nexus AI features a team of specialized agents that collaborate to achieve your goals. Each agent is powered by a common base class but has unique system prompts, tools, and processing logic.

## 🤖 Available Agents (Total: 8)

### 1. ManagerAgent
The "CEO" of the project workspace.
- **Primary Role**: Decomposes project goals into a multi-phase execution plan.
- **Capabilities**: Project planning, dependency management, workflow coordination.
- **Tools**: Plan analysis, phase sequencing.

### 2. ResearcherAgent
The information specialist.
- **Primary Role**: Performs deep web research and data gathering.
- **Capabilities**: Web searching, information extraction, source verification.
- **Tools**: Google Search API, Web Scraper.

### 3. CodeAgent
The senior developer.
- **Primary Role**: Writes, debugs, and optimizes code across various languages.
- **Capabilities**: Python/JS/SQL development, code refactoring, bug fixing.
- **Tools**: Local code executor (logic only), Shell analyzer.
- **Note**: Code blocks provided by CodeAgent are clean and ready for manual execution.

### 4. ContentAgent
The creative specialist.
- **Primary Role**: Generates high-quality written content.
- **Capabilities**: Email drafting, blog writing, documentation, scriptwriting.
- **Tools**: Formatting engine, tone analyzer.

### 5. QAAgent
The quality controller.
- **Primary Role**: Reviews the work of other agents to ensure it meets objectives.
- **Capabilities**: Code review, content proofreading, logic validation.
- **Tools**: Linter (for code), Sentiment analyzer.

### 6. MemoryAgent
The context keeper.
- **Primary Role**: Manages the storage and retrieval of long-term semantic context.
- **Capabilities**: Preference extraction, semantic search, context summarization.
- **Tools**: Vector DB interface (ChromaDB).

### 7. VisualAgent
The unified visual artist.
- **Primary Role**: Analyzes, generates, and edits images.
- **Capabilities**: 
    - **Analyze**: Describe and explain uploaded images/sketches.
    - **Generate**: Create stunning visuals from text prompts via SDXL.
    - **Chat**: Engaging, friendly conversation about visual concepts.
- **Tools**: Subprocess SDXL worker, Multimodal LLM (Vision).

### 8. DataAgent
The numbers specialist.
- **Primary Role**: Analyzes datasets and provides statistical insights.
- **Capabilities**: CSV/JSON analysis, trend detection, data visualization planning.
- **Tools**: Statistical analysis engine, Data formatter.

## 🛠️ How Agents Collaborate

When you submit a project:
1. The **ManagerAgent** creates a plan.
2. The **ResearcherAgent** gathers necessary background info.
3. The **CodeAgent**, **ContentAgent**, or **VisualAgent** performs the core work.
4. The **QAAgent** verifies the output.
5. Throughout the process, the **MemoryAgent** saves important context for future use.

## ⚙️ Customizing Agents
Agents can be customized via their system prompts in:
`backend/agents/<agent_name>_agent.py`

You can adjust their instructions to change their personality, strictness, or specific domain expertise.
