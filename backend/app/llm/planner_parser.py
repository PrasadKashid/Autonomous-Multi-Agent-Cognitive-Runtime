import json

from app.orchestration.planner.planner import PlannedTask


class PlannerParser:

    def parse(self, llm_output):
        if isinstance(llm_output, str):
            data = json.loads(llm_output)
        else:
            data = llm_output

        tasks = []

        for task in data:
            tasks.append(
                PlannedTask(
                    task_name=task["task_name"],
                    capability=task["capability"],
                    dependencies=task.get("dependencies", []),
                )
            )
        return tasks


planner_parser = PlannerParser()
