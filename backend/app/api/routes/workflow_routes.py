from fastapi import APIRouter

from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.bus import event_bus
from app.orchestration.event_bus.event_types import *

from app.api.schemas.workflow_schema import CreateWorkflowRequest
from app.db.repositories.workflow_repository import workflow_repository
from app.db.repositories.workflow_context_repository import workflow_context_repository
from app.db.repositories.task_repository import task_repository
from uuid import uuid4

# from app.

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.post("/")
async def create_workflow(request: CreateWorkflowRequest):
    correlation_id = str(uuid4())
    event = Event(
        event_type=TASK_CREATED,
        source_agent="API",
        correlation_id=correlation_id,
        payload={"task": request.task},
    )
    await event_bus.publish(event=event)

    return {"message": "Workflow Started", "task": request.task}


@router.get("/")
def get_all_worklflows():
    return workflow_repository.get_all()


@router.get("/{workflow_id}")
def get_workflow(workflow_id: str):
    workflow = workflow_repository.get(workflow_id=workflow_id)
    return workflow


@router.get("/{workflow_id}/tasks")
def get_task(workflow_id: str):
    return task_repository.get_by_workflow(workflow_id=workflow_id)


@router.get("/{workflow_id}/context")
def fet_context(workflow_id: str):
    return workflow_context_repository.get_workflow_context(workflow_id=workflow_id)
