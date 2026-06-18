from app.agents.base.base_agent import BaseAgent
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import TASK_ASSIGNED, TASK_COMPLETED

from app.memory.memory_manager import memory_manager
from app.capabilities.testing import TestingCapability


class QAAgent(BaseAgent):
    def __init__(self):
        self.capability = TestingCapability()
        super().__init__("QA_AGENT")

    async def handle_event(self, event: Event):

        if event.event_type != TASK_ASSIGNED:
            return

        assigned_agent = event.payload["assigned_agent"]

        if assigned_agent != self.agent_name:
            return

        print(f"\n[{self.agent_name}] Received Task : {event.event_type}")

        task_id = event.payload["task_id"]
        task_name = event.payload["task_name"]
        workflow_id = event.payload["workflow_id"]
        dependency_outputs = event.payload.get("dependency_outputs", {})
        workflow_context = event.payload.get("workflow_context", {})
        memory = memory_manager.get_memory(self.agent_name)

        print("\nDependency Ouput")
        print(dependency_outputs)
        print(f"\n[{self.agent_name}] : Task belongs to me")
        print(f"Workflow ID : {workflow_id}")
        print(f"Task ID : {task_id}")
        print(f"Task Name : {task_name}")

        result = self.capability.execute(
            task_name, dependency_outputs, workflow_context
        )
        memory.store(task_name, result)
        completed_event = Event(
            event_type=TASK_COMPLETED,
            source_agent=self.agent_name,
            correlation_id=event.correlation_id,
            payload={
                "workflow_id": workflow_id,
                "task_id": task_id,
                "status": "COMPLETED",
                "result": result,
            },
        )

        print("\nQA Agent Memory")
        print(memory.get_all())
        await self.publish_event(completed_event)
