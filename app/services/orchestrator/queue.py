import threading
import logging
from app.database import SessionLocal
from app.services.orchestrator.runner import AnalysisOrchestrator

logger = logging.getLogger(__name__)


def enqueue_analysis_job(job_id: str):
    """
    Enqueues an analysis job for background execution.
    In threaded mode (hackathon / standalone), runs in a daemon thread.
    Can be replaced or routed to Celery with Redis for distributed deployments.
    """
    def _worker():
        db = SessionLocal()
        try:
            AnalysisOrchestrator.execute_analysis(db=db, job_id=job_id)
        except Exception as e:
            logger.error(f"Background analysis worker failed for job {job_id}: {str(e)}", exc_info=True)
        finally:
            db.close()

    thread = threading.Thread(target=_worker, daemon=True, name=f"analysis-worker-{job_id}")
    thread.start()
