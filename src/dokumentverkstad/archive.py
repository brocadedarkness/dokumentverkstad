from __future__ import annotations

import json
from pathlib import Path

from .knowledge import KnowledgeObject


class Archive:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.knowledge_root = self.root / "knowledge"

    def initialize(self) -> None:
        self.knowledge_root.mkdir(parents=True, exist_ok=True)

    def create_knowledge_object(
        self, content: str, creator: str = "user"
    ) -> KnowledgeObject:
        knowledge_object = KnowledgeObject.create(content=content, creator=creator)
        self.save_knowledge_object(knowledge_object)
        return knowledge_object

    def save_knowledge_object(self, knowledge_object: KnowledgeObject) -> None:
        self.initialize()
        path = self._knowledge_path(knowledge_object.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(knowledge_object.to_dict(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    def get_knowledge_object(self, object_id: str) -> KnowledgeObject:
        path = self._knowledge_path(object_id)
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return KnowledgeObject.from_dict(data)

    def update_knowledge_object(self, object_id: str, content: str) -> KnowledgeObject:
        knowledge_object = self.get_knowledge_object(object_id)
        revised = knowledge_object.revise(content)
        self.save_knowledge_object(revised)
        return revised

    def list_recent_knowledge_objects(self, limit: int = 10) -> list[KnowledgeObject]:
        self.initialize()
        objects = [
            self.get_knowledge_object(path.parent.name)
            for path in self.knowledge_root.glob("*/object.json")
        ]
        objects.sort(key=lambda item: item.created_at, reverse=True)
        return objects[:limit]

    def _knowledge_path(self, object_id: str) -> Path:
        return self.knowledge_root / object_id / "object.json"
