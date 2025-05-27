"""
Task definitions for the API.
This module defines the interface to Celery tasks.
"""
from app.celery_worker.worker import celery_app


def process_report_task(query: str):
    """
    Submit a task to process a report query.
    
    Args:
        query: The investigation query string
        
    Returns:
        The task object
    """
    return celery_app.send_task('app.celery_worker.tasks.process_report', args=[query])
