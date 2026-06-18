from pydantic import BaseModel


class CreateWorkflowRequest(BaseModel):
    task: str
