from sqlalchemy import Column, String, Integer, Text
from app.db.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"
    task_id = Column(String, primary_key=True)
    workflow_id = Column(String)
    task_name = Column(String)
    assigned_agent = Column(String)
    status = Column(String)
    retry_count = Column(Integer)
    dependencies = Column(String)
    output = Column(Text, nullable=True)
