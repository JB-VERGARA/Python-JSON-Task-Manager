from dataclasses import dataclass, asdict
from datetime import datetime
from uuid import uuid4


@dataclass
class Task:
    id: str
    title: str
    description: str
    date: str
    time: str
    priority: str
    completed: bool
    created_at: str
    updated_at: str

    @classmethod
    def create(
        cls,
        title: str,
        description: str,
        date: str,
        time: str,
        priority: str,
    ):
        now = datetime.now().astimezone().isoformat()

        return cls(
            id=str(uuid4()),
            title=title,
            description=description,
            date=date,
            time=time,
            priority=priority,
            completed=False,
            created_at=now,
            updated_at=now,
        )

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            date=data["date"],
            time=data.get("time", ""),
            priority=data.get("priority", "medium"),
            completed=data.get("completed", False),
            created_at=data["created_at"],
            updated_at=data["updated_at"],
        )