"""
Celeryワーカーの設定。
"""

from celery import Celery
import os

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "report_worker",
    broker=redis_url,
    backend=redis_url,
    include=["app.celery_worker.tasks", "app.api.tasks"],
)

celery_app.conf.update(
    result_expires=3600,  # 結果は1時間後に期限切れになります
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

if __name__ == "__main__":
    celery_app.start()
