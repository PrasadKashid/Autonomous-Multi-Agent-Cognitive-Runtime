from typing import Dict, Optional
import json

from app.orchestration.workflows.task import Task
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.task_model import TaskModel


class TaskRepository:

    def save(self, task: Task, workflow_id):
        db: Session = SessionLocal()

        try:
            existing = (
                db.query(TaskModel).filter(TaskModel.task_id == task.task_id).first()
            )
            if existing:
                return existing

            db_task = TaskModel(
                task_id=task.task_id,
                workflow_id=workflow_id,
                task_name=task.task_name,
                assigned_agent=task.assigned_agent,
                capability=task.capability,
                status=task.status,
                dependencies=",".join(task.dependencies),
                priority=task.priority,
                retry_count=task.retry_count,
                max_retries=task.max_retries,
                output=task.output,
                created_at=task.created_at,
            )
            db.add(db_task)
            db.commit()
        finally:
            db.close()

    def get(self, task_id: str) -> Optional[Task]:

        db: Session = SessionLocal()
        try:
            task = db.query(TaskModel).filter(TaskModel.task_id == task_id).first()
            if task and task.output:
                task.output = json.loads(task.output)
            return task
        finally:
            db.close()

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

    def get_by_workflow(self, workflow_id):

        db = SessionLocal()

        try:
            tasks = (
                db.query(TaskModel).filter(TaskModel.workflow_id == workflow_id).all()
            )
            for task in tasks:
                if task.output:
                    task.output = json.loads(task.output)
            return tasks

        finally:
            db.close()

    def get_by_status(self, status):
        db = SessionLocal()

        try:
            return db.query(TaskModel).filter(TaskModel.status == status).all()
        finally:
            db.close()


task_repository = TaskRepository()
