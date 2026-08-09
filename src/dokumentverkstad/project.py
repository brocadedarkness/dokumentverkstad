from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .knowledge import utc_now


@dataclass(frozen=True)
class Project:
    id: str
    name: str
    description: str
    created_at: str
    updated_at: str

    @classmethod
    def create(cls, name: str, description: str = "") -> "Project":
        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Project name cannot be empty.")

        now = utc_now()
        return cls(
            id=f"proj_{uuid4().hex}",
            name=clean_name,
            description=description.strip(),
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Project":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            description=str(data.get("description", "")),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "type": "Project",
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def revise(self, name: str | None = None, description: str | None = None) -> "Project":
        new_name = self.name if name is None else name.strip()
        if not new_name:
            raise ValueError("Project name cannot be empty.")

        return Project(
            id=self.id,
            name=new_name,
            description=self.description if description is None else description.strip(),
            created_at=self.created_at,
            updated_at=utc_now(),
        )
