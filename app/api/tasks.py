"""
APIのタスク定義。
このモジュールはCeleryタスクへのインターフェースを定義します。
"""

from app.celery_worker.worker import celery_app


@celery_app.task(name="app.api.tasks.process_report_task")
def process_report_task(query: str):
    """
    レポートクエリを処理するタスクを送信します。

    引数:
        query: 調査クエリ文字列

    戻り値:
        タスクオブジェクト
    """
    from app.celery_worker.tasks import process_report

    return process_report.delay(query)
