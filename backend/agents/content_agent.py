"""Nexus AI - Content Agent.

This module implements the ContentAgent, specialized in high-quality writing, 
copyediting, and documentation generation across various formats.
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry


@AgentRegistry.register
class ContentAgent(BaseAgent):
    """Agent specialized in writing, editing, and content generation.
    
    The ContentAgent handles a wide range of writing tasks, including 
    blog posts, technical documentation, marketing copy, and emails. It 
    ensures high readability, proper formatting, and adherence to specific 
    tones and styles.
    
    Attributes:
        name: Agent identifier ("ContentAgent").
        role: Description of the agent's purpose.
        system_prompt: Core instructions for high-quality writing.
        
    Example:
        >>> agent = ContentAgent(llm_manager, db_session)
        >>> result = agent.execute({"prompt": "Write a 500-word blog post about AI ethics"})
        >>> print(result["output"]["content"])
    """
    
    DEFAULT_ROLE = "Writing and content creation"
    
    SYSTEM_PROMPT = """You are a highly skilled and versatile professional writer. Your goal is to provide exceptional content while being engaging, talkative, and flexible.
    
    Your capabilities include:
    1. **Creative & Professional Writing**: Blog posts, articles, documentation, emails, essays, and more.
    2. **Intent-Focused Generation**: Always prioritize writing the actual content the user needs, rather than describing how to ask for it.
    3. **Adaptability**: Adjust your tone perfectly to match the user's request, from academic to casual.
    4. **Polishing**: Edit and improve existing text for clarity and impact.
    
    Always:
    - Be conversational and supportive. Explain your creative choices if they add value.
    - If a user asks for an essay or a report, write the full content immediately. 
    - Avoid being "robotic" or too literal with instructions that look like process meta-talk.
    - Use clean markdown for readability.
    
    Respond directly to the user as a helpful collaborator."""

    CONTENT_TYPES = ["blog", "documentation", "tutorial", "readme", "email", "social_media", "report", "essay"]
    TONE_OPTIONS = ["professional", "casual", "technical", "friendly", "formal", "academic"]

    def __init__(
        self,
        llm_manager=None,
        db_session=None,
        tools: List[Any] = None
    ):
        super().__init__(
            name="ContentAgent",
            role=self.DEFAULT_ROLE,
            system_prompt=self.SYSTEM_PROMPT,
            llm_manager=llm_manager,
            db_session=db_session,
            tools=tools or []
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates or improves content based on instructions.
er's request.
        
        Args:
            input_data: A dictionary containing:
                - task/prompt/original_prompt (str): The writing requirement.
                - context (dict, optional): Search results or data to include.
                - format (str, optional): Target format (e.g., markdown, html).
                - tone (str, optional): Desired voice (e.g., professional, casual).
                
        Returns:
            dict: The generated or edited content and associated metadata.
        """
        self.start_execution()
        
        try:
            # Extract parameters
            topic = (
                input_data.get("topic") or 
                input_data.get("task") or 
                input_data.get("user_prompt") or 
                input_data.get("task_description") or 
                input_data.get("prompt") or 
                input_data.get("original_prompt", "")
            )
            content_type = input_data.get("content_type", "").lower()
            tone = input_data.get("tone", "professional")
            file_id = input_data.get("file_id")
            context = input_data.get("context", "")

            # If file_id is provided, resolve it
            if file_id and not context:
                file_result = self._read_file_content(file_id)
                if file_result.get("success"):
                    context = file_result.get("content") or str(file_result.get("data", ""))
                    input_data["context"] = context
                    self.log_action("file_loaded_as_context", {"file_id": file_id})
            
            if not topic:
                return self.format_output(None, status="error", error="No topic provided")
            
            # Detect content type from topic if not specified
            if not content_type:
                content_type = self._detect_content_type(topic)
            
            mode = input_data.get("mode", "autonomous")
            self.log_action("creating_content", {
                "type": content_type,
                "topic": topic[:100],
                "tone": tone,
                "mode": mode
            })
            
            # Special handling for chat mode - be more direct and talkative
            if mode == "chat":
                result = self._handle_chat_request(topic, tone, content_type)
            else:
                # Route to appropriate method for autonomous pipeline
                if content_type == "blog":
                    result = self._write_blog_post(topic, tone)
                elif content_type == "documentation":
                    result = self._write_documentation(topic, input_data.get("context"))
                elif content_type == "tutorial":
                    result = self._write_tutorial(topic, input_data.get("skill_level", "beginner"))
                elif content_type == "readme":
                    result = self._write_readme(topic, input_data)
                elif content_type == "email":
                    result = self._write_email(topic, tone)
                else:
                    # Default: generic content
                    result = self._write_generic_content(topic, tone)
            
            self.end_execution()
            return self.format_output(result)
            
        except Exception as e:
            self.log_action("content_error", {"error": str(e)})
            self.end_execution()
            return self.format_output(None, status="error", error=str(e))
    
    def _write_blog_post(
        self, 
        topic: str, 
        tone: str = "professional",
        length: str = "medium"
    ) -> Dict[str, Any]:
        """
        Write a blog post.
        """
        length_guide = {
            "short": "300-500 words",
            "medium": "600-900 words",
            "long": "1000-1500 words"
        }
        
        prompt = f"""Write a blog post about: {topic}

Requirements:
- Tone: {tone}
- Length: {length_guide.get(length, "600-900 words")}
- Structure: 
  - Catchy title
  - Engaging introduction
  - 3-5 body sections with headings
  - Conclusion with key takeaways

Use markdown formatting with proper headings (##, ###).
Make it engaging and informative."""

        response = self.generate_response(prompt, use_cache=False)
        
        if not response:
            return {
                "title": "Untitled",
                "content": "Failed to generate blog post",
                "word_count": 0
            }
        
        # Extract title
        title = self._extract_title(response)
        
        # Calculate stats
        word_count = len(response.split())
        read_time = max(1, word_count // 200)
        
        return {
            "title": title,
            "content": response,
            "meta_description": self._generate_meta_description(topic, response),
            "tags": self._suggest_tags(topic),
            "word_count": word_count,
            "estimated_read_time": f"{read_time} min"
        }
    
    def _write_documentation(
        self, 
        topic: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Write technical documentation.
        """
        context_info = ""
        if context:
            if context.get("code"):
                context_info = f"\n\nCode to document:\n```\n{context['code'][:1000]}\n```"
            elif context.get("api"):
                context_info = f"\n\nAPI details: {context['api']}"
        
        prompt = f"""Write technical documentation for: {topic}{context_info}

Include these sections:
1. **Overview** - What it is and what it does
2. **Features** - Key features and capabilities
3. **Installation** (if applicable)
4. **Usage** - How to use with examples
5. **API Reference** (if applicable)
6. **Configuration** (if applicable)
7. **Troubleshooting** - Common issues

Use clear, technical writing style with markdown formatting."""

        response = self.generate_response(prompt, use_cache=False)
        
        sections = self._extract_sections(response)
        
        return {
            "documentation": response or "Documentation generation failed",
            "sections": sections,
            "word_count": len(response.split()) if response else 0
        }
    
    def _write_tutorial(
        self, 
        topic: str, 
        skill_level: str = "beginner"
    ) -> Dict[str, Any]:
        """
        Write a step-by-step tutorial.
        """
        prompt = f"""Write a {skill_level}-level tutorial about: {topic}

Structure:
1. **Introduction** - What you'll learn
2. **Prerequisites** - What you need to know/have
3. **Step 1, 2, 3...** - Numbered steps with clear instructions
4. **Code Examples** - Include working code examples
5. **Common Mistakes** - Things to avoid
6. **Summary** - What you've learned
7. **Next Steps** - Where to go from here

Make it educational and hands-on. Use markdown formatting."""

        response = self.generate_response(prompt, use_cache=False)
        
        steps = self._extract_steps(response)
        
        return {
            "tutorial": response or "Tutorial generation failed",
            "prerequisites": self._extract_prerequisites(response),
            "steps": steps,
            "difficulty": skill_level,
            "word_count": len(response.split()) if response else 0
        }
    
    def _write_readme(
        self, 
        project_name: str, 
        project_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive README file.
        """
        # Extract info
        description = project_info.get("description", project_name)
        features = project_info.get("features", [])
        install = project_info.get("install_command", "npm install" if "js" in project_name.lower() else "pip install")
        
        prompt = f"""Generate a professional GitHub README.md for a project called "{project_name}".

Project description: {description}
{f"Features: {features}" if features else ""}

Include these sections with proper markdown:
1. **Title** with badges (build status, version, license)
2. **Description** - What the project does
3. **Features** - Key features (bullet list)
4. **Installation** - How to install
5. **Usage** - Basic usage examples with code
6. **Configuration** - Optional settings
7. **Contributing** - How to contribute
8. **License** - MIT license

Make it professional and well-formatted for GitHub."""

        response = self.generate_response(prompt, use_cache=False)
        
        return {
            "readme": response or "# " + project_name,
            "sections": self._extract_sections(response),
            "word_count": len(response.split()) if response else 0
        }
    
    def _write_email(
        self, 
        topic: str, 
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Write a professional email.
        """
        prompt = f"""Write a {tone} email about: {topic}

Include:
- Subject line
- Professional greeting
- Clear body (2-3 paragraphs)
- Professional closing

Format as:
Subject: [subject]

[email body]"""

        response = self.generate_response(prompt, use_cache=False)
        
        # Extract subject
        subject = ""
        if "Subject:" in response:
            subject_match = re.search(r'Subject:\s*(.+)', response)
            if subject_match:
                subject = subject_match.group(1).strip()
        
        return {
            "subject": subject,
            "body": response or "Email generation failed",
            "tone": tone
        }
    
    def _write_generic_content(
        self, 
        topic: str, 
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Write generic content when type is not specified.
        """
        prompt = f"""Write content about: {topic}

Tone: {tone}

Create well-structured, informative content with:
- Clear introduction
- Organized body sections with headings
- Conclusion or summary

Use markdown formatting."""

        response = self.generate_response(prompt, use_cache=False)
        
        return {
            "content": response or "Content generation failed",
            "title": self._extract_title(response),
            "word_count": len(response.split()) if response else 0
        }

    def _handle_chat_request(self, topic: str, tone: str, content_type: str) -> Dict[str, Any]:
        """Handles direct chat requests with a more talkative and flexible approach."""
        prompt = f"""You are in a direct chat with a user. They want you to write something about: {topic}
        
CONTENT TYPE: {content_type}
TONE: {tone}

INSTRUCTIONS:
1. Start with a friendly, conversational opening (e.g., "I'd be happy to help you with that essay on teachers!")
2. Provide the FULL content requested immediately. 
3. If they ask for an essay, WRITE THE ESSAY. Do not explain how to ask for one.
4. End with a supportive closing.
5. Use markdown for structure.

Be talkative, helpful, and flexible."""

        response = self.generate_response(prompt, use_cache=False)
        
        return {
            "content": response,
            "title": self._extract_title(response),
            "summary": "Direct chat response generated."
        }
    
    def _detect_content_type(self, topic: str) -> str:
        """
        Detect content type from topic description.
        """
        topic_lower = topic.lower()
        
        if any(kw in topic_lower for kw in ["blog", "article", "post"]):
            return "blog"
        if any(kw in topic_lower for kw in ["document", "docs", "api", "reference"]):
            return "documentation"
        if any(kw in topic_lower for kw in ["tutorial", "guide", "how to", "learn"]):
            return "tutorial"
        if any(kw in topic_lower for kw in ["readme", "read me", "github"]):
            return "readme"
        if any(kw in topic_lower for kw in ["email", "mail", "message"]):
            return "email"
        if any(kw in topic_lower for kw in ["essay", "pape", "thesis", "report"]):
            return "essay"
        
        return "blog"  # Default
    
    def _extract_title(self, content: str) -> str:
        """
        Extract title from content.
        """
        if not content:
            return "Untitled"
        
        # Look for markdown title
        match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Use first line
        first_line = content.split('\n')[0].strip()
        return first_line[:100] if first_line else "Untitled"
    
    def _extract_sections(self, content: str) -> List[str]:
        """
        Extract section headings from content.
        """
        if not content:
            return []
        
        headings = re.findall(r'^#{1,3}\s+(.+)', content, re.MULTILINE)
        return headings[:10]
    
    def _extract_steps(self, content: str) -> List[str]:
        """
        Extract numbered steps from content.
        """
        if not content:
            return []
        
        steps = re.findall(r'(?:Step\s+)?(\d+)[.):]\s*(.+)', content)
        return [f"Step {num}: {desc.strip()}" for num, desc in steps[:10]]
    
    def _extract_prerequisites(self, content: str) -> List[str]:
        """
        Extract prerequisites from content.
        """
        prereqs = []
        in_prereq_section = False
        
        for line in content.split('\n'):
            if 'prerequisite' in line.lower():
                in_prereq_section = True
                continue
            if in_prereq_section:
                if line.startswith('#'):
                    break
                if line.strip().startswith('-') or line.strip().startswith('*'):
                    prereqs.append(line.strip()[1:].strip())
        
        return prereqs[:5]
    
    def _generate_meta_description(self, topic: str, content: str) -> str:
        """
        Generate SEO meta description.
        """
        # Use first 150 chars of content, cleaned
        if content:
            clean = re.sub(r'#.*\n', '', content)
            clean = re.sub(r'\[.*\]', '', clean)
            clean = ' '.join(clean.split()[:25])
            return clean[:150]
        return topic[:150]
    
    def _suggest_tags(self, topic: str) -> List[str]:
        """
        Suggest tags based on topic.
        """
        words = topic.lower().split()
        # Common tech terms to tag
        tech_terms = ['python', 'javascript', 'ai', 'machine learning', 'web', 'api', 
                      'database', 'cloud', 'devops', 'react', 'node', 'docker']
        
        tags = [word for word in words if word in tech_terms]
        
        # Add generic tags
        if not tags:
            tags = [words[0]] if words else ['general']
        
        return tags[:5]
