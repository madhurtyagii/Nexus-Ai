"""
Nexus AI - Architect Tool
Builds project scaffolding from AI designs.
"""

from typing import Dict, Any
from tools.base_tool import BaseTool, ToolRegistry
from orchestrator.architect import architect_service

@ToolRegistry.register
class ArchitectTool(BaseTool):
    """
    Tool for building complex project scaffolding (folders and files) in the Nexus sandbox.
    """
    
    def __init__(self):
        super().__init__(
            name="Architect",
            description=(
                "Builds recursive project scaffolding (folders and files) in the Nexus sandbox. "
                "Use this to turn a project plan into physical files and directories."
            ),
            parameters={
                "project_name": "Unique name for the project (required)",
                "structure": (
                    "Dictionary defining the blueprint. "
                    "Example: {'folders': ['src', 'tests'], 'files': {'README.md': '# Project Title'}} (required)"
                )
            }
        )

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the architect engine to build a project.
        
        Args:
            project_name (str): The name of the project.
            structure (dict): The folder/file definition.
            
        Returns:
            dict: Standard success/data/error object.
        """
        try:
            self.validate_parameters(**kwargs)
            
            project_name = kwargs.get("project_name")
            structure = kwargs.get("structure")
            
            if not isinstance(structure, dict):
                return {"success": False, "error": "Structure must be a dictionary definition."}
            
            result = architect_service.build_project(project_name, structure)
            
            if result.get("status") == "success":
                return {
                    "success": True,
                    "data": result,
                    "message": (
                        f"Successfully architected '{project_name}'. "
                        f"Created {result['folders_created']} folders and {result['files_created']} files."
                    )
                }
            else:
                return {
                    "success": False, 
                    "error": result.get("error", "Unknown scaffolding error occurred.")
                }
                
        except Exception as e:
            return {"success": False, "error": f"ArchitectTool Exception: {str(e)}"}
