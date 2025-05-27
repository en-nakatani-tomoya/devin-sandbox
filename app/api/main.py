"""
FastAPIアプリケーションのメインモジュール。
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.api.tasks import process_report_task

app = FastAPI(
    title="レポートAPI", description="調査レポート処理のためのAPI"
)


class ReportRequest(BaseModel):
    """レポートエンドポイントのリクエストモデル。"""

    query: str

    class Config:
        schema_extra = {
            "example": {
                "query": "気候変動がホッキョクグマに与える影響を調査する"
            }
        }


class ReportResponse(BaseModel):
    """レポートエンドポイントのレスポンスモデル。"""

    task_id: str
    message: str


class ReportResult(BaseModel):
    """完了したレポートの結果モデル。"""

    task_id: str
    result: str
    status: str


@app.post("/report", response_model=ReportResponse)
async def create_report(
    request: ReportRequest, background_tasks: BackgroundTasks
):
    """
    提供されたクエリに基づいて新しい調査レポートを作成します。
    レポートはバックグラウンドで処理されます。
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="クエリを空にすることはできません")

    task_id = process_report_task.delay(request.query)

    return ReportResponse(
        task_id=str(task_id),
        message="レポートリクエストが正常に送信されました。タスクIDでステータスを確認してください。",
    )


@app.get("/report/{task_id}", response_model=ReportResult)
async def get_report(task_id: str):
    """
    以前に送信されたレポートタスクの結果を取得します。
    """
    from app.celery_worker.worker import celery_app

    task = celery_app.AsyncResult(task_id)

    if task.state == "PENDING":
        return ReportResult(
            task_id=task_id,
            result="タスクはまだ処理中です",
            status="pending",
        )
    elif task.state == "FAILURE":
        return ReportResult(
            task_id=task_id,
            result=str(task.info),
            status="failed",
        )
    else:
        result = task.result
        if (
            isinstance(result, list)
            and len(result) > 0
            and isinstance(result[0], list)
            and len(result[0]) > 0
        ):
            inner_task_id = result[0][0]
            inner_task = celery_app.AsyncResult(inner_task_id)
            if inner_task.state == "SUCCESS":
                return ReportResult(
                    task_id=task_id,
                    result=str(inner_task.result),
                    status="completed",
                )

        return ReportResult(
            task_id=task_id,
            result=str(result),
            status="completed",
        )


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント。"""
    return {"status": "ok"}
