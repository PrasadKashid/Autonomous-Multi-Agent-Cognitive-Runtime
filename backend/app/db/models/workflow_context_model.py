from app.db.database import Base
from sqlalchemy import Column, String, Integer, Text


class WorkflowContextModel(Base):

    __tablename__ = "workflow_contexts"

    id = Column(Integer, primary_key=True)
    workflow_id = Column(String)
    task_name = Column(String)
    status = Column(String)
    output = Column(Text)
