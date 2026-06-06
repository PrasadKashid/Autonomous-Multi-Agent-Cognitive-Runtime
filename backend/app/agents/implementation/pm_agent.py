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

        # Create Tasks

        architecture_task = Task("Design Authentication Architecture")
        architecture_task.assigned_agent = "ARCHITECT_AGENT"

        jwt_task = Task("Build JWT Service")
        jwt_task.assigned_agent = "DEVELOPER_AGENT"

        login_task = Task("Create Login API")
        login_task.assigned_agent = "DEVELOPER_AGENT"

        test_task = Task("Write Authentication Tests")
        test_task.assigned_agent = "QA_AGENT"

        # Define Dependencies

        jwt_task.dependencies.append(architecture_task.task_id)

        login_task.dependencies.append(jwt_task.task_id)

        test_task.dependencies.append(login_task.task_id)

        tasks = [
            architecture_task,
            jwt_task,
            login_task,
            test_task,
        ]

        # Store Tasks

        for task in tasks:

            workflow_manager.add_task_to_workflow(
                created_workflow.workflow_id,
                task,
            )

            print("\nTask Created")
            print("Task ID :", task.task_id)
            print("Task Name :", task.task_name)
            print("Assigned Agent :", task.assigned_agent)
            print("Task Status :", task.status)
            print("Dependencies :", task.dependencies)

        print(f"\n[PM_Agent] Total Tasks Created : {len(tasks)}")

        # Assign Only Tasks Without Dependencies

        for task in tasks:

            if len(task.dependencies) > 0:
                continue

            workflow_context = workflow_manager.get_workflow_context(
                created_workflow.workflow_id
            )

            assigned_event = Event(
                event_type=TASK_ASSIGNED,
                source_agent=self.agent_name,
                correlation_id=event.correlation_id,
                payload={
                    "workflow_id": created_workflow.workflow_id,
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "assigned_agent": task.assigned_agent,
                    "workflow_context": workflow_context,
                },
            )

            await self.publish_event(assigned_event)
