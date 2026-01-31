from database import SessionLocal
from models.task import Subtask, TaskStatus
import datetime

db = SessionLocal()
try:
    # Get last 3 subtasks
    subtasks = db.query(Subtask).order_by(Subtask.id.desc()).limit(3).all()
    
    if subtasks:
        for subtask in subtasks:
            print(f"\n{'='*40}")
            print(f"ID: {subtask.id} | Status: {subtask.status} | Agent: {subtask.assigned_agent}")
            print(f"Error Field: {subtask.error_message}")
            print(f"Input Data keys: {list(subtask.input_data.keys()) if subtask.input_data else 'None'}")
            if subtask.input_data:
                print(f"Input Data: {subtask.input_data}")
            if subtask.output_data:
                print(f"Output Data: {subtask.output_data}")
    else:
        print("No subtasks found.")
        print("No failed subtasks found.")
finally:
    db.close()
