"""
Nexus AI - Code Agent
AI agent specialized in code generation, debugging, and optimization
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry


@AgentRegistry.register
class CodeAgent(BaseAgent):
    """
    Code Agent - Specialized in code generation and debugging.
    
    Capabilities:
    - Generate code in multiple languages
    - Debug and fix code errors
    - Review code for issues
    - Explain code functionality
    - Optimize code performance
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
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code-related task.
        
        Args:
            input_data: Must contain "task", "prompt", or "original_prompt"
            
        Returns:
            Code result with generated/fixed code
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
            
            if any(word in task_lower for word in ["fix", "debug", "error", "bug", "issue"]):
                result = self._debug_code(task, input_data.get("code", ""))
            elif any(word in task_lower for word in ["review", "check", "analyze", "audit"]):
                result = self._review_code(task, input_data.get("code", ""))
            elif any(word in task_lower for word in ["explain", "what does", "how does"]):
                result = self._explain_code(task, input_data.get("code", ""))
            else:
                # Default: generate code
                result = self._generate_code(task)
            
            self.end_execution()
            return self.format_output(result)
            
        except Exception as e:
            self.log_action("code_error", {"error": str(e)})
            self.end_execution()
            return self.format_output(None, status="error", error=str(e))
    
    def _generate_code(self, task: str) -> Dict[str, Any]:
        """
        Generate code based on task description.
        """
        self.log_action("generating_code", {"task": task[:100]})
        
        # Detect language from task
        language = self._detect_language(task)
        
        prompt = f"""Generate {language} code for the following task:

{task}

Requirements:
1. Write clean, well-documented code
2. Include proper error handling
3. Add docstrings/comments explaining the code
4. Make it production-ready

Return the code in a markdown code block with the language specified."""

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
        """
        text_lower = text.lower()
        
        for lang in self.SUPPORTED_LANGUAGES:
            if lang in text_lower:
                return lang
        
        # Check for language-specific keywords
        if any(kw in text_lower for kw in ['javascript', 'js', 'node']):
            return "javascript"
        if any(kw in text_lower for kw in ['typescript', 'ts']):
            return "typescript"
        if any(kw in text_lower for kw in ['c++', 'cpp']):
            return "cpp"
        
        # Default to Python
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
