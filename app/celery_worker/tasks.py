"""
レポート処理のためのCeleryタスク。
"""

from app.celery_worker.worker import celery_app
from app.celery_worker.openai_mock import OpenAIMock
import time


@celery_app.task(name="app.celery_worker.tasks.process_report")
def process_report(query: str) -> str:
    """
    OpenAI API（現在はモック）を使用してレポートクエリを処理します。

    引数:
        query: 調査クエリ文字列

    戻り値:
        文字列としての調査結果
    """
    time.sleep(2)

    openai_client = OpenAIMock()

    result = openai_client.generate_report(query)

    return result
