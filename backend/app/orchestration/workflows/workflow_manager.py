from typing import Dict, List, Optional
import json
from app.orchestration.workflows.workflow import WorkFlow
from app.orchestration.workflows.task import Task
from app.orchestration.workflows.states import *

from app.db.repositories.workflow_repository import workflow_repository
from app.db.repositories.task_repository import task_repository
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import TASK_ASSIGNED
from app.orchestration.event_bus.bus import event_bus
import os


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
            output=output,
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
        workflow_repository.update_progress(workflow_id, percentage)

        print(f"\nTASK COMPLETED % {percentage:.2f}")
        # if percentage == 25:
        #     print("testing recovery")
        #     os._exit(1)

        if completed == total:

            workflow.status = COMPLETED
            workflow_repository.update_status(workflow_id, COMPLETED)

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

        if not workflow:
            return

        # if not hasattr(workflow, "context"):
        #     workflow.context = {}

        workflow.context[key] = value

    def get_workflow_context(
        self,
        workflow_id,
    ):

        return self.build_workflow_context(workflow_id)

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

    def recover_workflows(self):

        # Clear runtime state
        self.workflows.clear()
        self.tasks.clear()

        workflows = workflow_repository.get_incomplete_workflows()

        print("\n===== DB WORKFLOWS =====")

        for wf in workflows:
            print(f"{wf.workflow_id} {wf.status}")

        if not workflows:
            print("No workflows to recover")
            return

        for db_workflow in workflows:

            print(f"\nRecovering Workflow {db_workflow.workflow_id}")

            runtime_workflow = WorkFlow(
                workflow_name=db_workflow.workflow_name,
                correlation_id=db_workflow.correlation_id,
            )

            runtime_workflow.workflow_id = db_workflow.workflow_id
            runtime_workflow.status = db_workflow.status
            runtime_workflow.progress = db_workflow.progress
            runtime_workflow.tasks = []

            # Restore workflow context
            if hasattr(db_workflow, "context") and db_workflow.context:

                if isinstance(db_workflow.context, str):

                    try:
                        runtime_workflow.context = json.loads(db_workflow.context)

                    except Exception:
                        runtime_workflow.context = {}

                else:
                    runtime_workflow.context = db_workflow.context

            else:
                runtime_workflow.context = {}

            self.workflows[runtime_workflow.workflow_id] = runtime_workflow

            # Load Tasks

            tasks = task_repository.get_by_workflow(db_workflow.workflow_id)

            task_ids = {task.task_id for task in tasks}

            for db_task in tasks:

                # Dependencies

                if isinstance(db_task.dependencies, str):

                    dependencies = (
                        db_task.dependencies.split(",") if db_task.dependencies else []
                    )

                elif isinstance(db_task.dependencies, list):

                    dependencies = db_task.dependencies

                else:

                    dependencies = []

                # Runtime Task

                runtime_task = Task(
                    task_name=db_task.task_name,
                    capability=db_task.capability,
                )

                runtime_task.task_id = db_task.task_id
                runtime_task.assigned_agent = db_task.assigned_agent
                runtime_task.status = db_task.status
                runtime_task.dependencies = dependencies
                runtime_task.retry_count = db_task.retry_count
                runtime_task.max_retries = db_task.max_retries

                # Reset RUNNING Tasks

                if runtime_task.status == RUNNING:

                    print(
                        f"Resetting RUNNING task "
                        f"{runtime_task.task_name} -> PENDING"
                    )

                    runtime_task.status = PENDING

                    task_repository.update_status(
                        task_id=runtime_task.task_id,
                        status=PENDING,
                    )

                # Restore Output

                if db_task.output is not None:

                    if isinstance(db_task.output, str):

                        try:
                            runtime_task.output = json.loads(db_task.output)

                        except Exception:
                            runtime_task.output = db_task.output

                    else:
                        runtime_task.output = db_task.output

                else:

                    runtime_task.output = None

                # Dependency Validation

                for dep in dependencies:

                    if dep not in task_ids:

                        print(
                            f"WARNING: Missing dependency "
                            f"{dep} for "
                            f"{runtime_task.task_name}"
                        )

                # Store Runtime Task

                self.tasks[runtime_task.task_id] = runtime_task

                runtime_workflow.tasks.append(runtime_task.task_id)

                print(
                    f"Recovered Task: "
                    f"{runtime_task.task_name} | "
                    f"Status={runtime_task.status} | "
                    f"Dependencies={runtime_task.dependencies}"
                )

            # Summary

            print(
                f"\nRecovered {len(tasks)} tasks "
                f"for workflow "
                f"{runtime_workflow.workflow_id}"
            )

            print(f"Workflow Status : " f"{runtime_workflow.status}")

            print(f"Workflow Progress : " f"{runtime_workflow.progress}")

            print("\n===== RECOVERED TASKS =====")

            for task_id in runtime_workflow.tasks:

                task = self.get_task(task_id)

                print(
                    f"Task={task.task_name}, "
                    f"Status={task.status}, "
                    f"Dependencies={task.dependencies}"
                )

            runnable_tasks = self.get_runnable_tasks(runtime_workflow.workflow_id)

            print(f"Runnable Tasks Found : " f"{len(runnable_tasks)}")

            for task in runnable_tasks:

                print(f"Ready To Resume : " f"{task.task_name}")

    async def resume_recovered_workflows(self):

        for workflow in self.workflows.values():

            if workflow.status == COMPLETED:
                continue

            runnable_tasks = self.get_runnable_tasks(workflow.workflow_id)

            for task in runnable_tasks:

                event = Event(
                    event_type=TASK_ASSIGNED,
                    source_agent="SYSTEM",
                    correlation_id=workflow.correlation_id,
                    payload={
                        "workflow_id": workflow.workflow_id,
                        "task_id": task.task_id,
                        "task_name": task.task_name,
                        "assigned_agent": task.assigned_agent,
                        "dependency_outputs": self.get_dependency_output(task),
                        "workflow_context": self.build_workflow_context(
                            workflow.workflow_id
                        ),
                    },
                )

                await event_bus.publish(event)


workflow_manager = WorkflowManager()
