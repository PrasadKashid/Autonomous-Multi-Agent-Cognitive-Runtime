from fastapi import FastAPI, APIRouter

from app.orchestration.event_bus.bus import event_bus
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import TASK_CREATED
import app.orchestration.event_bus.subscribers

import app.agents.registry.agent_bootstrap
from app.db.database import Base, engine
from app.orchestration.workflows.workflow_manager import workflow_manager

from app.api.routes.workflow_routes import router as workflow_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(workflow_router)
router = APIRouter()


@app.on_event("startup")
async def startup_event():

    workflow_manager.recover_workflows()
    workflows = workflow_manager.get_all_workflows()
    await workflow_manager.resume_recovered_workflows()


@app.get("/")
async def root():
    return {"message": "AI Autonomous Runtime Online"}
