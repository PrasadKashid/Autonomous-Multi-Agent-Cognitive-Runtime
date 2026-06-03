from typing import Dict, List, Optional

from app.orchestration.workflows.workflow import WorkFlow
from app.orchestration.workflows.task import Task
from app.orchestration.workflows.states import *


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
            return False

        # IMPORTANT FIX
        if workflow.status == COMPLETED:
            return False

        tasks = [self.get_task(task_id) for task_id in workflow.tasks]
        tasks = [task for task in tasks if task]

        total = len(tasks)

        if total == 0:
            return False

        completed = sum(task.status == COMPLETED for task in tasks)

        percentage = completed * 100 / total
        workflow.progress = percentage

        print(f"\nTASK COMPLETED % {percentage:.2f}")

        if completed == total:

            workflow.status = COMPLETED

            print("\nWORKFLOW COMPLETED")
            print("Workflow ID :", workflow.workflow_id)
            print("Workflow Name :", workflow.workflow_name)

            return True

        return False

    def get_runnable_tasks(self, workflow_id):
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return []

        runnable_task = []
        tasks = [self.get_task(task_id=task_id) for task_id in workflow.tasks]
        tasks = [task for task in tasks if task]

        for task in tasks:

            if task.status == COMPLETED:
                continue

            if len(task.dependencies) == 0:
                runnable_task.append(task)
                continue

            dependencies_completed = True

            for dependency_id in task.dependencies:
                dependency_task = self.get_task(dependency_id)

                if not dependency_task:
                    dependencies_completed = False
                    break

                if dependency_task.status != COMPLETED:
                    dependencies_completed = False
                    break
            if dependencies_completed:
                runnable_task.append(task)

        return runnable_task

    def update_task_output(
        self,
        task_id: str,
        output,
    ):
        task = self.get_task(task_id)

        if task:
            task.output = output

    def get_dependency_output(self, task: Task):
        outputs = {}

        for dependency_id in task.dependencies:
            dependency_task = self.get_task(dependency_id)
            if dependency_task:
                outputs[dependency_task.task_name] = dependency_task.output
        return outputs


workflow_manager = WorkflowManager()
