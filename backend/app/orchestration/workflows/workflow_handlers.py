from app.orchestration.event_bus.event_types import (
    TASK_COMPLETED,
    TASK_ASSIGNED,
    WORKFLOW_COMPLETED,
    WORKFLOW_FAILED,
)

from app.orchestration.workflows.workflow_manager import workflow_manager
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.bus import event_bus
from app.orchestration.workflows.states import RUNNING, FAILED
from app.db.repositories.workflow_context_repository import workflow_context_repository


async def task_completed_handler(event: Event):

    if event.event_type != TASK_COMPLETED:
        return

    completed_task_id = event.payload["task_id"]
    workflow_id = event.payload["workflow_id"]
    status = event.payload["status"]

    # Update task status

    workflow_manager.update_task_status(
        task_id=completed_task_id,
        status=status,
    )

    # Save task output

    output = event.payload.get("result")

    if output:
        workflow_manager.update_task_output(
            task_id=completed_task_id,
            output=output,
        )

    task = workflow_manager.get_task(completed_task_id)

    # Update workflow context

    if output:
        workflow_manager.update_workflow_context(
            workflow_id=workflow_id,
            key=task.task_name,
            value={
                "status": status,
                "output": output,
            },
        )
    workflow_context_repository.save(
        workflow_id=workflow_id, task_name=task.task_name, status=status, output=output
    )

    print("\n===== WORKFLOW CONTEXT =====")
    print(workflow_manager.get_workflow_context(workflow_id))

    print("\n=== TASK COMPLETED ===")
    print("Workflow ID :", workflow_id)
    print("Task ID :", completed_task_id)
    print("Task Name :", task.task_name)
    print("Task Status :", task.status)

    # Check workflow completion

    workflow_completed = workflow_manager.check_workflow_completion(workflow_id)

    print("Workflow Completed Flag =", workflow_completed)

    if workflow_completed:

        workflow = workflow_manager.get_workflow(workflow_id)

        print("\n===== WORKFLOW OUTPUTS =====")

        for workflow_task_id in workflow.tasks:

            workflow_task = workflow_manager.get_task(workflow_task_id)

            print("\nTask :", workflow_task.task_name)
            print("Output :", workflow_task.output)

        workflow_completed_event = Event(
            event_type=WORKFLOW_COMPLETED,
            source_agent="WORKFLOW_MANAGER",
            correlation_id=event.correlation_id,
            payload={
                "workflow_id": workflow.workflow_id,
                "workflow_name": workflow.workflow_name,
            },
        )

        await event_bus.publish(workflow_completed_event)

        return

    # Find next runnable tasks

    runnable_tasks = workflow_manager.get_runnable_tasks(workflow_id)

    for runnable_task in runnable_tasks:

        print(f"\nRunnable Task : {runnable_task.task_name}")

        workflow_manager.update_task_status(
            task_id=runnable_task.task_id,
            status=RUNNING,
        )

        dependency_output = workflow_manager.get_dependency_output(runnable_task)

        workflow_context = workflow_manager.get_workflow_context(workflow_id)

        assigned_event = Event(
            event_type=TASK_ASSIGNED,
            source_agent="WORKFLOW_MANAGER",
            correlation_id=event.correlation_id,
            payload={
                "workflow_id": workflow_id,
                "task_id": runnable_task.task_id,
                "task_name": runnable_task.task_name,
                "assigned_agent": runnable_task.assigned_agent,
                "dependency_outputs": dependency_output,
                "workflow_context": workflow_context,
            },
        )

        await event_bus.publish(assigned_event)


async def workflow_failed_handler(event: Event):

    if event.event_type != WORKFLOW_FAILED:
        return

    workflow_id = event.payload["workflow_id"]

    workflow = workflow_manager.get_workflow(workflow_id=workflow_id)

    if not workflow:
        return

    workflow.status = FAILED

    print("\n===== WORKFLOW FAILED =====")
    print("Workflow ID :", workflow.workflow_id)
    print("Workflow Name :", workflow.workflow_name)
    print("Failed Task :", event.payload["task_name"])
