"""
Nexus AI - Seed Domain Knowledge
Populates ChromaDB with expert knowledge for each agent type
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory.vector_store import VectorStore
from memory.embeddings import EmbeddingManager
from logging_config import get_logger

logger = get_logger(__name__)


# Domain knowledge for each agent
AGENT_KNOWLEDGE = {
    "ResearchAgent": [
        {
            "topic": "web_search_best_practices",
            "content": """Web Search Best Practices:
1. Use specific, targeted search queries
2. Combine multiple search results for comprehensive coverage
3. Prioritize recent sources for time-sensitive topics
4. Cross-reference information from multiple sources
5. Look for primary sources when possible
6. Consider the credibility and bias of sources
7. Use quotation marks for exact phrase searches
8. Use site: operator to search specific domains"""
        },
        {
            "topic": "credible_sources",
            "content": """Credible Source Guidelines:
- Academic journals and peer-reviewed publications
- Official government websites (.gov)
- Established news organizations with editorial standards
- Industry-recognized institutions and associations
- Primary source documents and official reports
- Expert interviews and authoritative blogs
- Avoid: User-generated content without verification, outdated sources, biased advocacy sites"""
        },
        {
            "topic": "fact_checking",
            "content": """Fact-Checking Guidelines:
1. Verify claims with multiple independent sources
2. Check the date of information
3. Identify the original source of claims
4. Look for supporting evidence and data
5. Consider expert consensus on the topic
6. Be skeptical of sensational claims
7. Distinguish between facts, opinions, and analysis
8. Document sources for all factual claims"""
        }
    ],
    
    "CodeAgent": [
        {
            "topic": "coding_best_practices",
            "content": """Coding Best Practices:
1. Write clean, readable code with meaningful variable names
2. Follow DRY (Don't Repeat Yourself) principle
3. Keep functions small and focused on single responsibility
4. Write comprehensive docstrings and comments
5. Handle errors gracefully with try/except blocks
6. Use type hints for better code clarity
7. Follow language-specific style guides (PEP 8 for Python)
8. Write unit tests for critical functionality"""
        },
        {
            "topic": "design_patterns",
            "content": """Common Design Patterns:
- Singleton: Ensure only one instance of a class
- Factory: Create objects without specifying exact class
- Observer: Subscribe to events from a subject
- Strategy: Define family of algorithms, make interchangeable
- Decorator: Add behavior to objects dynamically
- Repository: Abstract data layer from business logic
- Dependency Injection: Provide dependencies from outside
- Builder: Construct complex objects step by step"""
        },
        {
            "topic": "security_guidelines",
            "content": """Security Best Practices:
1. Never hardcode secrets or API keys
2. Validate and sanitize all user input
3. Use parameterized queries to prevent SQL injection
4. Implement proper authentication and authorization
5. Use HTTPS for all communications
6. Keep dependencies updated
7. Follow principle of least privilege
8. Log security-relevant events
9. Encrypt sensitive data at rest and in transit"""
        },
        {
            "topic": "debugging_techniques",
            "content": """Debugging Techniques:
1. Read error messages carefully - they often point to the issue
2. Use print statements or logging to trace execution
3. Use debugger breakpoints to inspect state
4. Simplify the problem - create minimal reproduction
5. Check recent changes - use git diff
6. Rubber duck debugging - explain the problem out loud
7. Take breaks - fresh perspective helps
8. Check documentation and Stack Overflow"""
        }
    ],
    
    "ContentAgent": [
        {
            "topic": "writing_style_guide",
            "content": """Writing Style Guidelines:
1. Know your audience - adjust tone and complexity
2. Use active voice for clearer, more engaging writing
3. Keep sentences and paragraphs concise
4. Use headings and bullet points for scanability
5. Start with the most important information
6. Use transitions to connect ideas smoothly
7. Avoid jargon unless writing for experts
8. Edit ruthlessly - remove unnecessary words"""
        },
        {
            "topic": "content_structure",
            "content": """Content Structure Templates:
- Blog Post: Hook → Problem → Solution → Examples → Conclusion → CTA
- Tutorial: Overview → Prerequisites → Steps → Code Examples → Summary
- Technical Doc: Purpose → Overview → Details → Examples → Troubleshooting
- Report: Executive Summary → Background → Analysis → Findings → Recommendations
- Email: Subject line → Greeting → Purpose → Details → Action items → Closing"""
        },
        {
            "topic": "grammar_rules",
            "content": """Essential Grammar Rules:
1. Subject-verb agreement
2. Proper use of their/there/they're, its/it's, your/you're
3. Correct comma usage (lists, introductory phrases, compound sentences)
4. Avoid sentence fragments and run-on sentences
5. Use consistent tense throughout
6. Proper apostrophe usage for possession
7. Parallel structure in lists
8. Proper semicolon and colon usage"""
        },
        {
            "topic": "seo_writing",
            "content": """SEO Writing Best Practices:
1. Include target keyword in title, headings, and first paragraph
2. Use natural keyword placement - avoid stuffing
3. Write compelling meta descriptions
4. Use descriptive, keyword-rich headings
5. Include internal and external links
6. Optimize images with alt text
7. Aim for comprehensive, valuable content
8. Use structured data when appropriate"""
        }
    ],
    
    "DataAgent": [
        {
            "topic": "statistical_methods",
            "content": """Key Statistical Methods:
- Descriptive: Mean, median, mode, standard deviation
- Correlation: Pearson, Spearman for relationship between variables
- Regression: Linear, logistic for prediction
- Hypothesis Testing: t-tests, chi-square, ANOVA
- Confidence Intervals: Estimate population parameters
- Always check assumptions before applying methods
- Consider sample size and statistical power
- Report effect sizes, not just p-values"""
        },
        {
            "topic": "visualization_best_practices",
            "content": """Data Visualization Best Practices:
- Bar charts: Compare categories
- Line charts: Show trends over time
- Scatter plots: Show relationships between variables
- Pie charts: Show parts of a whole (use sparingly)
- Histograms: Show distribution of single variable
- Always label axes clearly
- Use colors purposefully and accessibly
- Remove chart junk - keep it clean
- Tell a story with your visualization"""
        },
        {
            "topic": "data_cleaning",
            "content": """Data Cleaning Techniques:
1. Handle missing values (impute, drop, or flag)
2. Remove or correct duplicates
3. Standardize formats (dates, currencies, addresses)
4. Handle outliers appropriately
5. Validate data types and ranges
6. Check for consistency across related fields
7. Document all cleaning decisions
8. Keep original data, create cleaned copy"""
        },
        {
            "topic": "analysis_workflow",
            "content": """Data Analysis Workflow:
1. Define the question or problem clearly
2. Collect and explore the data
3. Clean and prepare the data
4. Perform exploratory data analysis (EDA)
5. Apply appropriate statistical methods
6. Visualize findings effectively
7. Draw conclusions and validate results
8. Communicate findings to stakeholders"""
        }
    ]
}


def seed_knowledge():
    """Seed ChromaDB with agent domain knowledge."""
    print("🧠 Seeding domain knowledge...")
    
    vector_store = VectorStore()
    embedding_manager = EmbeddingManager()
    
    total_added = 0
    
    for agent_name, knowledge_items in AGENT_KNOWLEDGE.items():
        print(f"\n📚 Seeding knowledge for {agent_name}...")
        
        for item in knowledge_items:
            topic = item["topic"]
            content = item["content"]
            
            # Generate embedding
            embedding = embedding_manager.generate_embedding(content)
            
            # Add to vector store
            memory_id = vector_store.add_memory(
                collection_name=VectorStore.DOMAIN_KNOWLEDGE,
                content=content,
                metadata={
                    "agent_name": agent_name,
                    "topic": topic,
                    "type": "domain_knowledge"
                },
                embedding=embedding
            )
            
            print(f"  ✅ Added: {topic}")
            total_added += 1
    
    print(f"\n✨ Successfully seeded {total_added} knowledge items!")
    
    # Print stats
    stats = vector_store.get_collection_stats(VectorStore.DOMAIN_KNOWLEDGE)
    print(f"📊 Collection stats: {stats}")


if __name__ == "__main__":
    seed_knowledge()
