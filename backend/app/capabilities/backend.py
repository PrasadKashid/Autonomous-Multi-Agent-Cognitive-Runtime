class BackendCapability:

    def execute(
        self,
        task_name,
        dependency_outputs,
        workflow_context,
    ):

        if "JWT" in task_name:

            return {
                "service_name": "JWT Service",
                "algorithm": "HS256",
                "expiry": "15m",
            }

        if "Login API" in task_name:

            return {
                "endpoint": "/auth/login",
                "method": "POST",
            }

        return {"message": "Backend Feature Implemented"}
