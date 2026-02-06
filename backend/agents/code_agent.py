"""Nexus AI - Code Agent.

This module implements the CodeAgent, which focuses on automated programming 
tasks including code generation, debugging, review, and explanation 
across multiple languages.
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry


@AgentRegistry.register
class CodeAgent(BaseAgent):
    """Agent specialized in code generation and debugging.
    
    The CodeAgent provides expert-level programming assistance, including 
    writing implementation code, fixing bugs from provided snippets, 
    performing security and performance reviews, and explaining complex 
    logic structures.
    
    Attributes:
        name: Agent identifier ("CodeAgent").
        role: Description of the agent's purpose.
        system_prompt: Detailed instructions on coding standards.
        SUPPORTED_LANGUAGES: List of languages with specialized support.
        
    Example:
        >>> agent = CodeAgent(llm_manager, db_session)
        >>> result = agent.execute({"task": "Write a Python function for Fibonacci"})
        >>> print(result["output"]["code"])
    """
    
    DEFAULT_ROLE = "Code generation and debugging"
    
    SYSTEM_PROMPT = """You are an expert programmer and code assistant. Your capabilities include:

1. **Code Generation**: Write clean, efficient, well-documented code in any language
2. **Debugging**: Find and fix bugs in code
3. **Code Review**: Analyze code for issues, best practices, and improvements
4. **Explanation**: Explain how code works clearly

Always:
- Write clean, readable code with proper formatting
- Include comments and docstrings
- Handle errors appropriately
- Follow language-specific best practices
- Test your code mentally before returning

When returning code, use markdown code blocks with the language specified."""

    SUPPORTED_LANGUAGES = ["python", "javascript", "java", "cpp", "go", "rust", "typescript", "html", "css"]

    def __init__(
        self,
        llm_manager=None,
        db_session=None,
        tools: List[Any] = None
    ):
        super().__init__(
            name="CodeAgent",
            role=self.DEFAULT_ROLE,
            system_prompt=self.SYSTEM_PROMPT,
            llm_manager=llm_manager,
            db_session=db_session,
            tools=tools or []
        )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution entry point for all code-related tasks.
        
        Detects the intent (generate, debug, review, explain) from the 
        input data and routes to the appropriate internal method.
        
        Args:
            input_data: A dictionary containing:
                - task/prompt (str): The primary coding requirement.
                - code (str, optional): Snippet to be analyzed or fixed.
                - file_id (int, optional): ID of a file to read as context.
                
        Returns:
            dict: Results of the coding operation, including code, 
                language, and explanations.
        """
        self.start_execution()
        
        try:
            # Extract task/prompt
            task = (
                input_data.get("task") or 
                input_data.get("prompt") or 
                input_data.get("original_prompt", "")
            )
            code = input_data.get("code", "")
            file_id = input_data.get("file_id")

            # If file_id is provided, resolve it
            if file_id and not code:
                file_result = self._read_file_content(file_id)
                if file_result.get("success"):
                    code = file_result.get("content") or str(file_result.get("data", ""))
                    input_data["code"] = code # Update input_data for downstream methods
                    self.log_action("file_loaded_as_code", {"file_id": file_id})
            
            if not task:
                return self.format_output(None, status="error", error="No coding task provided")
            
            # Determine task type
            task_lower = task.lower()
            
            print(f"🔍 CodeAgent.execute: task_lower[:200] = {task_lower[:200]}")
            
            if any(word in task_lower for word in ["fix", "debug", "error", "bug", "issue"]):
                print("🔍 CodeAgent: Taking DEBUG path")
                result = self._debug_code(task, input_data.get("code", ""))
            elif any(word in task_lower for word in ["review", "check", "analyze", "audit"]):
                print("🔍 CodeAgent: Taking REVIEW path")
                result = self._review_code(task, input_data.get("code", ""))
            elif any(word in task_lower for word in ["explain", "what does", "how does"]):
                print("🔍 CodeAgent: Taking EXPLAIN path")
                result = self._explain_code(task, input_data.get("code", ""))
            else:
                # Default: generate code
                print("🔍 CodeAgent: Taking GENERATE path")
                result = self._generate_code(task)
            
            self.end_execution()
            return self.format_output(result)
            
        except Exception as e:
            self.log_action("code_error", {"error": str(e)})
            self.end_execution()
            return self.format_output(None, status="error", error=str(e))
    
    def _generate_code(self, task: str) -> Dict[str, Any]:
        """Generates implementation code based on a task description.
        
        Args:
            task: Comprehensive description of the code to be written.
            
        Returns:
            dict: Generated code, detected language, and an explanation.
        """
        self.log_action("generating_code", {"task": task[:100]})
        
        # Detect language from task - prioritize explicit mentions
        language = self._detect_language(task)
        
        # Extract just the core task, removing any code from conversation history
        core_task = task
        original_task_description = ""
        
        if "Current request:" in task:
            current_request = task.split("Current request:")[-1].strip()
            if "Note:" in current_request:
                current_request = current_request.split("Note:")[0].strip()
            
            # Check if this is a "write the same in X" type request
            if any(phrase in current_request.lower() for phrase in ["same", "that in", "it in", "convert", "rewrite"]):
                # Try to find what the original task was about
                if "Previous conversation:" in task:
                    prev_part = task.split("Previous conversation:")[1].split("Current request:")[0]
                    # Look for the first user message which usually contains the task
                    if "User:" in prev_part:
                        first_user_msg = prev_part.split("User:")[1].split("Assistant:")[0].strip()
                        # This is likely "write a simple calculator" or similar
                        original_task_description = first_user_msg
                
                # Build a clean prompt without the actual code
                if original_task_description:
                    core_task = f"{original_task_description} (in {language.upper()})"
                else:
                    core_task = current_request
            else:
                core_task = current_request
        
        print(f"🔧 CodeAgent: Detected language: {language}, Core task: {core_task[:100]}")
        
        prompt = f"""You are a code generator. Generate ONLY {language.upper()} code.

TASK: {core_task}

IMPORTANT INSTRUCTIONS:
1. Return EXACTLY ONE code block with complete, working {language.upper()} code
2. Start with a 1-2 sentence explanation, then the code block
3. The code must be complete and runnable - not fragments
4. Use proper {language.upper()} syntax and best practices
5. Include comments inside the code

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
Brief explanation of what this code does.

```{language}
// Your complete code here
```

DO NOT use multiple code blocks. DO NOT use inline code. Return ONE complete code block."""

        response = self.generate_response(prompt, use_cache=False)
        
        if not response:
            return {
                "code": "",
                "language": language,
                "explanation": "Failed to generate code",
                "tested": False
            }
        
        # Extract code from response
        code = self._extract_code_from_markdown(response)
        
        # If Python, try to test it
        tested = False
        test_output = None
        
        if language == "python" and code:
            test_result = self._test_python_code(code)
            tested = test_result.get("success", False)
            test_output = test_result.get("stdout") or test_result.get("error")
            
            # If test failed, try to fix
            if not tested and test_result.get("error"):
                self.log_action("fixing_code", {"error": test_result["error"][:100]})
                fixed = self._attempt_fix(code, test_result["error"], language)
                if fixed:
                    code = fixed["code"]
                    tested = fixed.get("tested", False)
                    test_output = fixed.get("test_output")
        
        # Generate explanation
        explanation = self._get_code_explanation(code, language)
        
        return {
            "code": code,
            "language": language,
            "explanation": explanation,
            "tested": tested,
            "test_output": test_output
        }
    
    def _debug_code(self, task: str, code: str = "") -> Dict[str, Any]:
        """
        Debug and fix code.
        """
        self.log_action("debugging_code", {"task": task[:100]})
        
        # Extract code from task if not provided separately
        if not code:
            code = self._extract_code_from_markdown(task)
        
        if not code:
            # Ask LLM to identify the code from the description
            return self._generate_code(task)
        
        language = self._detect_language(task) or "python"
        
        prompt = f"""Debug and fix this {language} code:

```{language}
{code}
```

Task/Error description: {task}

Identify the issue(s), fix them, and explain what was wrong.
Return the fixed code in a markdown code block."""

        response = self.generate_response(prompt, use_cache=False)
        
        if not response:
            return {
                "original_code": code,
                "fixed_code": code,
                "issues_found": [],
                "explanation": "Failed to debug code"
            }
        
        fixed_code = self._extract_code_from_markdown(response)
        
        # Parse explanation from response
        explanation = response.replace(f"```{language}\n{fixed_code}\n```", "").strip()
        
        # Test if Python
        tested = False
        if language == "python" and fixed_code:
            test_result = self._test_python_code(fixed_code)
            tested = test_result.get("success", False)
        
        return {
            "original_code": code,
            "fixed_code": fixed_code or code,
            "issues_found": self._extract_issues(response),
            "explanation": explanation[:500] if explanation else "Code debugged and fixed.",
            "tested": tested
        }
    
    def _review_code(self, task: str, code: str = "") -> Dict[str, Any]:
        """
        Review code for issues and improvements.
        """
        self.log_action("reviewing_code", {"task": task[:100]})
        
        if not code:
            code = self._extract_code_from_markdown(task)
        
        if not code:
            return {
                "issues": [],
                "suggestions": [],
                "overall_rating": 0,
                "explanation": "No code provided to review"
            }
        
        language = self._detect_language(task) or "python"
        
        prompt = f"""Review this {language} code:

```{language}
{code}
```

Analyze for:
1. **Bugs**: Potential bugs or errors
2. **Performance**: Efficiency issues
3. **Security**: Security vulnerabilities
4. **Best Practices**: Coding standards violations
5. **Readability**: Code clarity issues

Provide a rating from 1-10 and list specific issues and suggestions.
Format your response as JSON:
{{
    "rating": 8,
    "issues": ["Issue 1", "Issue 2"],
    "suggestions": ["Suggestion 1", "Suggestion 2"],
    "security_concerns": ["Security issue 1"],
    "summary": "Overall assessment"
}}"""

        response = self.generate_response(prompt, use_cache=False)
        
        try:
            # Parse JSON response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "issues": result.get("issues", []),
                    "suggestions": result.get("suggestions", []),
                    "security_concerns": result.get("security_concerns", []),
                    "overall_rating": result.get("rating", 5),
                    "summary": result.get("summary", "Review completed")
                }
        except:
            pass
        
        return {
            "issues": [],
            "suggestions": [response],
            "overall_rating": 5,
            "summary": response[:300]
        }
    
    def _explain_code(self, task: str, code: str = "") -> Dict[str, Any]:
        """
        Explain how code works.
        """
        self.log_action("explaining_code", {"task": task[:100]})
        
        if not code:
            code = self._extract_code_from_markdown(task)
        
        if not code:
            return {
                "summary": "No code provided to explain",
                "details": "",
                "complexity": "unknown"
            }
        
        language = self._detect_language(task) or "python"
        
        prompt = f"""Explain this {language} code in detail:

```{language}
{code}
```

Provide:
1. A brief summary (1-2 sentences)
2. Step-by-step explanation of what the code does
3. Time/space complexity if applicable

Be clear and beginner-friendly."""

        response = self.generate_response(prompt, use_cache=False)
        
        return {
            "summary": response[:200] if response else "Code explanation",
            "details": response or "Unable to explain code",
            "complexity": self._estimate_complexity(code)
        }
    
    def _test_python_code(self, code: str) -> Dict[str, Any]:
        """
        Test Python code using CodeExecutorTool.
        """
        tool = self._tool_map.get("code_executor")
        if not tool:
            return {"success": False, "error": "Code executor not available"}
        
        return tool.execute(code=code, timeout=5)
    
    def _attempt_fix(self, code: str, error: str, language: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to fix code that failed to execute.
        """
        prompt = f"""This {language} code has an error:

```{language}
{code}
```

Error: {error}

Fix the code. Return ONLY the fixed code in a markdown code block."""

        response = self.generate_response(prompt, use_cache=False)
        
        if response:
            fixed_code = self._extract_code_from_markdown(response)
            if fixed_code and fixed_code != code:
                # Test the fix
                if language == "python":
                    test_result = self._test_python_code(fixed_code)
                    return {
                        "code": fixed_code,
                        "tested": test_result.get("success", False),
                        "test_output": test_result.get("stdout") or test_result.get("error")
                    }
                return {"code": fixed_code, "tested": False}
        
        return None
    
    def _get_code_explanation(self, code: str, language: str) -> str:
        """
        Get a brief explanation of the generated code.
        """
        if not code:
            return ""
        
        prompt = f"""In 2-3 sentences, explain what this {language} code does:

```{language}
{code[:500]}
```"""

        response = self.generate_response(prompt, use_cache=True)
        return response[:300] if response else "Code generated successfully."
    
    def _extract_code_from_markdown(self, text: str) -> str:
        """
        Extract code from markdown code blocks.
        """
        if not text:
            return ""
        
        # Try to find code blocks
        pattern = r'```(?:\w+)?\n([\s\S]*?)```'
        matches = re.findall(pattern, text)
        
        if matches:
            return matches[0].strip()
        
        # Check if the entire text looks like code
        if any(kw in text for kw in ['def ', 'function ', 'class ', 'import ', 'const ']):
            return text.strip()
        
        return ""
    
    def _detect_language(self, text: str) -> str:
        """
        Detect programming language from task description.
        When conversation history is present, ONLY analyze the current request.
        """
        # If there's conversation context, extract ONLY the current request
        current_text = text
        if "Current request:" in text:
            current_text = text.split("Current request:")[-1].strip()
            # Remove any trailing context notes
            if "Note:" in current_text:
                current_text = current_text.split("Note:")[0].strip()
        
        text_lower = current_text.lower()
        
        # Language patterns - check these in the CURRENT REQUEST ONLY
        language_keywords = {
            'cpp': ['c++', 'cpp', 'c plus plus'],
            'python': ['python', 'py '],
            'javascript': ['javascript', 'js ', ' js', 'node'],
            'typescript': ['typescript', 'ts '],
            'java': [' java ', 'java code', 'in java'],
            'go': [' go ', 'golang', 'in go'],
            'rust': ['rust ', ' rust', 'in rust'],
            'ruby': ['ruby'],
            'php': ['php'],
            'swift': ['swift'],
            'kotlin': ['kotlin'],
            'csharp': ['c#', 'csharp', 'c sharp'],
            'sql': ['sql'],
            'bash': ['bash', 'shell'],
            'html': ['html'],
            'css': ['css'],
        }
        
        # Check for each language in the current request
        for lang, keywords in language_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return lang
        
        # If no match in current request and there's previous context, 
        # try to infer from the FULL text but prioritize explicit mentions
        if "Current request:" in text:
            full_text = text.lower()
            # Still check for explicit "in [language]" patterns in the request
            for lang, keywords in language_keywords.items():
                for keyword in keywords:
                    if keyword in current_text.lower():
                        return lang
        
        # Default to Python only if nothing else found
        return "python"
    
    def _extract_issues(self, text: str) -> List[str]:
        """
        Extract issue mentions from text.
        """
        issues = []
        
        # Look for numbered or bulleted lists
        patterns = [
            r'\d+\.\s*(.+)',  # 1. Issue
            r'[-*]\s*(.+)',   # - Issue
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            issues.extend([m.strip() for m in matches if len(m) > 10])
        
        return issues[:5]  # Limit to 5 issues
    
    def _estimate_complexity(self, code: str) -> str:
        """
        Estimate code complexity (basic heuristic).
        """
        if not code:
            return "unknown"
        
        # Count loops and nested structures
        loop_count = len(re.findall(r'\b(for|while)\b', code))
        nested = code.count('    ' * 3)  # Deep nesting
        
        if loop_count >= 2 or nested > 2:
            return "O(n²) or higher"
        elif loop_count == 1:
            return "O(n)"
        else:
            return "O(1)"
