from app.agents.base.base_agent import BaseAgent

from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import (
    TASK_CREATED,
    TASK_ASSIGNED,
    WORKFLOW_CREATED,
)

from app.orchestration.workflows.workflow_manager import workflow_manager
from app.orchestration.workflows.task import Task

from app.agents.registry.agent_registry import agent_registry
from app.orchestration.planner.task_planner import task_planner


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

        planned_tasks = task_planner.create_plan(event.payload["task"])
        task_mapping = {}

        for planned_task in planned_tasks:

            task = Task(
                planned_task.task_name,
                capability=planned_task.capability,
            )

            task.assigned_agent = agent_registry.find_agent(planned_task.capability)

            task_mapping[planned_task.task_name] = task

        for planned_task in planned_tasks:

            current_task = task_mapping[planned_task.task_name]

            for dependency_name in planned_task.dependencies:

                dependency_task = task_mapping[dependency_name]

                current_task.dependencies.append(dependency_task.task_id)

        # Define Dependencies
        tasks = list(task_mapping.values())
        # Store Tasks

        for task in tasks:

            workflow_manager.add_task_to_workflow(
                created_workflow.workflow_id,
                task,
            )

        print(f"\n[PM_Agent] Total Tasks Created : {len(tasks)}")

        self.store_memory(
            workflow_id=created_workflow.workflow_id,
            task_name="Workflow Planning",
            memory_data=[
                {
                    "task": t.task_name,
                    "agent": t.assigned_agent,
                    "dependencies": t.dependencies,
                }
                for t in tasks
            ],
        )
        # for task in tasks:

        #     if len(task.dependencies) > 0:
        #         continue

        #     workflow_context = workflow_manager.get_workflow_context(
        #         created_workflow.workflow_id
        #     )

        #     assigned_event = Event(
        #         event_type=TASK_ASSIGNED,
        #         source_agent=self.agent_name,
        #         correlation_id=event.correlation_id,
        #         payload={
        #             "workflow_id": created_workflow.workflow_id,
        #             "task_id": task.task_id,
        #             "task_name": task.task_name,
        #             "assigned_agent": task.assigned_agent,
        #             "workflow_context": workflow_context,
        #         },
        #     )

        #     await self.publish_event(assigned_event)
        workflow_created_event = Event(
            event_type=WORKFLOW_CREATED,
            source_agent=self.agent_name,
            correlation_id=event.correlation_id,
            payload={
                "workflow_id": created_workflow.workflow_id,
            },
        )

        await self.publish_event(workflow_created_event)
