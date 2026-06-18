from app.db.database import Base
from sqlalchemy import String, Column, Integer, Text


class AgentMemories(Base):
    __tablename__ = "agent_memories"
    id = Column(Integer, primary_key=True)
    agent_name = Column(String)
    task_name = Column(String)
    memory_data = Column(Text)
