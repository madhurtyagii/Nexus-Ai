"""
Nexus AI - Code Executor Tool
Safely execute Python code in a sandboxed environment
"""

import sys
import io
import ast
import time
import traceback
from typing import Dict, Any, List
from contextlib import redirect_stdout, redirect_stderr
import threading

from tools.base_tool import BaseTool


class CodeExecutorTool(BaseTool):
    """
    Execute Python code safely in a restricted environment.
    
    Security measures:
    - Blacklisted dangerous imports (os, sys, subprocess, etc.)
    - Execution timeout
    - Captured stdout/stderr
    """
    
    # Dangerous modules and functions
    BLACKLISTED_IMPORTS = {
        'os', 'sys', 'subprocess', 'socket', 'shutil', 
        'pickle', 'shelve', 'marshal', 'builtins', '__builtins__',
        'importlib', 'ctypes', 'multiprocessing', 'threading',
        'asyncio', 'signal', 'resource', 'pty', 'fcntl',
    }
    
    BLACKLISTED_BUILTINS = {
        'eval', 'exec', 'compile', '__import__', 'open',
        'input', 'breakpoint', 'memoryview', 'globals', 'locals',
    }
    
    # Safe modules allowed
    ALLOWED_IMPORTS = {
        'math', 'random', 'datetime', 'json', 're', 'string',
        'collections', 'itertools', 'functools', 'operator',
        'decimal', 'fractions', 'statistics', 'copy',
    }
    
    def __init__(self, max_execution_time: int = 5):
        super().__init__(
            name="code_executor",
            description="Execute Python code safely in a sandboxed environment",
            parameters={
                "code": "Python code to execute (required)",
                "timeout": "Execution timeout in seconds (optional, default 5)"
            }
        )
        self.max_execution_time = max_execution_time
    
    def execute(
        self, 
        code: str, 
        timeout: int = None
    ) -> Dict[str, Any]:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result dictionary
        """
        if not code or not code.strip():
            return {
                "success": False,
                "error": "Code cannot be empty",
                "output": "",
                "stdout": "",
                "stderr": ""
            }
        
        timeout = timeout or self.max_execution_time
        
        # Step 1: Validate code safety
        safety_check = self._validate_code_safety(code)
        if not safety_check["safe"]:
            return {
                "success": False,
                "error": f"Security violation: {safety_check['reason']}",
                "output": "",
                "stdout": "",
                "stderr": ""
            }
        
        # Step 2: Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            return {
                "success": False,
                "error": f"Syntax error: {e.msg} (line {e.lineno})",
                "output": "",
                "stdout": "",
                "stderr": str(e)
            }
        
        # Step 3: Execute in sandbox
        start_time = time.time()
        result = self._execute_in_sandbox(code, timeout)
        execution_time = round(time.time() - start_time, 3)
        
        result["execution_time"] = execution_time
        return result
    
    def _validate_code_safety(self, code: str) -> Dict[str, Any]:
        """
        Check if code is safe to execute.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {"safe": True, "reason": None}  # Syntax errors caught later
        
        for node in ast.walk(tree):
            # Check for imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in self.BLACKLISTED_IMPORTS:
                        return {"safe": False, "reason": f"Import of '{module}' is not allowed"}
            
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module in self.BLACKLISTED_IMPORTS:
                        return {"safe": False, "reason": f"Import from '{module}' is not allowed"}
            
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.BLACKLISTED_BUILTINS:
                        return {"safe": False, "reason": f"Function '{node.func.id}' is not allowed"}
                
                # Check for __import__
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.BLACKLISTED_BUILTINS:
                        return {"safe": False, "reason": f"Function '{node.func.attr}' is not allowed"}
            
            # Check for attribute access to dangerous modules
            if isinstance(node, ast.Attribute):
                if node.attr in ['system', 'popen', 'spawn', 'fork', 'exec']:
                    return {"safe": False, "reason": f"Attribute '{node.attr}' access is not allowed"}
        
        return {"safe": True, "reason": None}
    
    def _execute_in_sandbox(
        self, 
        code: str, 
        timeout: int
    ) -> Dict[str, Any]:
        """
        Execute code in a sandboxed environment.
        """
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Create safe globals
        safe_globals = {
            '__builtins__': {
                # Safe builtins
                'print': print,
                'len': len,
                'range': range,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'abs': abs,
                'all': all,
                'any': any,
                'bin': bin,
                'chr': chr,
                'divmod': divmod,
                'enumerate': enumerate,
                'filter': filter,
                'format': format,
                'frozenset': frozenset,
                'getattr': getattr,
                'hasattr': hasattr,
                'hash': hash,
                'hex': hex,
                'id': id,
                'isinstance': isinstance,
                'issubclass': issubclass,
                'iter': iter,
                'map': map,
                'max': max,
                'min': min,
                'next': next,
                'oct': oct,
                'ord': ord,
                'pow': pow,
                'repr': repr,
                'reversed': reversed,
                'round': round,
                'slice': slice,
                'sorted': sorted,
                'sum': sum,
                'type': type,
                'zip': zip,
                'Exception': Exception,
                'ValueError': ValueError,
                'TypeError': TypeError,
                'KeyError': KeyError,
                'IndexError': IndexError,
                'True': True,
                'False': False,
                'None': None,
            }
        }
        
        # Add allowed imports
        for module_name in self.ALLOWED_IMPORTS:
            try:
                safe_globals[module_name] = __import__(module_name)
            except ImportError:
                pass
        
        result = {
            "success": False,
            "output": None,
            "stdout": "",
            "stderr": "",
            "error": None
        }
        
        def run_code():
            nonlocal result
            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # Execute and capture last expression result
                    exec_result = exec(code, safe_globals, safe_globals)
                    
                    # Try to get a return value
                    if '_result' in safe_globals:
                        result["output"] = safe_globals['_result']
                    else:
                        result["output"] = exec_result
                    
                    result["success"] = True
                    
            except Exception as e:
                result["success"] = False
                result["error"] = f"{type(e).__name__}: {str(e)}"
                result["stderr"] = traceback.format_exc()
        
        # Run with timeout
        thread = threading.Thread(target=run_code)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            result["success"] = False
            result["error"] = f"Execution timed out after {timeout} seconds"
        
        result["stdout"] = stdout_capture.getvalue()
        if not result["stderr"]:
            result["stderr"] = stderr_capture.getvalue()
        
        return result
