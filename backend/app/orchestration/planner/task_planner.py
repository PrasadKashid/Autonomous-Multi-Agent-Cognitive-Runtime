from app.capabilities.planner import planner_capability


class TaskPlanner:
    def create_plan(self, request):
        return planner_capability.execute(request)


task_planner = TaskPlanner()
