"""
Nexus AI - Quality Checker Tool
LLM-based quality assessment for content
"""

from typing import Dict, Any, Optional
from tools.base_tool import BaseTool, ToolRegistry
from llm.llm_manager import llm_manager


@ToolRegistry.register
class QualityCheckerTool(BaseTool):
    """
    Tool for LLM-based quality assessment of content.
    Uses AI to evaluate quality beyond automated checks.
    """
    
    QUALITY_PROMPT = """Evaluate the following content for quality.

Content Type: {content_type}
Expected Quality Level: {expected_quality}
Original Task: {original_task}

Content to Review:
---
{content}
---

Evaluate based on:
1. **Accuracy** - Is the information correct and factual?
2. **Completeness** - Does it fully address the task/requirements?
3. **Clarity** - Is it easy to understand?
4. **Professionalism** - Is the tone and presentation appropriate?
5. **Errors** - Are there any mistakes, bugs, or issues?

Provide your response in this format:
SCORES:
- Accuracy: X/10
- Completeness: X/10
- Clarity: X/10
- Professionalism: X/10
- Error-Free: X/10
- Overall: X/10

ISSUES:
- [List any critical issues found]

STRENGTHS:
- [List positive aspects]

SUGGESTIONS:
- [Specific improvements recommended]

VERDICT: PASS/FAIL
"""

    COMPARISON_PROMPT = """Compare these two versions of content and identify improvements or regressions.

Version 1 (Original):
---
{output1}
---

Version 2 (Updated):
---
{output2}
---

Analyze:
1. What improved in Version 2?
2. What regressed (got worse) in Version 2?
3. What remained the same?
4. Which version is better overall?

Provide your response in this format:
IMPROVEMENTS:
- [List improvements]

REGRESSIONS:
- [List what got worse]

UNCHANGED:
- [Key aspects that stayed the same]

BETTER_VERSION: 1 or 2
IMPROVEMENT_SCORE: X/10 (how much better is the preferred version)
"""

    def __init__(self):
        super().__init__(
            name="quality_checker",
            description="Use AI to assess content quality and provide detailed feedback"
        )
    
    def execute(
        self, 
        content: str, 
        expected_quality: str = "high",
        content_type: str = "general",
        original_task: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Perform LLM-based quality assessment.
        
        Args:
            content: The content to evaluate
            expected_quality: Quality level expected (low, medium, high, excellent)
            content_type: Type of content being evaluated
            original_task: The original task that produced this content
            
        Returns:
            Quality assessment report
        """
        prompt = self.QUALITY_PROMPT.format(
            content=content[:5000],  # Limit content length
            expected_quality=expected_quality,
            content_type=content_type,
            original_task=original_task or "Not specified"
        )
        
        try:
            response = llm_manager.generate(
                prompt=prompt,
                system_prompt="You are a quality assurance expert who evaluates content thoroughly and fairly.",
                temperature=0.3  # Lower temperature for consistent evaluation
            )
            
            # Parse the response
            return self._parse_quality_response(response)
            
        except Exception as e:
            return {
                "error": str(e),
                "scores": {},
                "overall_score": 0,
                "verdict": "ERROR",
                "issues": [f"Quality check failed: {str(e)}"],
                "suggestions": []
            }
    
    def compare_outputs(self, output1: str, output2: str) -> Dict[str, Any]:
        """
        Compare two versions of output to identify improvements or regressions.
        
        Args:
            output1: First version (usually original)
            output2: Second version (usually updated)
            
        Returns:
            Comparison report
        """
        prompt = self.COMPARISON_PROMPT.format(
            output1=output1[:3000],
            output2=output2[:3000]
        )
        
        try:
            response = llm_manager.generate(
                prompt=prompt,
                system_prompt="You are an analyst comparing two versions of content.",
                temperature=0.3
            )
            
            return self._parse_comparison_response(response)
            
        except Exception as e:
            return {
                "error": str(e),
                "improvements": [],
                "regressions": [],
                "better_version": None,
                "improvement_score": 0
            }
    
    def _parse_quality_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM quality assessment response."""
        result = {
            "raw_response": response,
            "scores": {},
            "overall_score": 0,
            "issues": [],
            "strengths": [],
            "suggestions": [],
            "verdict": "UNKNOWN"
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse scores
            if 'Accuracy:' in line:
                result["scores"]["accuracy"] = self._extract_score(line)
            elif 'Completeness:' in line:
                result["scores"]["completeness"] = self._extract_score(line)
            elif 'Clarity:' in line:
                result["scores"]["clarity"] = self._extract_score(line)
            elif 'Professionalism:' in line:
                result["scores"]["professionalism"] = self._extract_score(line)
            elif 'Error-Free:' in line:
                result["scores"]["error_free"] = self._extract_score(line)
            elif 'Overall:' in line:
                result["overall_score"] = self._extract_score(line)
            
            # Parse sections
            elif line.startswith('ISSUES:'):
                current_section = 'issues'
            elif line.startswith('STRENGTHS:'):
                current_section = 'strengths'
            elif line.startswith('SUGGESTIONS:'):
                current_section = 'suggestions'
            elif line.startswith('VERDICT:'):
                verdict = line.replace('VERDICT:', '').strip().upper()
                result["verdict"] = "PASS" if "PASS" in verdict else "FAIL"
                current_section = None
            elif line.startswith('- ') and current_section:
                item = line[2:].strip()
                if item and item not in ['None', 'N/A', '']:
                    result[current_section].append(item)
        
        # Calculate overall if not provided
        if result["overall_score"] == 0 and result["scores"]:
            scores = list(result["scores"].values())
            result["overall_score"] = sum(scores) / len(scores)
        
        # Convert to 0-100 scale
        result["quality_score"] = result["overall_score"] * 10
        
        return result
    
    def _parse_comparison_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM comparison response."""
        result = {
            "raw_response": response,
            "improvements": [],
            "regressions": [],
            "unchanged": [],
            "better_version": None,
            "improvement_score": 0
        }
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('IMPROVEMENTS:'):
                current_section = 'improvements'
            elif line.startswith('REGRESSIONS:'):
                current_section = 'regressions'
            elif line.startswith('UNCHANGED:'):
                current_section = 'unchanged'
            elif line.startswith('BETTER_VERSION:'):
                version = line.replace('BETTER_VERSION:', '').strip()
                result["better_version"] = int(version) if version.isdigit() else None
            elif line.startswith('IMPROVEMENT_SCORE:'):
                result["improvement_score"] = self._extract_score(line)
            elif line.startswith('- ') and current_section:
                item = line[2:].strip()
                if item and item not in ['None', 'N/A', '']:
                    result[current_section].append(item)
        
        return result
    
    def _extract_score(self, line: str) -> float:
        """Extract numeric score from a line like 'Accuracy: 8/10'."""
        import re
        match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', line)
        if match:
            return float(match.group(1))
        
        # Try just extracting a number
        match = re.search(r'(\d+(?:\.\d+)?)', line)
        if match:
            return float(match.group(1))
        
        return 0.0
