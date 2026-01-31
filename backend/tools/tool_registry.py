"""
Nexus AI - Tool Registry
Singleton registry for managing all tools
"""

from typing import Dict, List, Any, Optional

from tools.base_tool import BaseTool


class ToolRegistry:
    """
    Singleton registry for tools.
    
    Maintains a mapping of tool names to tool instances.
    """
    
    _instance = None
    _tools: Dict[str, BaseTool] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_default_tools()
            ToolRegistry._initialized = True
    
    def _initialize_default_tools(self):
        """Initialize default tools."""
        from tools.web_search import WebSearchTool
        from tools.web_scraper import WebScraperTool
        from tools.code_executor import CodeExecutorTool
        from tools.data_analysis import DataAnalysisTool
        from tools.file_processor import FileProcessorTool
        
        # Register default tools
        self.register_tool(WebSearchTool())
        self.register_tool(WebScraperTool())
        self.register_tool(CodeExecutorTool())
        self.register_tool(DataAnalysisTool())
        self.register_tool(FileProcessorTool())
    
    def register_tool(self, tool: BaseTool):
        """
        Register a tool instance.
        
        Args:
            tool: Tool instance to register
        """
        if not hasattr(tool, 'name') or not hasattr(tool, 'execute'):
            raise ValueError("Tool must have 'name' and 'execute' attributes")
        
        ToolRegistry._tools[tool.name] = tool
        print(f"✅ Registered tool: {tool.name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool instance or None
        """
        return ToolRegistry._tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all registered tools.
        
        Returns:
            List of tool info dictionaries
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in ToolRegistry._tools.values()
        ]
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool is registered."""
        return tool_name in ToolRegistry._tools
    
    @classmethod
    def clear(cls):
        """Clear all registered tools (for testing)."""
        cls._tools = {}
        cls._initialized = False


# Global registry instance
tool_registry = ToolRegistry()
