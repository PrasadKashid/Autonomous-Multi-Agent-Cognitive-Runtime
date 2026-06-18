from datetime import datetime
from typing import List, Dict
import uuid
from app.orchestration.workflows.states import PENDING


class WorkFlow:
    def __init__(self, workflow_name: str, correlation_id: str):
        self.workflow_id = str(uuid.uuid4())
        self.workflow_name = workflow_name
        self.correlation_id = correlation_id
        self.status = PENDING
        self.created_at = datetime.utcnow()
        self.tasks: List[str] = []
        self.progress = 0
        # self.context: Dict = {}
