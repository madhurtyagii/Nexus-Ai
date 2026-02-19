"""Nexus AI - Autonomous Project Architect Engine.

This module provides the logic for recursively generating complex project
structures (folders and files) from AI-generated architecture designs.
"""

import os
import json
from typing import Dict, Any, List, Optional
from logging_config import get_logger

logger = get_logger("orchestrator.architect")


class ArchitectService:
    """Engine for building project scaffolding from structural definitions."""
    
    def __init__(self, base_storage_path: str = None):
        """
        Initialize the architect service.
        
        Args:
            base_storage_path: Shared directory for all architected projects.
        """
        if base_storage_path:
            self.base_path = base_storage_path
        else:
            # Default to backend/storage/projects
            self.base_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "storage", "projects"
            )
        
        # Ensure the project sandbox exists
        try:
            os.makedirs(self.base_path, exist_ok=True)
            logger.info(f"🏗️ Architect Sandbox initialized at: {self.base_path}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Architect Sandbox: {e}")

    def build_project(self, project_name: str, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Constructs a project directory tree from a JSON structure definition.
        
        Structure Format:
        {
            "folders": ["src/components", "api/routes", "tests"],
            "files": {
                "README.md": "# Project Title\n...",
                "src/index.js": "console.log('init');",
                "api/main.py": "from fastapi import FastAPI..."
            }
        }
        
        Args:
            project_name: Name of the project (becomes the root folder name).
            structure: Dictionary defining folders and files.
            
        Returns:
            dict: Summary of created items and final absolute path.
        """
        safe_name = "".join([c if c.isalnum() else "_" for c in project_name]).lower()
        project_root = os.path.join(self.base_path, safe_name)
        
        results = {
            "project_name": project_name,
            "root_path": project_root,
            "folders_created": 0,
            "files_created": 0,
            "status": "success"
        }
        
        try:
            # 1. Create root
            os.makedirs(project_root, exist_ok=True)
            
            # 2. Create sub-folders
            for folder in structure.get("folders", []):
                folder_path = os.path.join(project_root, folder)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path, exist_ok=True)
                    results["folders_created"] += 1
            
            # 3. Create files with content
            for rel_path, content in structure.get("files", {}).items():
                full_path = os.path.join(project_root, rel_path)
                
                # Ensure the parent directory of the file exists (even if not in 'folders' list)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, "w", encoding="utf-8") as f:
                    # If content is a dict/list, save as JSON, otherwise string
                    if isinstance(content, (dict, list)):
                        json.dump(content, f, indent=4)
                    else:
                        f.write(str(content))
                
                results["files_created"] += 1
                
            logger.info(f"✨ Project '{project_name}' built successfully: {results['folders_created']} folders, {results['files_created']} files.")
            
        except Exception as e:
            logger.error(f"❌ Architect build failed for '{project_name}': {e}")
            results["status"] = "error"
            results["error"] = str(e)
            
        return results

# Singleton instance for global use
architect_service = ArchitectService()
