from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.db.database import Base


class AgentMemories(Base):
    __tablename__ = "agent_memories"

    id = Column(Integer, primary_key=True, index=True)

    workflow_id = Column(String, nullable=False, index=True)

    agent_name = Column(String, nullable=False, index=True)

    task_name = Column(String, nullable=False)

    memory_data = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
