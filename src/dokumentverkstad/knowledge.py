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
    source_location: str = ""
    review_status: str = ""
    rejection_reason: str = ""
    event: str = "revision"

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "KnowledgeVersion":
        return cls(
            content=str(data["content"]),
            updated_at=str(data["updated_at"]),
            source_location=str(data.get("source_location", "")),
            review_status=str(data.get("review_status", "")),
            rejection_reason=str(data.get("rejection_reason", "")),
            event=str(data.get("event", "revision")),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "content": self.content,
            "updated_at": self.updated_at,
            "source_location": self.source_location,
            "review_status": self.review_status,
            "rejection_reason": self.rejection_reason,
            "event": self.event,
        }


@dataclass(frozen=True)
class KnowledgeObject:
    id: str
    content: str
    creator: str
    created_at: str
    updated_at: str
    document_id: str = ""
    source_location: str = ""
    project_ids: tuple[str, ...] = field(default_factory=tuple)
    semantic_type: str = "unknown"
    review_status: str = "accepted"
    ai_run_id: str = ""
    ai_provider: str = ""
    ai_model: str = ""
    prompt_version: str = ""
    capability: str = ""
    confidence: str = ""
    original_content: str = ""
    accepted_content: str = ""
    rejection_reason: str = ""
    history: tuple[KnowledgeVersion, ...] = field(default_factory=tuple)

    @classmethod
    def create(
        cls,
        content: str,
        creator: str = "user",
        document_id: str = "",
        source_location: str = "",
        project_ids: tuple[str, ...] = (),
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
            project_ids=_clean_project_ids(project_ids),
        )

    @classmethod
    def create_ai_candidate(
        cls,
        content: str,
        ai_run_id: str,
        ai_provider: str,
        ai_model: str,
        prompt_version: str,
        capability: str,
        document_id: str,
        confidence: str = "",
        project_ids: tuple[str, ...] = (),
        semantic_type: str = "unknown",
    ) -> "KnowledgeObject":
        candidate = cls.create(
            content=content,
            creator="ai",
            document_id=document_id,
            project_ids=project_ids,
        )
        return cls(
            id=candidate.id,
            content=candidate.content,
            creator=candidate.creator,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
            document_id=candidate.document_id,
            source_location=candidate.source_location,
            project_ids=candidate.project_ids,
            semantic_type=semantic_type.strip() or "unknown",
            review_status="candidate",
            ai_run_id=ai_run_id.strip(),
            ai_provider=ai_provider.strip(),
            ai_model=ai_model.strip(),
            prompt_version=prompt_version.strip(),
            capability=capability.strip(),
            confidence=confidence.strip(),
            original_content=candidate.content,
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
            project_ids=_clean_project_ids(data.get("project_ids", [])),
            semantic_type=str(data.get("semantic_type", "unknown")),
            review_status=str(data.get("review_status", "accepted")),
            ai_run_id=str(data.get("ai_run_id", "")),
            ai_provider=str(data.get("ai_provider", "")),
            ai_model=str(data.get("ai_model", "")),
            prompt_version=str(data.get("prompt_version", "")),
            capability=str(data.get("capability", "")),
            confidence=str(data.get("confidence", "")),
            original_content=str(data.get("original_content", "")),
            accepted_content=str(data.get("accepted_content", "")),
            rejection_reason=str(data.get("rejection_reason", "")),
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
            "project_ids": list(self.project_ids),
            "semantic_type": self.semantic_type,
            "review_status": self.review_status,
            "ai_run_id": self.ai_run_id,
            "ai_provider": self.ai_provider,
            "ai_model": self.ai_model,
            "prompt_version": self.prompt_version,
            "capability": self.capability,
            "confidence": self.confidence,
            "original_content": self.original_content,
            "accepted_content": self.accepted_content,
            "rejection_reason": self.rejection_reason,
            "history": [version.to_dict() for version in self.history],
        }

    def revise(
        self, content: str, source_location: str | None = None
    ) -> "KnowledgeObject":
        clean_content = content.strip()
        if not clean_content:
            raise ValueError("Knowledge Object content cannot be empty.")
        clean_source_location = (
            self.source_location if source_location is None else source_location.strip()
        )

        previous = self._current_version("manual_edit")
        return KnowledgeObject(
            id=self.id,
            content=clean_content,
            creator=self.creator,
            created_at=self.created_at,
            updated_at=utc_now(),
            document_id=self.document_id,
            source_location=clean_source_location,
            project_ids=self.project_ids,
            semantic_type=self.semantic_type,
            review_status=self.review_status,
            ai_run_id=self.ai_run_id,
            ai_provider=self.ai_provider,
            ai_model=self.ai_model,
            prompt_version=self.prompt_version,
            capability=self.capability,
            confidence=self.confidence,
            original_content=self.original_content,
            accepted_content=self.accepted_content,
            rejection_reason=self.rejection_reason,
            history=(*self.history, previous),
        )

    def with_projects(self, project_ids: tuple[str, ...]) -> "KnowledgeObject":
        return KnowledgeObject(
            id=self.id,
            content=self.content,
            creator=self.creator,
            created_at=self.created_at,
            updated_at=utc_now(),
            document_id=self.document_id,
            source_location=self.source_location,
            project_ids=_clean_project_ids(project_ids),
            semantic_type=self.semantic_type,
            review_status=self.review_status,
            ai_run_id=self.ai_run_id,
            ai_provider=self.ai_provider,
            ai_model=self.ai_model,
            prompt_version=self.prompt_version,
            capability=self.capability,
            confidence=self.confidence,
            original_content=self.original_content,
            accepted_content=self.accepted_content,
            rejection_reason=self.rejection_reason,
            history=self.history,
        )

    def with_review_decision(
        self, review_status: str, content: str | None = None, rejection_reason: str = ""
    ) -> "KnowledgeObject":
        clean_status = review_status.strip()
        if clean_status not in {
            "candidate",
            "accepted",
            "later",
            "rejected",
            "handled",
        }:
            raise ValueError("Unknown Knowledge Object review status.")
        clean_content = self.content if content is None else content.strip()
        if not clean_content:
            raise ValueError("Knowledge Object content cannot be empty.")
        previous = self._current_version("review_decision")
        history = self.history
        if (
            clean_content != self.content
            or clean_status != self.review_status
            or rejection_reason.strip() != self.rejection_reason
        ):
            history = (*history, previous)
        return KnowledgeObject(
            id=self.id,
            content=clean_content,
            creator="user_after_ai" if self.creator == "ai" and clean_status == "accepted" else self.creator,
            created_at=self.created_at,
            updated_at=utc_now(),
            document_id=self.document_id,
            source_location=self.source_location,
            project_ids=self.project_ids,
            semantic_type=self.semantic_type,
            review_status=clean_status,
            ai_run_id=self.ai_run_id,
            ai_provider=self.ai_provider,
            ai_model=self.ai_model,
            prompt_version=self.prompt_version,
            capability=self.capability,
            confidence=self.confidence,
            original_content=self.original_content or self.content,
            accepted_content=clean_content if clean_status == "accepted" else self.accepted_content,
            rejection_reason=rejection_reason.strip() if clean_status == "rejected" else "",
            history=history,
        )

    def _current_version(self, event: str) -> KnowledgeVersion:
        return KnowledgeVersion(
            content=self.content,
            updated_at=self.updated_at,
            source_location=self.source_location,
            review_status=self.review_status,
            rejection_reason=self.rejection_reason,
            event=event,
        )


def _clean_project_ids(project_ids: object) -> tuple[str, ...]:
    if not isinstance(project_ids, (list, tuple)):
        return ()
    clean_ids: list[str] = []
    for project_id in project_ids:
        clean_id = str(project_id).strip()
        if clean_id and clean_id not in clean_ids:
            clean_ids.append(clean_id)
    return tuple(clean_ids)
