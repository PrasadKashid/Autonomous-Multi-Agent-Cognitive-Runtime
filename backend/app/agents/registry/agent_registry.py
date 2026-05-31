from app.agents.implementation.pm_agent import PMAgent
from app.agents.implementation.architect_agent import ArchitectureAgent
from app.orchestration.event_bus.bus import event_bus
from app.orchestration.event_bus.event_types import (
    TASK_CREATED,
    TASK_ASSIGNED,
    TASK_COMPLETED,
)
from app.orchestration.workflows.workflow_handlers import task_completed_handler

pm_agent = PMAgent()
architecture_agent = ArchitectureAgent()

event_bus.subscribe(TASK_CREATED, pm_agent.handle_event)
event_bus.subscribe(TASK_ASSIGNED, architecture_agent.handle_event)

event_bus.subscribe(TASK_COMPLETED, task_completed_handler)
