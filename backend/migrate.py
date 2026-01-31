"""
Nexus AI - Database Migration Script
Ensures all database tables and built-in templates are initialized on startup.
"""

import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
from seed_templates import seed_templates
from seed_agents import seed_agents

def run_migrations():
    print("🚀 Starting database migrations...")
    
    # Create all tables
    try:
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully.")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        # Don't exit, might be existing tables
        
    # Seed templates
    try:
        print("Seeding workflow templates...")
        seed_templates()
        print("✅ Templates seeded successfully.")
    except Exception as e:
        print(f"❌ Template seeding failed: {e}")

    # Seed agents
    try:
        print("Seeding default agents...")
        seed_agents()
        print("✅ Agents seeded successfully.")
    except Exception as e:
        print(f"❌ Agent seeding failed: {e}")

    print("✨ Migration process complete.")

if __name__ == "__main__":
    run_migrations()
