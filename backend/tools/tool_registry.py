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
    _lazy_tools: Dict[str, str] = {
        "web_search": "tools.web_search.WebSearchTool",
        "web_scraper": "tools.web_scraper.WebScraperTool",
        "code_executor": "tools.code_executor.CodeExecutorTool",
        "data_analysis": "tools.data_analysis.DataAnalysisTool",
        "FileProcessor": "tools.file_processor.FileProcessorTool",
        "project_planner": "tools.project_planner.ProjectPlannerTool",
        "task_scheduler": "tools.task_scheduler.task_scheduler.TaskSchedulerTool",
        "validation": "tools.validation_tools.ValidationTool",
        "quality_checker": "tools.quality_checker.QualityCheckerTool",
    }
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialized = True # Mark as initialized to skip old eager init
        return cls._instance
    
    def __init__(self):
        # Empty init, we use lazy loading now
        pass
    
    def register_tool(self, tool: BaseTool):
        """
        Register a tool instance (eager).
        """
        if not hasattr(tool, 'name') or not hasattr(tool, 'execute'):
            raise ValueError("Tool must have 'name' and 'execute' attributes")
        
        ToolRegistry._tools[tool.name] = tool
        # Remove from lazy if it's already registered
        if tool.name in ToolRegistry._lazy_tools:
            del ToolRegistry._lazy_tools[tool.name]
        print(f"✅ Registered tool: {tool.name}")
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name, loading it lazily if necessary.
        """
        if tool_name in ToolRegistry._tools:
            return ToolRegistry._tools[tool_name]
            
        if tool_name in ToolRegistry._lazy_tools:
            module_path = ToolRegistry._lazy_tools[tool_name]
            try:
                import importlib
                module_name, class_name = module_path.rsplit(".", 1)
                print(f"🚚 Lazy loading tool: {tool_name} from {module_name}")
                module = importlib.import_module(module_name)
                tool_class = getattr(module, class_name)
                tool_instance = tool_class()
                
                ToolRegistry._tools[tool_name] = tool_instance
                del ToolRegistry._lazy_tools[tool_name]
                return tool_instance
            except Exception as e:
                print(f"❌ Failed to lazy load tool {tool_name}: {e}")
                return None
                
        return None
    
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
