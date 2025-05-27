"""
Celery tasks for processing reports.
"""

from app.celery_worker.worker import celery_app
from app.celery_worker.openai_mock import OpenAIMock
import time


@celery_app.task(name="app.celery_worker.tasks.process_report")
def process_report(query: str) -> str:
    """
    Process a report query using the OpenAI API (mock for now).

    Args:
        query: The investigation query string

    Returns:
        The investigation results as a string
    """
    time.sleep(2)

    openai_client = OpenAIMock()

    result = openai_client.generate_report(query)

    return result
