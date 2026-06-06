from app.agents.base.base_agent import BaseAgent
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import (
    TASK_ASSIGNED,
    TASK_COMPLETED,
    TASK_FAILED,
)
from app.orchestration.workflows.workflow_manager import workflow_manager


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
        dependency_outputs = event.payload.get("dependency_outputs", {})

        print("\nDependency Output")
        print(dependency_outputs)

        print(f"\n[{self.agent_name}] : Task belongs to me")
        print(f"Workflow ID : {workflow_id}")
        print(f"Task ID : {task_id}")
        print(f"Task Name : {task_name}")

        task = workflow_manager.get_task(task_id)

        # Simulate failure for JWT task (first 2 attempts)

        task = workflow_manager.get_task(task_id)

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

        elif "Login API" in task_name:

            print(f"\n[{self.agent_name}] Creating Login API...")

            result = {
                "endpoint": "/auth/login",
                "method": "POST",
            }

        else:

            print(f"\n[{self.agent_name}] Developing Feature...")

            result = {
                "message": "Feature Implemented",
            }

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

        await self.publish_event(completed_event)
