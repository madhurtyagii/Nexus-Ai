"""
Nexus AI - File Processor Tool
Tool for reading and analyzing various file formats
"""

import os
import json
import pandas as pd
from typing import Dict, Any, Optional, List
from abc import ABC

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

from tools.base_tool import BaseTool

class FileProcessorTool(BaseTool):
    """
    Tool for processing uploaded files (CSV, PDF, Excel, JSON, Text).
    Used by agents to access user-provided data.
    """
    
    def __init__(self):
        super().__init__(
            name="FileProcessor",
            description="Process and read contents of various file formats (CSV, PDF, Excel, JSON, Text)"
        )

    def execute(self, action: str, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Main entry point for tool execution.
        
        Actions:
            - read_csv: Read CSV file and return head/summary or full content
            - read_text: Read plain text file
            - read_pdf: Extract text from PDF
            - read_excel: Read Excel file
            - read_json: Parse JSON file
            - get_file_info: Get metadata about the file
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found at: {file_path}"}
            
        try:
            if action == "read_csv":
                return self.read_csv(file_path, **kwargs)
            elif action == "read_text":
                return self.read_text(file_path)
            elif action == "read_pdf":
                return self.read_pdf(file_path)
            elif action == "read_excel":
                return self.read_excel(file_path, **kwargs)
            elif action == "read_json":
                return self.read_json(file_path)
            elif action == "get_file_info":
                return self.get_file_info(file_path)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            return {"error": f"Error processing file: {str(e)}"}

    def read_csv(self, file_path: str, max_rows: int = 100, **kwargs) -> Dict[str, Any]:
        """Read CSV file using pandas."""
        df = pd.read_csv(file_path)
        
        return {
            "columns": list(df.columns),
            "row_count": len(df),
            "data": df.head(max_rows).to_dict(orient="records"),
            "summary": df.describe(include='all').to_dict() if len(df) > 0 else {}
        }

    def read_text(self, file_path: str) -> Dict[str, Any]:
        """Read text file."""
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        return {
            "content": content,
            "length": len(content)
        }

    def read_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF using PyPDF2."""
        if PyPDF2 is None:
            return {"error": "PyPDF2 library not installed"}
            
        text = ""
        page_count = 0
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            page_count = len(reader.pages)
            for page in reader.pages:
                text += page.extract_text() or ""
                
        return {
            "content": text,
            "page_count": page_count,
            "length": len(text)
        }

    def read_excel(self, file_path: str, sheet_name: Optional[str] = 0, **kwargs) -> Dict[str, Any]:
        """Read Excel file using pandas."""
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        return {
            "columns": list(df.columns),
            "row_count": len(df),
            "data": df.head(100).to_dict(orient="records")
        }

    def read_json(self, file_path: str) -> Dict[str, Any]:
        """Parse JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {"data": data}

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file metadata."""
        stats = os.stat(file_path)
        return {
            "filename": os.path.basename(file_path),
            "size_bytes": stats.st_size,
            "extension": os.path.splitext(file_path)[1].lower(),
            "last_modified": stats.st_mtime
        }
