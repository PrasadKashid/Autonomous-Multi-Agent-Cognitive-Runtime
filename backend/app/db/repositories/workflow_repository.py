from typing import Dict, Optional

from app.orchestration.workflows.workflow import WorkFlow

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.workflow_model import WorkflowModel
from app.orchestration.workflows.states import COMPLETED


class WorkflowRepository:

    def __init__(self):
        self._workflows: Dict[str, WorkFlow] = {}

    def save(self, workflow: WorkFlow):
        db: Session = SessionLocal()

        try:
            db_workflow = WorkflowModel(
                workflow_id=workflow.workflow_id,
                workflow_name=workflow.workflow_name,
                status=workflow.status,
                correlation_id=workflow.correlation_id,
                progress=workflow.progress,
            )
            db.add(db_workflow)
            db.commit()
        finally:
            db.close()

    def get(self, workflow_id):
        db: Session = SessionLocal()

        try:
            return (
                db.query(WorkflowModel)
                .filter(WorkflowModel.workflow_id == workflow_id)
                .first()
            )
        finally:
            db.close()

    def get_all(self):
        db: Session = SessionLocal()
        try:
            workflows = db.query(WorkflowModel).all()
            return workflows
        finally:
            db.close()

    def update_status(self, workflow_id, status):
        db: Session = SessionLocal()

        try:
            workflow = (
                db.query(WorkflowModel)
                .filter(WorkflowModel.workflow_id == workflow_id)
                .first()
            )

            if workflow:
                workflow.status = status
                db.commit()

        finally:
            db.close()

    def update_progress(self, workflow_id, progress):
        db: Session = SessionLocal()

        try:
            workflow = (
                db.query(WorkflowModel)
                .filter(WorkflowModel.workflow_id == workflow_id)
                .first()
            )

            if workflow:
                workflow.progress = progress
                db.commit()

        finally:
            db.close()

    def get_incomplete_workflows(self):
        db = SessionLocal()

        try:
            workflows = (
                db.query(WorkflowModel).filter(WorkflowModel.status != COMPLETED).all()
            )
            return workflows

        finally:
            db.close()


workflow_repository = WorkflowRepository()
