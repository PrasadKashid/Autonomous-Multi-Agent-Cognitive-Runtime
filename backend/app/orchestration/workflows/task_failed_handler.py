# app/orchestration/workflows/task_failed_handler.py

from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import (
    TASK_FAILED,
    TASK_ASSIGNED,
    WORKFLOW_FAILED,
)
from app.orchestration.event_bus.bus import event_bus
from app.orchestration.workflows.workflow_manager import workflow_manager
from app.orchestration.workflows.states import RUNNING


async def task_failed_handler(event: Event):

    if event.event_type != TASK_FAILED:
        return

    task_id = event.payload["task_id"]
    workflow_id = event.payload["workflow_id"]

    task = workflow_manager.get_task(task_id)

    if not task:
        return

    print("\n===== TASK FAILED =====")
    print("Task :", task.task_name)

    workflow_manager.increment_retry_count(task_id)

    print(f"Retry Count : {task.retry_count}/{task.max_retries}")

    # Retry available
    if task.retry_count < task.max_retries:

        print("Reassigning task...")

        workflow_manager.update_task_status(
            task_id=task_id,
            status=RUNNING,
        )

        dependency_outputs = workflow_manager.get_dependency_output(task)
        workflow = workflow_manager.get_workflow(workflow_id)

        print("\n===== WORKFLOW OBJECT =====")
        print(workflow)
        print(workflow.context if workflow else "NO WORKFLOW")
        workflow_context = workflow_manager.get_workflow_context(
            workflow_id=workflow_id
        )

        retry_event = Event(
            event_type=TASK_ASSIGNED,
            source_agent="WORKFLOW_MANAGER",
            correlation_id=event.correlation_id,
            payload={
                "workflow_id": workflow_id,
                "task_id": task.task_id,
                "task_name": task.task_name,
                "assigned_agent": task.assigned_agent,
                "dependency_outputs": dependency_outputs,
                "workflow_context": workflow_context,
            },
        )

        await event_bus.publish(retry_event)

    else:

        print("\n===== MAX RETRIES EXCEEDED =====")
        print("Task :", task.task_name)
        print("Workflow Failed")
        workflow_failed_event = Event(
            event_type=WORKFLOW_FAILED,
            source_agent="WORKFLOW_MANAGER",
            correlation_id=event.correlation_id,
            payload={
                "workflow_id": workflow_id,
                "task_id": task.task_id,
                "task_name": task.task_name,
            },
        )
        await event_bus.publish(workflow_failed_event)
