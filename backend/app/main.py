from fastapi import FastAPI, APIRouter

from app.orchestration.event_bus.bus import event_bus
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import TASK_CREATED
import app.orchestration.event_bus.subscribers

import app.agents.registry.agent_bootstrap
from app.db.database import Base, engine
from app.orchestration.workflows.workflow_manager import workflow_manager

Base.metadata.create_all(bind=engine)

app = FastAPI()
router = APIRouter()


@app.on_event("startup")
async def startup_event():
    # workflow = workflow_manager.create_workflow(
    #     workflow_name="Test Workflow", correlation_id="123"
    # )
    event = Event(
        event_type=TASK_CREATED,
        source_agent="SYSTEM",
        correlation_id="workflow_001",
        payload={"task": "Build Authentication module"},
    )

    await event_bus.publish(event)


@app.get("/")
async def root():
    return {"message": "AI Autonomous Runtime Online"}


@router.post("/workflow/start")
async def start_workflow():
    pass
