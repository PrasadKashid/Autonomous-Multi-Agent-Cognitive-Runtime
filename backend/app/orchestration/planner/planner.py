from dataclasses import dataclass, field


@dataclass
class PlannedTask:
    task_name: str
    capability: str
    dependencies: list[str] = field(default_factory=list)
