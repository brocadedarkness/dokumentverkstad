from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .knowledge import utc_now


@dataclass(frozen=True)
class Relation:
    id: str
    source_id: str
    target_id: str
    relation_type: str
    created_at: str
    comment: str = ""

    @classmethod
    def create(
        cls, source_id: str, target_id: str, comment: str = ""
    ) -> "Relation":
        clean_source = source_id.strip()
        clean_target = target_id.strip()
        if not clean_source or not clean_target:
            raise ValueError("Relation endpoints cannot be empty.")
        if clean_source == clean_target:
            raise ValueError("A Knowledge Object cannot be related to itself.")

        return cls(
            id=f"rel_{uuid4().hex}",
            source_id=clean_source,
            target_id=clean_target,
            relation_type="hör ihop med",
            comment=comment.strip(),
            created_at=utc_now(),
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Relation":
        return cls(
            id=str(data["id"]),
            source_id=str(data["source_id"]),
            target_id=str(data["target_id"]),
            relation_type=str(data.get("relation_type", "hör ihop med")),
            comment=str(data.get("comment", "")),
            created_at=str(data["created_at"]),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "type": "Relation",
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type,
            "comment": self.comment,
            "created_at": self.created_at,
        }
