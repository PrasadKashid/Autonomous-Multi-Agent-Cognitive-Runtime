from app.orchestration.planner.planner import PlannedTask


class TaskPlanner:

    def create_plan(self, request: str):

        if "authentication" in request.lower():

            architecture = PlannedTask(
                task_name="Design Authentication Architecture",
                capability="architecture_design",
            )

            jwt = PlannedTask(
                task_name="Build JWT Service",
                capability="backend_development",
                dependencies=["Design Authentication Architecture"],
            )

            login = PlannedTask(
                task_name="Create Login API",
                capability="api_development",
                dependencies=["Build JWT Service"],
            )

            testing = PlannedTask(
                task_name="Write Authentication Tests",
                capability="testing",
                dependencies=["Create Login API"],
            )

            return [
                architecture,
                jwt,
                login,
                testing,
            ]

        return [
            PlannedTask(
                task_name="Generic Task",
                capability="backend_development",
            )
        ]


task_planner = TaskPlanner()
