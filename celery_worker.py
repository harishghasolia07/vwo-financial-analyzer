import os
from celery import Celery
from database import SessionLocal, AnalysisResult
from runner import run_crew
from datetime import datetime

# Initialize Celery
# If you run locally and don't have redis, you can use SQLite for broker as well (though Redis is standard)
# We fall back to standard redis://localhost:6379/0 and it requires a running Redis server
REDIS_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "financial_analyzer_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Optional configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(name="process_financial_document")
def process_financial_document_task(analysis_id: str, file_path: str, query: str):
    db = SessionLocal()
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    if not analysis:
        db.close()
        return "Analysis ID not found"

    try:
        # Run the crew pipeline
        result = run_crew(query=query, file_path=file_path)
        
        # Update DB on success
        analysis.status = "completed"
        analysis.result = str(result)
        analysis.completed_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        # Update DB on failure
        analysis.status = "failed"
        analysis.error_message = str(e)
        analysis.completed_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()
        
        # Clean up the physical file
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

    return f"Processed {analysis_id}"
