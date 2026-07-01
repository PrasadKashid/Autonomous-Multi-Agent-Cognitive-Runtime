from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models.workflow_event import WorkflowEventModel


class WorkflowEventRepository:

    def save(
        self,
        workflow_id,
        event_type,
        agent=None,
        task_id=None,
        task_name=None,
        message=None,
    ):
        db: Session = SessionLocal()

        try:
            event = WorkflowEventModel(
                workflow_id=workflow_id,
                task_id=task_id,
                task_name=task_name,
                event_type=event_type,
                agent=agent,
                message=message,
            )

            db.add(event)
            db.commit()
            db.refresh(event)
            return event
        finally:
            db.close()

    def get_by_workflow(self, workflow_id):
        db: Session = SessionLocal()

        try:
            return (
                db.query(WorkflowEventModel)
                .filter(WorkflowEventModel.workflow_id == workflow_id)
                .order_by(WorkflowEventModel.created_at.asc())
                .all()
            )
        finally:
            db.close()

    def get_latest_events(self, limit=50):
        db: Session = SessionLocal()
        try:
            return (
                db.query(WorkflowEventModel)
                .order_by(WorkflowEventModel.created_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def delete_by_workflow(self, workflow_id):
        db: Session = SessionLocal()

        try:
            (
                db.query(WorkflowEventModel)
                .filter(WorkflowEventModel.workflow_id == workflow_id)
                .delete()
            )
            db.commit()
        finally:
            db.close()


workflow_event_repository = WorkflowEventRepository()