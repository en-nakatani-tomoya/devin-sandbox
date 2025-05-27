"""
Task definitions for the API.
This module defines the interface to Celery tasks.
"""
from app.celery_worker.worker import celery_app


@celery_app.task(name='app.api.tasks.process_report_task')
def process_report_task(query: str):
    """
    Submit a task to process a report query.
    
    Args:
        query: The investigation query string
        
    Returns:
        The task object
    """
    from app.celery_worker.tasks import process_report
    return process_report.delay(query)
