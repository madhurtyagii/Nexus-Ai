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
    print("🚀 Starting database migrations script...", flush=True)
    
    # Create all tables
    try:
        print("🔍 Creating tables...", flush=True)
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully.", flush=True)
    except Exception as e:
        print(f"❌ Table creation failed: {e}", flush=True)
        # Don't exit, might be existing tables
        
    # Seed templates
    try:
        print("🌱 Seeding workflow templates...", flush=True)
        seed_templates()
        print("✅ Templates seeded successfully.", flush=True)
    except Exception as e:
        print(f"❌ Template seeding failed: {e}", flush=True)

    # Seed agents
    try:
        print("🤖 Seeding default agents...", flush=True)
        seed_agents()
        print("✅ Agents seeded successfully.", flush=True)
    except Exception as e:
        print(f"❌ Agent seeding failed: {e}", flush=True)

    print("✨ Migration process complete.", flush=True)


if __name__ == "__main__":
    run_migrations()
