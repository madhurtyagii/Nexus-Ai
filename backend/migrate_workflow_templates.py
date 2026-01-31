"""
Nexus AI - Migration Script for Workflow Templates
Creates the workflow_templates table
"""

import sys
import os

# Add the current directory to sys.path to import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
from models.workflow_template import WorkflowTemplate

def migrate():
    print("🚀 Starting migration for workflow_templates table...")
    try:
        # This will create the table if it doesn't exist
        WorkflowTemplate.__table__.create(engine)
        print("✅ workflow_templates table created successfully!")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("ℹ️ workflow_templates table already exists.")
        else:
            print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    migrate()
