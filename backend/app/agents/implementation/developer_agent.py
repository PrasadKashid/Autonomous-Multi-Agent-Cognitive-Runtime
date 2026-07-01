from app.agents.base.base_agent import BaseAgent
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import (
    TASK_ASSIGNED,
    TASK_COMPLETED,
    TASK_FAILED,
)
from app.orchestration.workflows.workflow_manager import workflow_manager
from app.capabilities.backend import BackendCapability
import os


class DeveloperAgent(BaseAgent):

    def __init__(self):
        self.capability = BackendCapability()
        super().__init__("DEVELOPER_AGENT")

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

        dependency_outputs = event.payload.get(
            "dependency_outputs",
            {},
        )

        workflow_context = event.payload.get(
            "workflow_context",
            {},
        )

        print("\nDependency Output")
        print(dependency_outputs)

        print("\nWorkflow Context")
        print(workflow_context)

        print(f"\n[{self.agent_name}] : Task belongs to me")
        print(f"Workflow ID : {workflow_id}")
        print(f"Task ID : {task_id}")
        print(f"Task Name : {task_name}")

        task = workflow_manager.get_task(task_id)

        if not task:
            print(f"[{self.agent_name}] Task not found")
            return

        # Retry simulation for JWT task

        if "JWT" in task_name and task.retry_count < 2:

            print(f"\n[{self.agent_name}] Simulating JWT Service Failure...")

            failed_event = Event(
                event_type=TASK_FAILED,
                source_agent=self.agent_name,
                correlation_id=event.correlation_id,
                payload={
                    "workflow_id": workflow_id,
                    "task_id": task_id,
                    "task_name": task_name,
                },
            )

            await self.publish_event(failed_event)
            return

        print(f"\n[{self.agent_name}] Executing Backend Capability...")

        result = self.capability.execute(
            task_name,
            dependency_outputs,
            workflow_context,
        )

        self.store_memory(
            workflow_id=workflow_id, task_name=task_name, memory_data=result
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

        print("\nAgent Memory")
        print(self.get_recent_memory())

        await self.publish_event(completed_event)
        # if task_name == "Build JWT Service":
        #     print("\n===== SIMULATING CRASH =====")
        #     os._exit(1)
