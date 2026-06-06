from app.agents.implementation.pm_agent import PMAgent
from app.agents.implementation.architect_agent import ArchitectureAgent
from app.agents.implementation.developer_agent import DeveloperAgent
from app.agents.implementation.qa_agent import QAAgent
from app.orchestration.event_bus.bus import event_bus
from app.orchestration.event_bus.event_types import *
from app.orchestration.workflows.workflow_handlers import task_completed_handler

from app.orchestration.workflows.task_failed_handler import task_failed_handler

pm_agent = PMAgent()
architecture_agent = ArchitectureAgent()
developer_agent = DeveloperAgent()
qa_agent = QAAgent()

event_bus.subscribe(TASK_CREATED, pm_agent.handle_event)
event_bus.subscribe(TASK_ASSIGNED, architecture_agent.handle_event)
event_bus.subscribe(TASK_ASSIGNED, developer_agent.handle_event)
event_bus.subscribe(TASK_ASSIGNED, qa_agent.handle_event)

event_bus.subscribe(TASK_COMPLETED, task_completed_handler)
event_bus.subscribe(TASK_FAILED, task_failed_handler)
