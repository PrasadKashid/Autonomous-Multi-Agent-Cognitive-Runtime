from fastapi import FastAPI

from app.orchestration.event_bus.bus import event_bus
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import TASK_CREATED
import app.orchestration.event_bus.subscribers

import app.agents.registry.agent_registry

app = FastAPI()


@app.on_event("startup")
async def startup_event():

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
