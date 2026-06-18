class ArchitectureCapability:

    def execute(
        self,
        task_name,
        dependency_outputs,
        workflow_context,
    ):

        return {
            "architecture_type": "JWT Authentication",
            "components": [
                "Auth API",
                "JWT Service",
                "User Repository",
            ],
        }
