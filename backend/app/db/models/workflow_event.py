from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class WorkflowEventModel(Base):
    __tablename__ = "workflow_events"

    id = Column(Integer, primary_key=True, index=True)

    workflow_id = Column(String, nullable=False)
    task_id = Column(String, nullable=True)
    task_name = Column(String, nullable = True)
    event_type = Column(String, nullable=False)

    agent = Column(String, nullable=True)

    message = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
