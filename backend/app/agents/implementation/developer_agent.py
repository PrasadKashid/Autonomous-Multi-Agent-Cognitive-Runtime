from app.agents.base.base_agent import BaseAgent
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import (
    TASK_ASSIGNED,
    TASK_COMPLETED,
    TASK_FAILED,
)
from app.orchestration.workflows.workflow_manager import workflow_manager
from app.memory.memory_manager import memory_manager


class DeveloperAgent(BaseAgent):

    def __init__(self):
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

        memory = memory_manager.get_memory(self.agent_name)
        # JWT SERVICE TASK
        # Fail first 2 times, succeed on 3rd attempt

        if "JWT" in task_name:

            if task.retry_count < 2:

                print(f"\n[{self.agent_name}] Simulating JWT Service Failure...")

                failed_event = Event(
                    event_type=TASK_FAILED,
                    source_agent=self.agent_name,
                    correlation_id=event.correlation_id,
                    payload={
                        "workflow_id": workflow_id,
                        "task_id": task_id,
                    },
                )

                await self.publish_event(failed_event)
                return

            print(f"\n[{self.agent_name}] Building JWT Service...")

            result = {
                "service_name": "JWT Service",
                "algorithm": "HS256",
                "expiry": "15m",
            }

            memory.store(task_name, result)

        # LOGIN API TASK

        elif "Login API" in task_name:

            print(f"\n[{self.agent_name}] Creating Login API...")

            result = {
                "endpoint": "/auth/login",
                "method": "POST",
            }

            memory.store(task_name, result)

        # DEFAULT TASK

        else:

            print(f"\n[{self.agent_name}] Developing Feature...")

            result = {
                "message": "Feature Implemented",
            }
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

        print("\nAgent Memory")
        print(memory.get_all())

        await self.publish_event(completed_event)
