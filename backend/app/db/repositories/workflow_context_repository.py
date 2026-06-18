from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.workflow_context_model import WorkflowContextModel
import json


class WorkflowContextRepository:
    def save(self, workflow_id, task_name, status, output):
        db: Session = SessionLocal()

        try:
            context = WorkflowContextModel(
                workflow_id=workflow_id,
                task_name=task_name,
                status=status,
                output=json.dumps(output),
            )

            db.add(context)
            db.commit()
        finally:
            db.close()

    def get_workflow_context(self, workflow_id):
        db: Session = SessionLocal()

        try:
            workflow_context = (
                db.query(WorkflowContextModel)
                .filter(WorkflowContextModel.workflow_id == workflow_id)
                .all()
            )
        finally:
            db.close()


workflow_context_repository = WorkflowContextRepository()
