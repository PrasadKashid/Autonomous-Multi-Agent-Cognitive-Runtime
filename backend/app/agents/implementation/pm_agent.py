from app.agents.base.base_agent import BaseAgent

from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import (
    TASK_CREATED,
    TASK_ASSIGNED,
)

from app.orchestration.workflows.workflow_manager import workflow_manager
from app.orchestration.workflows.task import Task


class PMAgent(BaseAgent):

    def __init__(self):
        super().__init__("PM_Agent")

    async def handle_event(self, event: Event):

        print(f"[PM_Agent] Received Event : {event.event_type}")

        if event.event_type != TASK_CREATED:
            return

        print("[PM_Agent] Breaking tasks into subtasks")

        created_workflow = workflow_manager.create_workflow(
            workflow_name=event.payload["task"],
            correlation_id=event.correlation_id,
        )

        print("Workflow ID :", created_workflow.workflow_id)
        print("Workflow Name :", created_workflow.workflow_name)
        print("Workflow Status :", created_workflow.status)

        subtasks = [
            "Design Authentication Architecture",
            "Build JWT Service",
            "Create Login API",
            "Write Authentication Tests",
        ]

        # -----------------------------
        # Phase 1 - Create all tasks
        # -----------------------------

        tasks_to_assign = []

        for subtask in subtasks:

            task = Task(subtask)

            if "Design" in subtask:
                task.assigned_agent = "ARCHITECT_AGENT"

            elif "Build" in subtask or "Create" in subtask:
                task.assigned_agent = "DEVELOPER_AGENT"

            elif "Test" in subtask:
                task.assigned_agent = "QA_AGENT"

            workflow_manager.add_task_to_workflow(
                created_workflow.workflow_id,
                task,
            )

            tasks_to_assign.append(task)

            print("\nTask Created")
            print("Task ID :", task.task_id)
            print("Task Name :", task.task_name)
            print("Assigned Agent :", task.assigned_agent)
            print("Task Status :", task.status)

        print(f"\n[PM_Agent] Total Tasks Created : " f"{len(created_workflow.tasks)}")

        # -----------------------------
        # Phase 2 - Assign all tasks
        # -----------------------------

        for task in tasks_to_assign:

            assigned_event = Event(
                event_type=TASK_ASSIGNED,
                source_agent=self.agent_name,
                correlation_id=event.correlation_id,
                payload={
                    "workflow_id": created_workflow.workflow_id,
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "assigned_agent": task.assigned_agent,
                },
            )

            await self.publish_event(assigned_event)
