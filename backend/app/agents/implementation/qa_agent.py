from app.agents.base.base_agent import BaseAgent
from app.orchestration.event_bus.base import Event
from app.orchestration.event_bus.event_types import (
    TASK_ASSIGNED,
    TASK_COMPLETED,
)

from app.capabilities.testing import TestingCapability
from app.prompting.prompt_builder import prompt_builder


class QAAgent(BaseAgent):

    def __init__(self):
        super().__init__("QA_AGENT")
        self.capability = TestingCapability()

    async def handle_event(self, event: Event):

        if event.event_type != TASK_ASSIGNED:
            return

        if event.payload["assigned_agent"] != self.agent_name:
            return

        print(f"\n[{self.agent_name}] Received Task : {event.event_type}")

        task_id = event.payload["task_id"]
        task_name = event.payload["task_name"]
        workflow_id = event.payload["workflow_id"]

        dependency_outputs = event.payload.get(
            "dependency_outputs",
            {},
        )

        workflow_context = event.payload.get(
            "workflow_context",
            {},
        )

        print("\nDependency Output")
        print(dependency_outputs)

        print("\nWorkflow Context")
        print(workflow_context)

        print(f"\n[{self.agent_name}] Task belongs to me")
        print(f"Workflow ID : {workflow_id}")
        print(f"Task ID : {task_id}")
        print(f"Task Name : {task_name}")

        # Retrieve relevant memories
        retrieved_memories = self.search_memory(task_name)

        print("\n===== Retrieved Memories =====")

        for memory in retrieved_memories:
            print(memory)

        # Execute capability (later this will call an LLM)
        result = self.capability.execute(
            task_name=task_name,
            dependency_outputs=dependency_outputs,
            workflow_context=workflow_context,
            memories=retrieved_memories,
        )

        # Store memory
        self.store_memory(
            workflow_id=workflow_id,
            task_name=task_name,
            memory_data=result,
        )

        print("\nQA Agent Memory")
        print(self.get_recent_memory())

        completed_event = Event(
            event_type=TASK_COMPLETED,
            source_agent=self.agent_name,
            correlation_id=event.correlation_id,
            payload={
                "workflow_id": workflow_id,
                "task_id": task_id,
                "status": "COMPLETED",
                "result": result,
                "task_name": task_name,
            },
        )

        await self.publish_event(completed_event)
