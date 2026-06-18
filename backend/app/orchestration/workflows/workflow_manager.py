from typing import Dict, List, Optional
import json
from app.orchestration.workflows.workflow import WorkFlow
from app.orchestration.workflows.task import Task
from app.orchestration.workflows.states import *

from app.db.repositories.workflow_repository import workflow_repository
from app.db.repositories.task_repository import task_repository


class WorkflowManager:

    def __init__(self):
        self.workflows: Dict[str, WorkFlow] = {}
        self.tasks: Dict[str, Task] = {}

    def create_workflow(
        self,
        workflow_name: str,
        correlation_id: str,
    ) -> WorkFlow:

        workflow = WorkFlow(
            workflow_name=workflow_name,
            correlation_id=correlation_id,
        )

        # Runtime Memory
        self.workflows[workflow.workflow_id] = workflow

        # Persist to DB
        workflow_repository.save(workflow)

        return workflow

    def get_workflow(
        self,
        workflow_id: str,
    ) -> Optional[WorkFlow]:

        return self.workflows.get(workflow_id)

    def update_workflow_status(
        self,
        workflow_id: str,
        status: str,
    ):

        workflow = self.get_workflow(workflow_id)

        if workflow:
            workflow.status = status

    def add_task_to_workflow(
        self,
        workflow_id: str,
        task: Task,
    ):

        workflow = self.get_workflow(workflow_id)

        if not workflow:
            return

        workflow.tasks.append(task.task_id)

        # Runtime Memory
        self.tasks[task.task_id] = task

        # Persist Copy
        task_repository.save(task, workflow_id)

    def get_task(
        self,
        task_id: str,
    ) -> Optional[Task]:

        # IMPORTANT:
        # Runtime execution should always use memory
        task = task_repository.get(task_id=task_id)
        print("DB")
        print(task.__dict__)
        return self.tasks.get(task_id)
        # return task_repository.get(task_id)

    def get_all_workflows(self) -> List[WorkFlow]:

        return list(self.workflows.values())

    def update_task_status(
        self,
        task_id: str,
        status: str,
    ):
        # Update runtime object
        task = self.get_task(task_id)

        if task:
            task.status = status

        # Update DB copy
        task_repository.update_status(
            task_id=task_id,
            status=status,
        )

    def update_task_output(self, task_id: str, output):

        task = self.get_task(task_id)

        if task:
            task.output = output
        task_repository.update_output(
            task_id=task_id,
            output=json.dumps(output),
        )

    def increment_retry_count(
        self,
        task_id: str,
    ):

        task = self.get_task(task_id)

        if task:
            task.retry_count += 1
        task_repository.increment_retry_count(task_id=task_id)

    def check_workflow_completion(
        self,
        workflow_id,
    ):

        workflow = self.get_workflow(workflow_id)

        if not workflow:
            return False

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

    def get_runnable_tasks(
        self,
        workflow_id,
    ):

        workflow = self.get_workflow(workflow_id)

        if not workflow:
            return []

        runnable_tasks = []

        tasks = [self.get_task(task_id) for task_id in workflow.tasks]

        tasks = [task for task in tasks if task]

        for task in tasks:

            if task.status in [COMPLETED, RUNNING]:
                continue

            if len(task.dependencies) == 0:
                runnable_tasks.append(task)
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
                runnable_tasks.append(task)

        return runnable_tasks

    def get_dependency_output(
        self,
        task: Task,
    ):

        outputs = {}

        for dependency_id in task.dependencies:

            dependency_task = self.get_task(dependency_id)

            if dependency_task:

                outputs[dependency_task.task_name] = dependency_task.output

        return outputs

    def update_workflow_context(
        self,
        workflow_id,
        key,
        value,
    ):

        workflow = self.get_workflow(workflow_id)

        if workflow:
            workflow.context[key] = value

    def get_workflow_context(
        self,
        workflow_id,
    ):

        workflow = self.get_workflow(workflow_id)

        if workflow:
            return workflow.context

        return {}

    def build_workflow_context(
        self,
        workflow_id,
    ):

        workflow = self.get_workflow(workflow_id)

        if not workflow:
            return {}

        context = {}

        for task_id in workflow.tasks:

            task = self.get_task(task_id)

            if not task:
                continue

            context[task.task_name] = {
                "status": task.status,
                "output": task.output,
            }

        return context


workflow_manager = WorkflowManager()
