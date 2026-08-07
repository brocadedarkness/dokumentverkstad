from __future__ import annotations

import json
from pathlib import Path

from .document import Document
from .knowledge import KnowledgeObject


class Archive:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.documents_root = self.root / "documents"
        self.knowledge_root = self.root / "knowledge"

    def initialize(self) -> None:
        self.documents_root.mkdir(parents=True, exist_ok=True)
        self.knowledge_root.mkdir(parents=True, exist_ok=True)

    def create_document(
        self,
        title: str,
        author: str = "",
        year: str = "",
        document_type: str = "",
        language: str = "",
        edition: str = "",
        comment: str = "",
    ) -> Document:
        document = Document.create(
            title=title,
            author=author,
            year=year,
            document_type=document_type,
            language=language,
            edition=edition,
            comment=comment,
        )
        self.save_document(document)
        return document

    def save_document(self, document: Document) -> None:
        self.initialize()
        path = self._document_path(document.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(document.to_dict(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    def get_document(self, document_id: str) -> Document:
        path = self._document_path(document_id)
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return Document.from_dict(data)

    def update_document(
        self,
        document_id: str,
        title: str | None = None,
        author: str | None = None,
        year: str | None = None,
        document_type: str | None = None,
        language: str | None = None,
        edition: str | None = None,
        comment: str | None = None,
    ) -> Document:
        document = self.get_document(document_id)
        revised = document.revise_metadata(
            title=title,
            author=author,
            year=year,
            document_type=document_type,
            language=language,
            edition=edition,
            comment=comment,
        )
        self.save_document(revised)
        return revised

    def list_documents(self) -> list[Document]:
        self.initialize()
        documents = [
            self.get_document(path.parent.name)
            for path in self.documents_root.glob("*/metadata.json")
        ]
        documents.sort(key=lambda item: item.title.casefold())
        return documents

    def create_knowledge_object(
        self,
        content: str,
        creator: str = "user",
        document_id: str = "",
        source_location: str = "",
    ) -> KnowledgeObject:
        knowledge_object = KnowledgeObject.create(
            content=content,
            creator=creator,
            document_id=document_id,
            source_location=source_location,
        )
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

    def list_knowledge_objects_for_document(
        self, document_id: str
    ) -> list[KnowledgeObject]:
        objects = [
            item
            for item in self.list_recent_knowledge_objects(limit=10_000)
            if item.document_id == document_id
        ]
        objects.sort(key=lambda item: item.created_at, reverse=True)
        return objects

    def _document_path(self, document_id: str) -> Path:
        return self.documents_root / document_id / "metadata.json"

    def _knowledge_path(self, object_id: str) -> Path:
        return self.knowledge_root / object_id / "object.json"
