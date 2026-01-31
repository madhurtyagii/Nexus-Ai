"""Nexus AI - Data Agent.

This module implements the DataAgent, which specializes in data analysis, 
statistical insights, and generating visualizations from various data sources.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry


@AgentRegistry.register
class DataAgent(BaseAgent):
    """Agent specialized in data analysis and visualization.
    
    The DataAgent processes structured data (CSV, Excel, JSON) to extract 
    meaningful insights, calculate statistics, and suggest or generate 
    visualizations that help users understand their data.
    
    Attributes:
        name: Agent identifier ("DataAgent").
        role: Description of the agent's purpose.
        system_prompt: Core instructions for rigorous data analysis.
        
    Example:
        >>> agent = DataAgent(llm_manager, db_session)
        >>> result = agent.execute({"data": my_spreadsheet_data, "task": "Find top 10 customers"})
        >>> print(result["output"]["insights"])
    """
    
    DEFAULT_ROLE = "Data analysis and insights"
    
    SYSTEM_PROMPT = """You are a data analyst expert. Your capabilities include:

1. **Data Analysis**: Analyze datasets and extract meaningful insights
2. **Statistics**: Calculate and interpret statistical measures
3. **Pattern Recognition**: Identify trends, patterns, and anomalies
4. **Reporting**: Create clear, actionable data reports

Always:
- Provide clear, non-technical explanations when appropriate
- Back up insights with specific numbers
- Highlight important findings
- Suggest actionable recommendations
- Acknowledge data limitations"""

    def __init__(
        self,
        llm_manager=None,
        db_session=None,
        tools: List[Any] = None
    ):
        super().__init__(
            name="DataAgent",
            role=self.DEFAULT_ROLE,
            system_prompt=self.SYSTEM_PROMPT,
            llm_manager=llm_manager,
            db_session=db_session,
            tools=tools or []
        )
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Performs data analysis or visualization based on provided datasets.
        
        Args:
            input_data: A dictionary containing:
                - task/prompt/original_prompt (str): Analysis objective.
                - data (list/dict, optional): The raw data to be analyzed.
                - file_id (int, optional): ID of a file containing the data.
                
        Returns:
            dict: Analysis results, insights, and visualization metadata.
        """
        self.start_execution()
        
        try:
            # Extract parameters
            task = (
                input_data.get("task") or 
                input_data.get("prompt") or 
                input_data.get("original_prompt", "")
            )
            data = input_data.get("data")
            file_id = input_data.get("file_id")
            
            # If file_id is provided, resolve it
            if file_id and not data:
                file_result = self._read_file_content(file_id)
                if file_result.get("success"):
                    data = file_result.get("data") or file_result.get("content")
                    self.log_action("file_loaded", {"file_id": file_id})
                else:
                    self.log_action("file_load_error", {"file_id": file_id, "error": file_result.get("error")})
            
            if not task:
                return self.format_output(None, status="error", error="No analysis task provided")
            
            self.log_action("analyzing_data", {"task": task[:100]})
            
            # If we have actual data, analyze it
            if data:
                result = self._analyze_dataset(data, task)
            else:
                # Generate sample analysis or answer data-related questions
                result = self._answer_data_question(task)
            
            self.end_execution()
            return self.format_output(result)
            
        except Exception as e:
            self.log_action("data_error", {"error": str(e)})
            self.end_execution()
            return self.format_output(None, status="error", error=str(e))
    
    def _analyze_dataset(
        self, 
        data: Any, 
        question: str = None
    ) -> Dict[str, Any]:
        """
        Analyze a dataset.
        """
        # Use data analysis tool if available
        tool = self._tool_map.get("data_analysis")
        
        if tool:
            # Get full summary
            analysis = tool.execute(action="summary", data=data)
            
            if analysis.get("success"):
                stats = analysis.get("data", {})
                
                # Use LLM to generate insights narrative
                insights_prompt = f"""Based on this data analysis:

Dataset Shape: {stats.get('overview', {}).get('shape', {})}
Statistics: {json.dumps(stats.get('overview', {}).get('statistics', {}), indent=2)[:500]}
Correlations: {json.dumps(stats.get('correlations', {}).get('strong_correlations', []), indent=2)[:300]}

{f"User question: {question}" if question else ""}

Provide:
1. Key insights (3-5 bullet points)
2. Notable patterns or trends
3. Recommendations based on the data"""

                narrative = self.generate_response(insights_prompt, use_cache=False)
                
                return {
                    "summary": stats.get("overview", {}),
                    "correlations": stats.get("correlations", {}),
                    "insights": narrative,
                    "recommendations": self._extract_recommendations(narrative)
                }
        
        # Fallback: use LLM to describe what analysis would look like
        return self._describe_analysis_approach(question or "Analyze the data")
    
    def _answer_data_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a data-related question without actual data.
        """
        prompt = f"""You are a data analyst. The user is asking about data analysis:

Question: {question}

If this is a general data question, provide helpful information.
If they want to analyze specific data, explain what data they should provide and what analysis you can do.

Be helpful and educational."""

        response = self.generate_response(prompt, use_cache=False)
        
        return {
            "answer": response,
            "note": "No data provided. For actual analysis, please provide a dataset.",
            "supported_formats": ["CSV", "JSON", "Dictionary/Object"]
        }
    
    def _describe_analysis_approach(self, task: str) -> Dict[str, Any]:
        """
        Describe how we would analyze data for a given task.
        """
        prompt = f"""Describe how you would analyze data for this task:

Task: {task}

Include:
1. What data would be needed
2. What analysis methods to use
3. What insights to look for
4. What visualizations would help"""

        response = self.generate_response(prompt, use_cache=False)
        
        return {
            "approach": response,
            "data_requirements": self._extract_data_requirements(response)
        }
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """
        Extract recommendations from text.
        """
        recommendations = []
        
        if not text:
            return recommendations
        
        # Look for recommendation patterns
        import re
        patterns = [
            r'recommend[s]?[:\s]+(.+?)(?:\.|$)',
            r'should[:\s]+(.+?)(?:\.|$)',
            r'suggest[s]?[:\s]+(.+?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            recommendations.extend([m.strip() for m in matches if len(m) > 10])
        
        return recommendations[:5]
    
    def _extract_data_requirements(self, text: str) -> List[str]:
        """
        Extract data requirements from text.
        """
        requirements = []
        
        keywords = ["need", "require", "should have", "must include", "data about"]
        
        for line in text.split('\n'):
            if any(kw in line.lower() for kw in keywords):
                requirements.append(line.strip())
        
        return requirements[:5]
