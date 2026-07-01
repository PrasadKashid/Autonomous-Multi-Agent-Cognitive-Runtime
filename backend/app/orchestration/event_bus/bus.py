from collections import defaultdict
from typing import Callable, Dict, List

from app.orchestration.event_bus.base import Event
from app.db.repositories.workflow_event_repository import workflow_event_repository


class EventBus:

    def __init__(self):

        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable):

        self.subscribers[event_type].append(handler)

    async def publish(self, event: Event):

        workflow_id = event.payload.get("workflow_id")

        if workflow_id:
            workflow_event_repository.save(
                workflow_id=workflow_id,
                task_id=event.payload.get("task_id"),
                task_name=event.payload.get("task_name"),
                event_type=event.event_type,
                agent=event.source_agent,
                message=event.message
                or f"{event.event_type} published by {event.source_agent}",
            )

        handlers = self.subscribers.get(event.event_type, [])

        for handler in handlers:
            await handler(event)


event_bus = EventBus()
