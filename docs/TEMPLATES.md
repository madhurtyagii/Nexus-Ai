# Nexus AI - Workflow Templates Guide

Workflow templates are pre-defined project structures that help you get started quickly with common domains. Each template defines a series of phases and specialized tasks assigned to specific agents.

## 📋 Available Templates

### 💻 Software Development
A comprehensive lifecycle for building software.
- **Phase 1: Architecture & Planning**: Focuses on schemas and technology research. (CodeAgent, ResearchAgent)
- **Phase 2: Core Implementation**: Development of backend APIs and frontend components. (CodeAgent)
- **Phase 3: Integration & QA**: Wiring everything together and bug fixing. (CodeAgent, QAAgent)

### 📝 Content Marketing Campaign
For research-driven content creation.
- **Phase 1: Market Research**: Competitor analysis and SEO keyword identification. (ResearchAgent)
- **Phase 2: Content Creation**: High-quality blogs, articles, and social media copy. (ContentAgent)
- **Phase 3: Review & Optimization**: Brand consistency review and distribution strategy. (ContentAgent, ManagerAgent)

### 📊 Data Analysis & Insights
End-to-end data processing and reporting.
- **Phase 1: Data Preparation**: Gathering and cleaning raw datasets (EDA). (DataAgent)
- **Phase 2: Statistical Modeling**: Identifying correlations and validating findings. (DataAgent, ResearchAgent)
- **Phase 3: Insights Generation**: Comprehensive reporting and business recommendations. (ContentAgent, ManagerAgent)

### 🤖 Customer Support Automation
Building automated support systems and knowledge bases.
- **Phase 1: Requirement Analysis**: Identifying pain points and technical architecture. (ResearchAgent, CodeAgent)
- **Phase 2: Knowledge Base & Flows**: Documentation drafting and response logic. (ContentAgent, ManagerAgent)
- **Phase 3: Implementation**: API triggers and feedback-driven refinement. (CodeAgent, QAAgent)

### 🚀 Product Launch Strategy
Strategic and operational planning for new launches.
- **Phase 1: Strategic Planning**: Defining goals, KPIs, and market research. (ManagerAgent, ResearchAgent)
- **Phase 2: Marketing Assets**: Product descriptions and outreach campaigns. (ContentAgent)
- **Phase 3: Operations & Launch**: Finalizing schedules and internal coordination. (ManagerAgent)

## 🛠️ How to Use a Template

When creating a new project:
1. Select the **Template** option in the Project Wizard.
2. Choose the template that matches your goal.
3. Nexus AI will automatically populate your project plan with the pre-defined phases and tasks.
4. You can then review and modify the plan before execution.

## ➕ Creating Custom Templates

Developer can add new templates by modifying the `BUILT_IN_TEMPLATES` list in:
`backend/templates/workflows.py`

Custom templates allow you to standardize your organization's specific workflows and ensure consistency across AI-driven projects.
