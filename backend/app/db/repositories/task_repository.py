from typing import Dict, Optional
import json

from app.orchestration.workflows.task import Task
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.task_model import TaskModel


class TaskRepository:
    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def save(self, task: Task, workflow_id):
        db: Session = SessionLocal()

        try:
            db_task = TaskModel(
                task_id=task.task_id,
                workflow_id=workflow_id,
                task_name=task.task_name,
                assigned_agent=task.assigned_agent,
                status=task.status,
                retry_count=task.retry_count,
                dependencies=",".join(task.dependencies),
            )
            db.add(db_task)
            db.commit()
        finally:
            db.close()
        # self._tasks[task.task_id] = task

    def get(self, task_id: str) -> Optional[Task]:

        db: Session = SessionLocal()
        try:
            return db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
        finally:
            db.close()
        # return self._tasks.get(task_id)

    def get_all(self):
        db: Session = SessionLocal()
        try:
            return db.query(TaskModel).all()
        finally:
            db.close()

    def update_status(self, task_id, status):
        db: Session = SessionLocal()
        try:
            task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
            if not task:
                return None
            task.status = status

            db.commit()
            db.refresh(task)

            return task
        finally:
            db.close()

    def update_output(self, task_id, output):
        db: Session = SessionLocal()

        try:
            task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
            if not task:
                return None
            task.output = json.dumps(output)
            db.commit()
            db.refresh(task)
            return task
        finally:
            db.close()

    def increment_retry_count(self, task_id):
        db: Session = SessionLocal()

        try:
            task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
            if not task:
                return None
            task.retry_count += 1

            db.commit()
            db.refresh(task)
            return task
        finally:
            db.close()


task_repository = TaskRepository()
