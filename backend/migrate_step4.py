"""
Manual migration script to add Step 4 columns to projects table.
Run this script to update the database schema.
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Migrating database...")
        
        # Add is_archived
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN is_archived INTEGER DEFAULT 0"))
            print("Added is_archived column")
        except Exception as e:
            print(f"Column is_archived might already exist: {e}")
            
        # Add is_pinned
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN is_pinned INTEGER DEFAULT 0"))
            print("Added is_pinned column")
        except Exception as e:
            print(f"Column is_pinned might already exist: {e}")
            
        # Add tags
        try:
            conn.execute(text("ALTER TABLE projects ADD COLUMN tags JSONB DEFAULT '[]'::jsonb"))
            print("Added tags column")
        except Exception as e:
            print(f"Column tags might already exist: {e}")
            
        conn.commit()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
