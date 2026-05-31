from datetime import datetime
from typing import Optional, List
import uuid
from app.orchestration.workflows.states import PENDING


class Task:
    def __init__(self, task_name):
        self.task_id: str = str(uuid.uuid4())
        self.task_name: str = task_name
        self.assigned_agent: Optional[str] = None
        self.status: str = PENDING
        self.dependencies: List[str] = []
        self.priority: str = "NORMAL"
        self.created_at = datetime.utcnow()
