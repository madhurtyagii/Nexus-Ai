"""
Nexus AI - Run Worker Script
Standalone script to start a background worker
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from worker import run_worker

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 NEXUS AI BACKGROUND WORKER")
    print("=" * 50)
    print("Press Ctrl+C to stop the worker")
    print("-" * 50)
    
    run_worker()
