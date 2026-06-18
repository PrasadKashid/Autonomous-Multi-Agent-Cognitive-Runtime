from sqlalchemy import Column, String, Float
from app.db.database import Base


class WorkflowModel(Base):
    __tablename__ = "workflows"

    workflow_id = Column(String, primary_key=True)
    workflow_name = Column(String)
    status = Column(String)
    correlation_id = Column(String)
    progress = Column(Float)
