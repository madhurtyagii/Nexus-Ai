"""
Nexus AI - Phase 6 Projects Migration
Add new columns to projects table for workflow management
"""

import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), "nexus.db")


def migrate():
    """Add Phase 6 columns to projects table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # First, check if projects table exists - if not, create it via SQLAlchemy
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects'")
    if not cursor.fetchone():
        print("Projects table doesn't exist. Creating tables via SQLAlchemy...")
        # Import and create all tables
        import sys
        sys.path.insert(0, os.path.dirname(__file__))
        from database import Base, engine
        from models.project import Project
        from models.task import Task
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully")
        # Close and reconnect after creating tables
        conn.close()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
    
    # New columns to add (only for existing tables that may not have these)
    new_columns = [
        ("status", "VARCHAR(50) DEFAULT 'planning'"),
        ("project_plan", "JSON"),
        ("workflow", "JSON"),
        ("created_by_agent", "VARCHAR(100) DEFAULT 'ManagerAgent'"),
        ("total_tasks", "INTEGER DEFAULT 0"),
        ("completed_tasks", "INTEGER DEFAULT 0"),
        ("total_phases", "INTEGER DEFAULT 0"),
        ("current_phase", "INTEGER DEFAULT 0"),
        ("estimated_minutes", "INTEGER"),
        ("actual_minutes", "INTEGER"),
        ("risk_level", "VARCHAR(20)"),
        ("complexity_score", "REAL"),
        ("started_at", "DATETIME"),
        ("completed_at", "DATETIME"),
        ("output", "TEXT"),
        ("summary", "TEXT"),
    ]
    
    # Add columns for tasks table
    task_columns = [
        ("project_phase", "INTEGER"),
        ("task_sequence", "INTEGER"),
    ]
    
    print("Migrating projects table for Phase 6...")
    
    for column_name, column_type in new_columns:
        try:
            cursor.execute(f"ALTER TABLE projects ADD COLUMN {column_name} {column_type}")
            print(f"  ✓ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"  - Column {column_name} already exists")
            else:
                print(f"  ✗ Error adding {column_name}: {e}")
    
    print("\nMigrating tasks table for Phase 6...")
    
    for column_name, column_type in task_columns:
        try:
            cursor.execute(f"ALTER TABLE tasks ADD COLUMN {column_name} {column_type}")
            print(f"  ✓ Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print(f"  - Column {column_name} already exists")
            else:
                print(f"  ✗ Error adding {column_name}: {e}")
    
    # Create index on projects status
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)")
        print("\n  ✓ Created index: idx_projects_status")
    except Exception as e:
        print(f"\n  - Index creation: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Phase 6 migration complete!")


if __name__ == "__main__":
    migrate()
