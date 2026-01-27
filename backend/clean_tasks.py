from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Fail stuck tasks
    session.execute(text("UPDATE tasks SET status = 'failed' WHERE status = 'in_progress'"))
    session.execute(text("UPDATE subtasks SET status = 'failed', error_message = 'Worker execution failed: Redis unavailable' WHERE status = 'in_progress' OR status = 'queued'"))
    session.commit()
    print("Stuck tasks marked as failed.")
except Exception as e:
    print(f"Error: {e}")
finally:
    session.close()
