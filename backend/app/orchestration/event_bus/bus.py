from collections import defaultdict, deque
from typing import Callable, Dict, List

from app.orchestration.event_bus.base import Event
from app.db.repositories.workflow_event_repository import workflow_event_repository


class EventBus:

    def __init__(self):

        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)

        # FIFO event queue
        self.queue = deque()

        # Prevent recursive processing
        self.processing = False

    def subscribe(self, event_type: str, handler: Callable):

        self.subscribers[event_type].append(handler)

    async def publish(self, event: Event):

        # Add event to queue
        self.queue.append(event)

        # If another publish() is already processing,
        # just enqueue and return.
        if self.processing:
            return

        self.processing = True

        try:

            while self.queue:

                current_event = self.queue.popleft()

                workflow_id = current_event.payload.get("workflow_id")

                if workflow_id:
                    workflow_event_repository.save(
                        workflow_id=workflow_id,
                        task_id=current_event.payload.get("task_id"),
                        task_name=current_event.payload.get("task_name"),
                        event_type=current_event.event_type,
                        agent=current_event.source_agent,
                        message=current_event.message
                        or f"{current_event.event_type} published by {current_event.source_agent}",
                    )

                handlers = self.subscribers.get(current_event.event_type, [])

                for handler in handlers:
                    await handler(current_event)
        finally:
            self.processing = False


event_bus = EventBus()
