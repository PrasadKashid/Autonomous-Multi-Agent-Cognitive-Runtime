from app.orchestration.event_bus.bus import event_bus
from app.orchestration.event_bus.event_types import TASK_CREATED


async def task_created_handler(event):
    print("Event Recieved")
    print(event.payload)


event_bus.subscribe(TASK_CREATED, task_created_handler)
