from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import uuid

from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.bus import event_bus
from app.memory.memory_manager import memory_manager


class BaseAgent(ABC):
    def __init__(self, agent_name):
        self.agent_id: str = str(uuid.uuid4())
        self.agent_name: str = agent_name

    @abstractmethod
    async def handle_event(self, event: Event):
        pass

    async def publish_event(self, event: Event):
        await event_bus.publish(event)

    def store_memory(
        self,
        workflow_id: str,
        task_name: str,
        memory_data: str,
    ):
        memory = memory_manager.get_memory(self.agent_name)

        memory.store(
            workflow_id=workflow_id,
            task_name=task_name,
            memory_data=memory_data,
        )

    def get_recent_memory(self, limit: int = 10):
        memory = memory_manager.get_memory(self.agent_name)
        return memory.get_recent(limit)
