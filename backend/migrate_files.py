"""
Nexus AI - Database Migration
Simple script to create new tables defined in models
"""

import sys
import os

# Add the current directory to path so we can import models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
import models  # This triggers model registration in Base.metadata

def migrate():
    print("🚀 Starting database migration for Phase 7...")
    try:
        # This will create all tables that don't exist yet
        Base.metadata.create_all(bind=engine)
        print("✅ Migration successful! Tables created.")
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    migrate()
