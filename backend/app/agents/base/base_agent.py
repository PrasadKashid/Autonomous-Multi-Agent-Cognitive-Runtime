from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import uuid

from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.bus import event_bus


class BaseAgent(ABC):
    def __init__(self, agent_name):
        self.agent_id: str = str(uuid.uuid4())
        self.agent_name: str = agent_name

    @abstractmethod
    async def handle_event(self, event: Event):
        pass

    async def publish_event(self, event: Event):
        await event_bus.publish(event)
