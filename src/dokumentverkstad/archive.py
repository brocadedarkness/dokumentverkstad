from __future__ import annotations

import json
from pathlib import Path

from .document import Document
from .knowledge import KnowledgeObject
from .project import Project
from .relation import Relation


class Archive:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.documents_root = self.root / "documents"
        self.knowledge_root = self.root / "knowledge"
        self.projects_root = self.root / "projects"
        self.relations_root = self.root / "relations"

    def initialize(self) -> None:
        self.documents_root.mkdir(parents=True, exist_ok=True)
        self.knowledge_root.mkdir(parents=True, exist_ok=True)
        self.projects_root.mkdir(parents=True, exist_ok=True)
        self.relations_root.mkdir(parents=True, exist_ok=True)

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
        project_ids: tuple[str, ...] = (),
    ) -> KnowledgeObject:
        knowledge_object = KnowledgeObject.create(
            content=content,
            creator=creator,
            document_id=document_id,
            source_location=source_location,
            project_ids=project_ids,
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

    def create_project(self, name: str, description: str = "") -> Project:
        project = Project.create(name=name, description=description)
        self.save_project(project)
        return project

    def save_project(self, project: Project) -> None:
        self.initialize()
        path = self._project_path(project.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(project.to_dict(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    def get_project(self, project_id: str) -> Project:
        path = self._project_path(project_id)
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return Project.from_dict(data)

    def update_project(
        self, project_id: str, name: str | None = None, description: str | None = None
    ) -> Project:
        project = self.get_project(project_id)
        revised = project.revise(name=name, description=description)
        self.save_project(revised)
        return revised

    def list_projects(self) -> list[Project]:
        self.initialize()
        projects = [
            self.get_project(path.parent.name)
            for path in self.projects_root.glob("*/metadata.json")
        ]
        projects.sort(key=lambda item: item.name.casefold())
        return projects

    def set_knowledge_object_projects(
        self, object_id: str, project_ids: tuple[str, ...]
    ) -> KnowledgeObject:
        knowledge_object = self.get_knowledge_object(object_id)
        updated = knowledge_object.with_projects(project_ids)
        self.save_knowledge_object(updated)
        return updated

    def add_knowledge_object_to_project(
        self, object_id: str, project_id: str
    ) -> KnowledgeObject:
        knowledge_object = self.get_knowledge_object(object_id)
        project_ids = (*knowledge_object.project_ids, project_id)
        return self.set_knowledge_object_projects(object_id, project_ids)

    def list_knowledge_objects_for_project(
        self, project_id: str
    ) -> list[KnowledgeObject]:
        objects = [
            item
            for item in self.list_recent_knowledge_objects(limit=10_000)
            if project_id in item.project_ids
        ]
        objects.sort(key=lambda item: item.created_at, reverse=True)
        return objects

    def list_documents_for_project(self, project_id: str) -> list[Document]:
        document_ids: list[str] = []
        for knowledge_object in self.list_knowledge_objects_for_project(project_id):
            if knowledge_object.document_id and knowledge_object.document_id not in document_ids:
                document_ids.append(knowledge_object.document_id)
        documents = [self.get_document(document_id) for document_id in document_ids]
        documents.sort(key=lambda item: item.title.casefold())
        return documents

    def create_relation(
        self, source_id: str, target_id: str, comment: str = ""
    ) -> Relation:
        self.get_knowledge_object(source_id)
        self.get_knowledge_object(target_id)
        relation = Relation.create(
            source_id=source_id, target_id=target_id, comment=comment
        )
        self.save_relation(relation)
        return relation

    def save_relation(self, relation: Relation) -> None:
        self.initialize()
        path = self._relation_path(relation.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(relation.to_dict(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    def get_relation(self, relation_id: str) -> Relation:
        path = self._relation_path(relation_id)
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return Relation.from_dict(data)

    def _document_path(self, document_id: str) -> Path:
        return self.documents_root / document_id / "metadata.json"

    def _knowledge_path(self, object_id: str) -> Path:
        return self.knowledge_root / object_id / "object.json"

    def _project_path(self, project_id: str) -> Path:
        return self.projects_root / project_id / "metadata.json"

    def _relation_path(self, relation_id: str) -> Path:
        return self.relations_root / relation_id / "relation.json"
