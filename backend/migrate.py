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

import time

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def run_migrations():
    print("🚀 Starting database migrations script...", flush=True)
    
    # Create all tables with retry logic
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🔍 Creating tables (attempt {attempt}/{MAX_RETRIES})...", flush=True)
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created successfully.", flush=True)
            break
        except Exception as e:
            print(f"❌ Table creation failed: {e}", flush=True)
            if attempt < MAX_RETRIES:
                print(f"⏳ Retrying in {RETRY_DELAY} seconds...", flush=True)
                time.sleep(RETRY_DELAY)
            else:
                print("❌ All retry attempts failed. Exiting.", flush=True)
                sys.exit(1)
        
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
