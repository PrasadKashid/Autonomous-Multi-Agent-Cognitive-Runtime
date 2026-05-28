from collections import defaultdict
from typing import Callable, Dict, List

from app.orchestration.event_bus.base import Event


class EventBus:

    def __init__(self):

        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable):

        self.subscribers[event_type].append(handler)

    async def publish(self, event: Event):

        handlers = self.subscribers.get(event.event_type, [])

        for handler in handlers:
            await handler(event)


event_bus = EventBus()
