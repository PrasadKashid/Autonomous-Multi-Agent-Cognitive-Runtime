from app.orchestration.event_bus.event_types import TASK_COMPLETED
from app.orchestration.workflows.workflow_manager import workflow_manager
from app.orchestration.event_bus.base import Event


async def task_completed_handler(event: Event):
    if event.event_type != TASK_COMPLETED:
        return

    task_id = event.payload["task_id"]
    workflow_id = event.payload["workflow_id"]
    status = event.payload["status"]

    workflow_manager.update_task_status(task_id=task_id, status=status)

    task = workflow_manager.get_task(task_id)

    print("\n=== TASK COMPLETED ===")
    print("Workflow ID :", workflow_id)
    print("Task ID :", task_id)
    print("Task Name :", task.task_name)
    print("Task Status :", task.status)
    workflow_manager.check_workflow_completion(workflow_id)
