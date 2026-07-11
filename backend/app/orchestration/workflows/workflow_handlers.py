from app.orchestration.event_bus.event_types import (
    TASK_COMPLETED,
    TASK_ASSIGNED,
    WORKFLOW_COMPLETED,
    WORKFLOW_FAILED,
    WORKFLOW_CREATED,
)

from app.orchestration.workflows.workflow_manager import workflow_manager
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.bus import event_bus
from app.orchestration.workflows.states import (
    RUNNING,
    FAILED,
    COMPLETED,
    PENDING,
)


async def task_completed_handler(event: Event):

    if event.event_type != TASK_COMPLETED:
        return

    completed_task_id = event.payload["task_id"]
    workflow_id = event.payload["workflow_id"]
    status = event.payload["status"]

    task = workflow_manager.get_task(completed_task_id)

    if task is None:
        return

    # Ignore duplicate completion events
    if task.status == COMPLETED:
        return

    workflow_manager.update_task_status(
        task_id=completed_task_id,
        status=status,
    )

    output = event.payload.get("result")

    if output:
        workflow_manager.update_task_output(
            task_id=completed_task_id,
            output=output,
        )

    task = workflow_manager.get_task(completed_task_id)

    workflow_manager.update_workflow_context(
        workflow_id=workflow_id,
        key=task.task_name,
        value={
            "status": status,
            "output": output,
        },
    )

    if workflow_manager.check_workflow_completion(workflow_id):

        workflow = workflow_manager.get_workflow(workflow_id)

        await event_bus.publish(
            Event(
                event_type=WORKFLOW_COMPLETED,
                source_agent="WORKFLOW_MANAGER",
                correlation_id=event.correlation_id,
                payload={
                    "workflow_id": workflow.workflow_id,
                    "workflow_name": workflow.workflow_name,
                },
            )
        )

        return

    runnable_tasks = workflow_manager.get_runnable_tasks(workflow_id)

    for task in runnable_tasks:

        current_task = workflow_manager.get_task(task.task_id)

        if current_task is None:
            continue

        if current_task.status != PENDING:
            continue

        workflow_manager.update_task_status(
            current_task.task_id,
            RUNNING,
        )

        dependency_outputs = workflow_manager.get_dependency_output(current_task)

        workflow_context = workflow_manager.get_workflow_context(workflow_id)

        await event_bus.publish(
            Event(
                event_type=TASK_ASSIGNED,
                source_agent="WORKFLOW_MANAGER",
                correlation_id=event.correlation_id,
                payload={
                    "workflow_id": workflow_id,
                    "task_id": current_task.task_id,
                    "task_name": current_task.task_name,
                    "assigned_agent": current_task.assigned_agent,
                    "dependency_outputs": dependency_outputs,
                    "workflow_context": workflow_context,
                },
            )
        )


async def workflow_created_handler(event: Event):

    if event.event_type != WORKFLOW_CREATED:
        return

    workflow_id = event.payload["workflow_id"]

    runnable_tasks = workflow_manager.get_runnable_tasks(workflow_id)

    for task in runnable_tasks:

        if task.status != PENDING:
            continue

        workflow_manager.update_task_status(
            task.task_id,
            RUNNING,
        )

        workflow_context = workflow_manager.get_workflow_context(workflow_id)

        await event_bus.publish(
            Event(
                event_type=TASK_ASSIGNED,
                source_agent="WORKFLOW_MANAGER",
                correlation_id=event.correlation_id,
                payload={
                    "workflow_id": workflow_id,
                    "task_id": task.task_id,
                    "task_name": task.task_name,
                    "assigned_agent": task.assigned_agent,
                    "workflow_context": workflow_context,
                    "dependency_outputs": {},
                },
            )
        )
