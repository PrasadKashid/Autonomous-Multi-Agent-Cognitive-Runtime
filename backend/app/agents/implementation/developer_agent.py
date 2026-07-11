from app.agents.base.base_agent import BaseAgent
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import TASK_ASSIGNED, TASK_COMPLETED
from app.orchestration.workflows.states import COMPLETED
from app.orchestration.workflows.workflow_manager import workflow_manager
from app.capabilities.backend import BackendCapability
from app.prompting.prompt_builder import prompt_builder


class DeveloperAgent(BaseAgent):

    def __init__(self):
        super().__init__("DEVELOPER_AGENT")
        self.capability = BackendCapability()

    async def handle_event(self, event: Event):

        if event.event_type != TASK_ASSIGNED:
            return

        if event.payload["assigned_agent"] != self.agent_name:
            return

        print(f"\n[{self.agent_name}] Received Task : {event.event_type}")

        task_id = event.payload["task_id"]
        task_name = event.payload["task_name"]
        workflow_id = event.payload["workflow_id"]

        dependency_outputs = event.payload.get(
            "dependency_outputs",
            {},
        )

        workflow_context = event.payload.get(
            "workflow_context",
            {},
        )

        print(f"\n[{self.agent_name}] Task belongs to me")

        task = workflow_manager.get_task(task_id)

        if not task:
            return
        if task.status == COMPLETED:
            return
        retrieved_memories = self.search_memory(task_name)

        print(f"\n[{self.agent_name}] Executing Backend Capability...")

        result = self.capability.execute(
            task_name=task_name,
            dependency_outputs=dependency_outputs,
            workflow_context=workflow_context,
            memories=retrieved_memories,
        )

        self.store_memory(
            workflow_id=workflow_id,
            task_name=task_name,
            memory_data=result,
        )

        completed_event = Event(
            event_type=TASK_COMPLETED,
            source_agent=self.agent_name,
            correlation_id=event.correlation_id,
            payload={
                "workflow_id": workflow_id,
                "task_id": task_id,
                "status": "COMPLETED",
                "result": result,
                "task_name": task_name,
            },
        )
        print(f"DEVELOPER RECEIVED -> " f"{task_name} | {task_id}")

        await self.publish_event(completed_event)
