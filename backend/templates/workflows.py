"""
Nexus AI - Built-in Workflow Templates
Pre-defined project structures for various domains
"""

from typing import List, Dict, Any

BUILT_IN_TEMPLATES: List[Dict[str, Any]] = [
    {
        "name": "Software Development",
        "category": "Technology",
        "description": "Standard software development lifecycle including architecture, implementation, and quality assurance.",
        "icon": "💻",
        "structure": [
            {
                "name": "Phase 1: Architecture & Planning",
                "tasks": [
                    {"description": "Define system architecture and database schema", "agent": "CodeAgent"},
                    {"description": "Research best technologies and libraries for the stack", "agent": "ResearchAgent"}
                ]
            },
            {
                "name": "Phase 2: Core Implementation",
                "tasks": [
                    {"description": "Implement core backend API endpoints", "agent": "CodeAgent"},
                    {"description": "Develop main frontend components and state management", "agent": "CodeAgent"}
                ]
            },
            {
                "name": "Phase 3: Integration & QA",
                "tasks": [
                    {"description": "Integrate frontend with backend APIs", "agent": "CodeAgent"},
                    {"description": "Perform comprehensive testing and bug fixing", "agent": "QAAgent"}
                ]
            }
        ]
    },
    {
        "name": "Content Marketing Campaign",
        "category": "Marketing",
        "description": "Full content strategy from research to creation and distribution planning.",
        "icon": "📝",
        "structure": [
            {
                "name": "Phase 1: Market Research",
                "tasks": [
                    {"description": "Analyze competitor content and identify gaps", "agent": "ResearchAgent"},
                    {"description": "Identify target audience interests and SEO keywords", "agent": "ResearchAgent"}
                ]
            },
            {
                "name": "Phase 2: Content Creation",
                "tasks": [
                    {"description": "Write high-quality blog posts and articles", "agent": "ContentAgent"},
                    {"description": "Create social media copy and email newsletters", "agent": "ContentAgent"}
                ]
            },
            {
                "name": "Phase 3: Review & Optimization",
                "tasks": [
                    {"description": "Review content for brand consistency and SEO", "agent": "ContentAgent"},
                    {"description": "Develop a distribution and promotion strategy", "agent": "ManagerAgent"}
                ]
            }
        ]
    },
    {
        "name": "Data Analysis & Insights",
        "category": "Data Science",
        "description": "End-to-end data processing, statistical analysis, and business intelligence reporting.",
        "icon": "📊",
        "structure": [
            {
                "name": "Phase 1: Data Preparation",
                "tasks": [
                    {"description": "Gather and clean raw datasets from identified sources", "agent": "DataAgent"},
                    {"description": "Perform exploratory data analysis (EDA)", "agent": "DataAgent"}
                ]
            },
            {
                "name": "Phase 2: Statistical Modeling",
                "tasks": [
                    {"description": "Apply statistical models and identify correlations", "agent": "DataAgent"},
                    {"description": "Validate findings against business benchmarks", "agent": "ResearchAgent"}
                ]
            },
            {
                "name": "Phase 3: Insights Generation",
                "tasks": [
                    {"description": "Create a comprehensive data report with visualizations", "agent": "ContentAgent"},
                    {"description": "Present actionable business recommendations", "agent": "ManagerAgent"}
                ]
            }
        ]
    },
    {
        "name": "Customer Support Automation",
        "category": "Customer Success",
        "description": "Design and implement an automated support system including knowledge base and chatbot triggers.",
        "icon": "🤖",
        "structure": [
            {
                "name": "Phase 1: Requirement Analysis",
                "tasks": [
                    {"description": "Identify common support queries and pain points", "agent": "ResearchAgent"},
                    {"description": "Define the technical architecture for the automation", "agent": "CodeAgent"}
                ]
            },
            {
                "name": "Phase 2: Knowledge Base & Flows",
                "tasks": [
                    {"description": "Draft comprehensive documentation for standard solutions", "agent": "ContentAgent"},
                    {"description": "Define logic flows for automated responses", "agent": "ManagerAgent"}
                ]
            },
            {
                "name": "Phase 3: Implementation",
                "tasks": [
                    {"description": "Implement API triggers for the automated bot", "agent": "CodeAgent"},
                    {"description": "Review and refine responses against user feedback", "agent": "QAAgent"}
                ]
            }
        ]
    },
    {
        "name": "Product Launch Strategy",
        "category": "Business",
        "description": "Plan the marketing and operations side of a new product launch.",
        "icon": "🚀",
        "structure": [
            {
                "name": "Phase 1: Strategic Planning",
                "tasks": [
                    {"description": "Define product goals and KPIs", "agent": "ManagerAgent"},
                    {"description": "Research market competitors and pricing strategies", "agent": "ResearchAgent"}
                ]
            },
            {
                "name": "Phase 2: Marketing Assets",
                "tasks": [
                    {"description": "Write product descriptions and marketing copy", "agent": "ContentAgent"},
                    {"description": "Plan social media and email outreach campaigns", "agent": "ContentAgent"}
                ]
            },
            {
                "name": "Phase 3: Operations & Launch",
                "tasks": [
                    {"description": "Finalize launch schedule and distribution list", "agent": "ManagerAgent"},
                    {"description": "Coordinate internal team for the launch day tasks", "agent": "ManagerAgent"}
                ]
            }
        ]
    }
]
