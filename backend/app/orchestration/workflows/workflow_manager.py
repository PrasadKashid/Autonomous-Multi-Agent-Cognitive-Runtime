from typing import Dict, List, Optional

from app.orchestration.workflows.workflow import WorkFlow
from app.orchestration.workflows.task import Task
from app.orchestration.workflows.states import COMPLETED, PENDING, RUNNING, FAILED


class WorkflowManager:

    def __init__(self):
        self.workflows: Dict[str, WorkFlow] = {}
        self.tasks: Dict[str, Task] = {}

    def create_workflow(self, workflow_name: str, correlation_id: str) -> WorkFlow:

        workflow = WorkFlow(workflow_name=workflow_name, correlation_id=correlation_id)

        self.workflows[workflow.workflow_id] = workflow

        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[WorkFlow]:

        return self.workflows.get(workflow_id)

    def update_workflow_status(self, workflow_id: str, status: str):

        workflow = self.get_workflow(workflow_id)

        if workflow:
            workflow.status = status

    def add_task_to_workflow(self, workflow_id: str, task: Task):

        workflow = self.get_workflow(workflow_id)

        if workflow:

            workflow.tasks.append(task.task_id)

            self.tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Optional[Task]:

        return self.tasks.get(task_id)

    def get_all_workflows(self) -> List[WorkFlow]:

        return list(self.workflows.values())

    def update_task_status(self, task_id: str, status: str):
        task = self.get_task(task_id)
        if task:
            task.status = status

    def check_workflow_completion(self, workflow_id):
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return

        tasks = [self.get_task(task_id=task_id) for task_id in workflow.tasks]
        tasks = [task for task in tasks if task]

        total = len(tasks)

        if total == 0:
            print("TASK COMPLETED % 0")
            return

        completed = sum(task.status == COMPLETED for task in tasks)
        if completed == total:
            workflow.status = COMPLETED

            print("\nWORKFLOW COMPLETED")
            print("Workflow ID :", workflow.workflow_id)
            print("Workflow Name :", workflow.workflow_name)
        percentage = completed * 100 / total
        workflow.progress = percentage

        print(f"\nTASK COMPLETED % {percentage:.2f}")


workflow_manager = WorkflowManager()
