"""
FastAPI application main module.
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from app.api.tasks import process_report_task

app = FastAPI(
    title="Report API", description="API for processing investigation reports"
)


class ReportRequest(BaseModel):
    """Request model for the report endpoint."""

    query: str

    class Config:
        schema_extra = {
            "example": {
                "query": "Investigate the impact of climate change on polar bears"
            }
        }


class ReportResponse(BaseModel):
    """Response model for the report endpoint."""

    task_id: str
    message: str


class ReportResult(BaseModel):
    """Result model for completed reports."""

    task_id: str
    result: str
    status: str


@app.post("/report", response_model=ReportResponse)
async def create_report(
    request: ReportRequest, background_tasks: BackgroundTasks
):
    """
    Create a new investigation report based on the provided query.
    The report will be processed in the background.
    """
    if not request.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    task_id = process_report_task.delay(request.query)

    return ReportResponse(
        task_id=str(task_id),
        message="Report request submitted successfully. Check status with the task ID.",
    )


@app.get("/report/{task_id}", response_model=ReportResult)
async def get_report(task_id: str):
    """
    Get the result of a previously submitted report task.
    """
    from app.celery_worker.worker import celery_app

    task = celery_app.AsyncResult(task_id)

    if task.state == "PENDING":
        return ReportResult(
            task_id=task_id,
            result="Task is still processing",
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
    """Health check endpoint."""
    return {"status": "ok"}
