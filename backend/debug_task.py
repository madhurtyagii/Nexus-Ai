from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import get_settings
import json

settings = get_settings()
engine = create_engine(settings.database_url)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Get most recent task
    result = session.execute(text("SELECT id, user_prompt, status, output FROM tasks ORDER BY created_at DESC LIMIT 1"))
    task = result.fetchone()
    
    if task:
        print(f"Task ID: {task[0]}")
        print(f"Prompt: {task[1][:50]}...")
        print(f"Status: {task[2]}")
        print(f"Output: {task[3][:200] if task[3] else 'NULL'}")
        
        # Check subtasks
        subtasks = session.execute(text(f"SELECT id, assigned_agent, status, output_data FROM subtasks WHERE task_id = {task[0]}")).fetchall()
        print(f"\nSubtasks ({len(subtasks)}):")
        for st in subtasks:
            print(f"- Agent: {st[1]}, Status: {st[2]}")
            if st[3]:
                print(f"  Output data keys: {list(st[3].keys()) if isinstance(st[3], dict) else type(st[3])}")
                if isinstance(st[3], dict) and 'output' in st[3]:
                    output = st[3]['output']
                    print(f"  Output type: {type(output)}")
                    if isinstance(output, dict):
                        print(f"  Output keys: {list(output.keys())}")
    else:
        print("No tasks found.")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
