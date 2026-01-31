"""
Nexus AI - Template Seeder
Populates the database with built-in workflow templates
"""

import sys
import os

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models.workflow_template import WorkflowTemplate
from templates.workflows import BUILT_IN_TEMPLATES

def seed_templates():
    print("🌱 Seeding workflow templates...")
    db = SessionLocal()
    
    try:
        count = 0
        for template_data in BUILT_IN_TEMPLATES:
            # Check if template already exists
            existing = db.query(WorkflowTemplate).filter(WorkflowTemplate.name == template_data["name"]).first()
            
            if existing:
                print(f"ℹ️ Template '{template_data['name']}' already exists. Updating...")
                existing.description = template_data["description"]
                existing.category = template_data["category"]
                existing.icon = template_data["icon"]
                existing.structure = template_data["structure"]
            else:
                template = WorkflowTemplate(
                    name=template_data["name"],
                    description=template_data["description"],
                    category=template_data["category"],
                    icon=template_data["icon"],
                    structure=template_data["structure"],
                    is_built_in=True
                )
                db.add(template)
                count += 1
                print(f"✅ Added template: {template_data['name']}")
        
        db.commit()
        print(f"✨ Seeding complete! {count} new templates added.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_templates()
