from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


@dataclass(frozen=True)
class KnowledgeVersion:
    content: str
    updated_at: str

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "KnowledgeVersion":
        return cls(content=str(data["content"]), updated_at=str(data["updated_at"]))

    def to_dict(self) -> dict[str, str]:
        return {"content": self.content, "updated_at": self.updated_at}


@dataclass(frozen=True)
class KnowledgeObject:
    id: str
    content: str
    creator: str
    created_at: str
    updated_at: str
    document_id: str = ""
    source_location: str = ""
    history: tuple[KnowledgeVersion, ...] = field(default_factory=tuple)

    @classmethod
    def create(
        cls,
        content: str,
        creator: str = "user",
        document_id: str = "",
        source_location: str = "",
    ) -> "KnowledgeObject":
        clean_content = content.strip()
        if not clean_content:
            raise ValueError("Knowledge Object content cannot be empty.")

        now = utc_now()
        return cls(
            id=f"ko_{uuid4().hex}",
            content=clean_content,
            creator=creator,
            created_at=now,
            updated_at=now,
            document_id=document_id.strip(),
            source_location=source_location.strip(),
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "KnowledgeObject":
        history = tuple(
            KnowledgeVersion.from_dict(item)
            for item in data.get("history", [])
            if isinstance(item, dict)
        )
        return cls(
            id=str(data["id"]),
            content=str(data["content"]),
            creator=str(data["creator"]),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
            document_id=str(data.get("document_id", "")),
            source_location=str(data.get("source_location", "")),
            history=history,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "type": "KnowledgeObject",
            "content": self.content,
            "creator": self.creator,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "document_id": self.document_id,
            "source_location": self.source_location,
            "history": [version.to_dict() for version in self.history],
        }

    def revise(self, content: str) -> "KnowledgeObject":
        clean_content = content.strip()
        if not clean_content:
            raise ValueError("Knowledge Object content cannot be empty.")

        previous = KnowledgeVersion(content=self.content, updated_at=self.updated_at)
        return KnowledgeObject(
            id=self.id,
            content=clean_content,
            creator=self.creator,
            created_at=self.created_at,
            updated_at=utc_now(),
            document_id=self.document_id,
            source_location=self.source_location,
            history=(*self.history, previous),
        )
