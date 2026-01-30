"""
Nexus AI - Validation Tools
Tools for validating different types of content (code, text, data, research)
"""

import ast
import re
from typing import Dict, Any, List, Optional
from tools.base_tool import BaseTool, ToolRegistry


@ToolRegistry.register
class ValidationTool(BaseTool):
    """
    Tool for validating different types of content and outputs.
    Performs automated checks for quality, security, and correctness.
    """
    
    # Security patterns to detect
    DANGEROUS_IMPORTS = ['os', 'subprocess', 'shutil', 'sys', 'eval', 'exec']
    SQL_INJECTION_PATTERNS = [
        r"[\'\"].*OR.*[\'\"]",
        r"[\'\"].*--.*",
        r"[\'\"].*;.*DROP",
        r"[\'\"].*;.*DELETE",
    ]
    CREDENTIAL_PATTERNS = [
        r"password\s*=\s*['\"][^'\"]+['\"]",
        r"api_key\s*=\s*['\"][^'\"]+['\"]",
        r"secret\s*=\s*['\"][^'\"]+['\"]",
        r"token\s*=\s*['\"][A-Za-z0-9]+['\"]",
    ]
    
    def __init__(self):
        super().__init__(
            name="validator",
            description="Validate different types of content and outputs for quality, security, and correctness"
        )
        self.validation_rules = {
            "code": {
                "max_function_length": 50,
                "require_docstrings": True,
                "check_security": True
            },
            "content": {
                "min_words": 50,
                "require_structure": True,
                "check_grammar": True
            },
            "data_analysis": {
                "require_visualization": True,
                "check_statistics": True
            },
            "research": {
                "min_sources": 2,
                "require_citations": True
            }
        }
    
    def execute(
        self, 
        content: str, 
        content_type: str, 
        rules: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Validate content based on its type.
        
        Args:
            content: The content to validate
            content_type: Type of content (code, content, data_analysis, research)
            rules: Optional custom validation rules
            
        Returns:
            Validation results with score and issues
        """
        # Merge custom rules with defaults
        effective_rules = self.validation_rules.get(content_type, {})
        if rules:
            effective_rules.update(rules)
        
        # Route to appropriate validator
        validators = {
            "code": self._validate_code,
            "content": self._validate_content,
            "data_analysis": self._validate_data_analysis,
            "research": self._validate_research
        }
        
        validator = validators.get(content_type, self._validate_generic)
        return validator(content, effective_rules)
    
    def _validate_code(self, code: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code for syntax, security, and best practices."""
        issues = []
        warnings = []
        suggestions = []
        score = 100
        
        # 1. Syntax check (Python)
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(f"Syntax error at line {e.lineno}: {e.msg}")
            score -= 30
        
        # 2. Security checks
        if rules.get("check_security", True):
            # Check dangerous imports
            for dangerous in self.DANGEROUS_IMPORTS:
                if re.search(rf'\bimport\s+{dangerous}\b', code) or \
                   re.search(rf'\bfrom\s+{dangerous}\b', code):
                    if dangerous in ['eval', 'exec']:
                        issues.append(f"Security: Dangerous use of '{dangerous}' detected")
                        score -= 20
                    else:
                        warnings.append(f"Potentially risky import: '{dangerous}'")
                        score -= 5
            
            # Check SQL injection
            for pattern in self.SQL_INJECTION_PATTERNS:
                if re.search(pattern, code, re.IGNORECASE):
                    issues.append("Security: Potential SQL injection vulnerability")
                    score -= 15
                    break
            
            # Check hardcoded credentials
            for pattern in self.CREDENTIAL_PATTERNS:
                if re.search(pattern, code, re.IGNORECASE):
                    issues.append("Security: Hardcoded credentials detected")
                    score -= 20
                    break
        
        # 3. Best practices
        lines = code.split('\n')
        
        # Function length check
        max_length = rules.get("max_function_length", 50)
        in_function = False
        function_start = 0
        function_name = ""
        
        for i, line in enumerate(lines):
            if re.match(r'\s*def\s+\w+', line):
                if in_function:
                    length = i - function_start
                    if length > max_length:
                        warnings.append(f"Function '{function_name}' is {length} lines (recommended < {max_length})")
                        score -= 5
                in_function = True
                function_start = i
                match = re.search(r'def\s+(\w+)', line)
                function_name = match.group(1) if match else "unknown"
        
        # Docstring check
        if rules.get("require_docstrings", True):
            if '"""' not in code and "'''" not in code:
                warnings.append("No docstrings found - consider adding documentation")
                score -= 5
        
        # Check for exception handling
        if 'try:' not in code and 'except' not in code:
            if 'open(' in code or 'request' in code.lower():
                suggestions.append("Consider adding exception handling for I/O operations")
        
        # Check for type hints
        function_defs = re.findall(r'def\s+\w+\([^)]*\)', code)
        if function_defs:
            typed_functions = [f for f in function_defs if ':' in f or '->' in code]
            if len(typed_functions) < len(function_defs) / 2:
                suggestions.append("Consider adding type hints for better code quality")
        
        # 4. Common bugs
        # Unclosed files
        if 'open(' in code and 'with ' not in code:
            warnings.append("File opened without 'with' statement - potential resource leak")
            score -= 5
        
        # Infinite loops
        if re.search(r'while\s+True:', code) and 'break' not in code:
            warnings.append("Potential infinite loop detected (while True without break)")
            score -= 10
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, score),
            "suggestions": suggestions,
            "content_type": "code"
        }
    
    def _validate_content(self, text: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate text content for structure, grammar, and readability."""
        issues = []
        warnings = []
        suggestions = []
        score = 100
        
        # 1. Basic metrics
        words = text.split()
        word_count = len(words)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Check minimum length
        min_words = rules.get("min_words", 50)
        if word_count < min_words:
            issues.append(f"Content too short: {word_count} words (minimum: {min_words})")
            score -= 20
        
        # 2. Structure checks
        if rules.get("require_structure", True):
            # Check for headings
            has_headings = bool(re.search(r'^#+\s+.+|^[A-Z][^.]+:$', text, re.MULTILINE))
            if not has_headings and word_count > 200:
                warnings.append("Long content without headings - consider adding structure")
                score -= 5
            
            # Check for paragraphs
            paragraphs = text.split('\n\n')
            if len(paragraphs) < 2 and word_count > 100:
                suggestions.append("Consider breaking content into multiple paragraphs")
        
        # 3. Readability (simplified Flesch-Kincaid)
        if sentence_count > 0:
            avg_sentence_length = word_count / sentence_count
            if avg_sentence_length > 25:
                warnings.append(f"Average sentence length is {avg_sentence_length:.1f} words - consider shorter sentences")
                score -= 5
            elif avg_sentence_length < 5:
                warnings.append("Sentences may be too short - consider more detail")
                score -= 3
        
        # 4. Formatting checks
        # Excessive whitespace
        if re.search(r'\s{3,}', text):
            warnings.append("Excessive whitespace detected")
            score -= 2
        
        # Inconsistent capitalization
        sentences_lower = [s.strip() for s in sentences if s.strip()]
        uncapitalized = [s for s in sentences_lower if s and s[0].islower()]
        if uncapitalized and len(uncapitalized) > len(sentences_lower) / 4:
            warnings.append("Some sentences don't start with capital letters")
            score -= 3
        
        # 5. Content quality indicators
        # Check for placeholder text
        placeholders = ['TODO', 'FIXME', 'TBD', 'lorem ipsum', '[insert', '...']
        for placeholder in placeholders:
            if placeholder.lower() in text.lower():
                issues.append(f"Placeholder text found: '{placeholder}'")
                score -= 10
        
        # Check conclusion indicators
        has_conclusion = any(phrase in text.lower() for phrase in 
                           ['in conclusion', 'to summarize', 'in summary', 'finally,', 'overall,'])
        if word_count > 300 and not has_conclusion:
            suggestions.append("Consider adding a conclusion or summary")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, score),
            "suggestions": suggestions,
            "content_type": "content",
            "metrics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "paragraph_count": len([p for p in text.split('\n\n') if p.strip()])
            }
        }
    
    def _validate_data_analysis(self, analysis: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data analysis for statistical validity and visualization quality."""
        issues = []
        warnings = []
        suggestions = []
        score = 100
        
        analysis_lower = analysis.lower()
        
        # 1. Check for statistical validity claims
        correlation_claims = re.findall(r'correlat\w*', analysis_lower)
        causation_claims = re.findall(r'caus\w*|leads? to|results? in', analysis_lower)
        
        if correlation_claims and causation_claims:
            warnings.append("Both correlation and causation mentioned - ensure proper distinction")
            score -= 5
        
        # 2. Check for sample size mentions
        sample_patterns = re.findall(r'n\s*=\s*\d+|\d+\s*samples?|\d+\s*observations?', analysis_lower)
        if not sample_patterns and 'significant' in analysis_lower:
            warnings.append("Statistical significance claimed without sample size mentioned")
            score -= 5
        
        # 3. Check for visualization mentions
        if rules.get("require_visualization", True):
            viz_keywords = ['chart', 'graph', 'plot', 'visualization', 'figure', 'diagram']
            has_viz = any(keyword in analysis_lower for keyword in viz_keywords)
            if not has_viz:
                suggestions.append("Consider adding visualizations to support the analysis")
        
        # 4. Check for insights
        insight_patterns = re.findall(r'shows? that|indicates?|suggests?|reveals?|demonstrates?', analysis_lower)
        if not insight_patterns:
            warnings.append("Analysis may lack clear insights - consider adding interpretations")
            score -= 5
        
        # 5. Check for numbers and data
        numbers = re.findall(r'\d+\.?\d*%?', analysis)
        if len(numbers) < 3:
            warnings.append("Few numerical values found - ensure data is properly referenced")
            score -= 5
        
        # 6. Check for methodology
        method_keywords = ['method', 'approach', 'technique', 'algorithm', 'analysis']
        has_methodology = any(keyword in analysis_lower for keyword in method_keywords)
        if not has_methodology:
            suggestions.append("Consider explaining the methodology used")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, score),
            "suggestions": suggestions,
            "content_type": "data_analysis"
        }
    
    def _validate_research(self, research: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Validate research for source quality and completeness."""
        issues = []
        warnings = []
        suggestions = []
        score = 100
        
        research_lower = research.lower()
        
        # 1. Check for sources/citations
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, research)
        
        min_sources = rules.get("min_sources", 2)
        if len(urls) < min_sources:
            issues.append(f"Only {len(urls)} sources found (minimum: {min_sources})")
            score -= 15
        
        # 2. Check source quality
        credible_domains = ['.edu', '.gov', '.org', 'wikipedia', 'arxiv', 'doi.org']
        news_domains = ['bbc', 'nytimes', 'reuters', 'wsj', 'theguardian']
        credible_count = 0
        
        for url in urls:
            if any(domain in url for domain in credible_domains + news_domains):
                credible_count += 1
        
        if urls and credible_count < len(urls) / 2:
            warnings.append("Less than half of sources are from credible domains")
            score -= 10
        
        # 3. Check for recency indicators
        year_pattern = r'\b20[12]\d\b'
        years = re.findall(year_pattern, research)
        recent_years = [y for y in years if int(y) >= 2023]
        
        if years and not recent_years:
            warnings.append("No recent sources (2023+) found - information may be outdated")
            score -= 5
        
        # 4. Check completeness
        common_sections = ['introduction', 'background', 'findings', 'conclusion', 'summary']
        sections_found = sum(1 for section in common_sections if section in research_lower)
        
        if sections_found < 2:
            suggestions.append("Consider adding more structure (introduction, findings, conclusion)")
        
        # 5. Check for conflicting info
        contrast_words = ['however', 'but', 'although', 'despite', 'contrary', 'disagree']
        has_contrast = any(word in research_lower for word in contrast_words)
        if has_contrast:
            suggestions.append("Conflicting viewpoints detected - ensure proper analysis")
        
        # 6. Check for proper citations
        if rules.get("require_citations", True):
            citation_patterns = [
                r'\([^)]+\d{4}\)',  # (Author 2024)
                r'\[\d+\]',  # [1]
                r'according to',
                r'source:',
                r'cited'
            ]
            has_citations = any(re.search(pattern, research_lower) for pattern in citation_patterns)
            if not has_citations and urls:
                warnings.append("Sources found but no in-text citations")
                score -= 5
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, score),
            "suggestions": suggestions,
            "content_type": "research",
            "metrics": {
                "source_count": len(urls),
                "credible_sources": credible_count
            }
        }
    
    def _validate_generic(self, content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Generic validation for unknown content types."""
        issues = []
        warnings = []
        suggestions = []
        score = 100
        
        # Basic checks
        if not content or len(content.strip()) < 10:
            issues.append("Content is empty or too short")
            score -= 50
        
        # Check for placeholder content
        if any(p in content.lower() for p in ['todo', 'fixme', 'placeholder']):
            warnings.append("Placeholder content detected")
            score -= 10
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, score),
            "suggestions": suggestions,
            "content_type": "generic"
        }
