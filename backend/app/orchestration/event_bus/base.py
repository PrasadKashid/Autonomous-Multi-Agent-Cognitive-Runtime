from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


class Event(BaseModel):

    id: str = str(uuid.uuid4())

    event_type: str

    source_agent: str

    target_agent: Optional[str] = None

    timestamp: datetime = datetime.utcnow()

    correlation_id: str

    payload: Dict[str, Any]
