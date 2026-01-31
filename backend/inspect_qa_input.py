from database import SessionLocal
from models.task import Subtask
import json

db = SessionLocal()
try:
    subtask = db.query(Subtask).filter(Subtask.assigned_agent == 'QAAgent').order_by(Subtask.id.desc()).first()
    if subtask:
        print(f"Subtask ID: {subtask.id}")
        if subtask.input_data:
            print("Input Keys:", list(subtask.input_data.keys()))
            if 'content' in subtask.input_data:
                content = subtask.input_data['content']
                print(f"Content Length: {len(content) if content else 0}")
                print(f"Content Preview: {content[:100] if content else 'Empty'}")
            else:
                print("CRITICAL: 'content' key matches MISSING")
        else:
            print("CRITICAL: input_data is NONE")
    else:
        print("No QAAgent subtasks found")
finally:
    db.close()
