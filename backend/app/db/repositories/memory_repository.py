from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.agent_memories import AgentMemories
import json


class MemoryRepository:

    def save(
        self,
        workflow_id: str,
        agent_name: str,
        task_name: str,
        memory_data: str,
    ):
        db: Session = SessionLocal()

        try:
            memory = AgentMemories(
                workflow_id=workflow_id,
                agent_name=agent_name,
                task_name=task_name,
                memory_data=json.dumps(memory_data),
            )

            db.add(memory)
            db.commit()
            db.refresh(memory)

            return memory

        finally:
            db.close()

    def get_recent(self, agent_name: str, limit: int = 10):
        db: Session = SessionLocal()

        try:
            memories = (
                db.query(AgentMemories)
                .filter(AgentMemories.agent_name == agent_name)
                .order_by(AgentMemories.created_at.desc())
                .limit(limit)
                .all()
            )

            for memory in memories:
                memory.memory_data = json.loads(memory.memory_data)

            return memories

        finally:
            db.close()

    def get_by_workflow(self, workflow_id: str):
        db: Session = SessionLocal()

        try:
            agent_memories = (
                db.query(AgentMemories)
                .filter(AgentMemories.workflow_id == workflow_id)
                .order_by(AgentMemories.created_at)
                .all()
            )

            for agent_memory in agent_memories:
                agent_memories.memory_data = json.loads(agent_memories.memory_data)

            return agent_memories

        finally:
            db.close()


memory_repository = MemoryRepository()
