from sqlalchemy import Column, String, Integer, Text, JSON, DateTime
from app.db.database import Base


class TaskModel(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    task_id = Column(String, unique=True, nullable=False)
    workflow_id = Column(String, nullable=False)
    task_name = Column(String, nullable=False)
    assigned_agent = Column(String)
    capability = Column(String)
    status = Column(String)
    dependencies = Column(Text)
    priority = Column(String)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    output = Column(JSON)
    created_at = Column(DateTime)
