from typing import Dict, Optional

from app.orchestration.workflows.workflow import WorkFlow

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.workflow_model import WorkflowModel


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


workflow_repository = WorkflowRepository()
