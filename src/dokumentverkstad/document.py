from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from uuid import uuid4

from .knowledge import utc_now


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    created_at: str
    updated_at: str
    author: str = ""
    year: str = ""
    document_type: str = ""
    language: str = ""
    edition: str = ""
    comment: str = ""
    has_original_file: bool = False
    original_filename: str = ""
    metadata_sources: dict[str, str] | None = None
    checksum_sha256: str = ""
    extracted_text_path: str = ""
    inbox_status: str = "new"
    project_ids: tuple[str, ...] = ()

    @classmethod
    def create(
        cls,
        title: str,
        author: str = "",
        year: str = "",
        document_type: str = "",
        language: str = "",
        edition: str = "",
        comment: str = "",
        has_original_file: bool = False,
        original_filename: str = "",
        checksum_sha256: str = "",
        extracted_text_path: str = "",
        inbox_status: str = "new",
        project_ids: tuple[str, ...] = (),
        metadata_sources: dict[str, str] | None = None,
    ) -> "Document":
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Document title cannot be empty.")
        clean_year = _validate_year(year)

        now = utc_now()
        return cls(
            id=f"doc_{uuid4().hex}",
            title=clean_title,
            author=author.strip(),
            year=clean_year,
            document_type=document_type.strip(),
            language=language.strip(),
            edition=edition.strip(),
            comment=comment.strip(),
            has_original_file=has_original_file,
            original_filename=original_filename.strip(),
            metadata_sources=metadata_sources or {},
            checksum_sha256=checksum_sha256.strip(),
            extracted_text_path=extracted_text_path.strip(),
            inbox_status=inbox_status.strip() or "new",
            project_ids=_unique_project_ids(project_ids),
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Document":
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            author=str(data.get("author", "")),
            year=str(data.get("publication_year", data.get("year", ""))),
            document_type=str(data.get("document_type", "")),
            language=str(data.get("language", "")),
            edition=str(data.get("edition", "")),
            comment=str(data.get("comment", "")),
            has_original_file=bool(data.get("has_original_file", False)),
            original_filename=str(data.get("original_filename", "")),
            metadata_sources=dict(data.get("metadata_sources", {})),
            checksum_sha256=str(data.get("checksum_sha256", "")),
            extracted_text_path=str(data.get("extracted_text_path", "")),
            inbox_status=str(data.get("inbox_status", "new")),
            project_ids=_unique_project_ids(
                str(project_id) for project_id in data.get("project_ids", [])
            ),
            created_at=str(data["created_at"]),
            updated_at=str(data["updated_at"]),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "type": "Document",
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "publication_year": self.year,
            "document_type": self.document_type,
            "language": self.language,
            "edition": self.edition,
            "comment": self.comment,
            "has_original_file": self.has_original_file,
            "original_filename": self.original_filename,
            "metadata_sources": self.metadata_sources or {},
            "checksum_sha256": self.checksum_sha256,
            "extracted_text_path": self.extracted_text_path,
            "inbox_status": self.inbox_status,
            "project_ids": list(self.project_ids),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def revise_metadata(
        self,
        title: str | None = None,
        author: str | None = None,
        year: str | None = None,
        document_type: str | None = None,
        language: str | None = None,
        edition: str | None = None,
        comment: str | None = None,
    ) -> "Document":
        new_title = self.title if title is None else title.strip()
        if not new_title:
            raise ValueError("Document title cannot be empty.")
        new_year = self.year if year is None else _validate_year(year)

        return Document(
            id=self.id,
            title=new_title,
            author=self.author if author is None else author.strip(),
            year=new_year,
            document_type=(
                self.document_type if document_type is None else document_type.strip()
            ),
            language=self.language if language is None else language.strip(),
            edition=self.edition if edition is None else edition.strip(),
            comment=self.comment if comment is None else comment.strip(),
            has_original_file=self.has_original_file,
            original_filename=self.original_filename,
            metadata_sources=_with_manual_metadata_sources(
                self.metadata_sources or {}, title, author, year
            ),
            checksum_sha256=self.checksum_sha256,
            extracted_text_path=self.extracted_text_path,
            inbox_status=self.inbox_status,
            project_ids=self.project_ids,
            created_at=self.created_at,
            updated_at=utc_now(),
        )

    def with_inbox_status(self, inbox_status: str) -> "Document":
        clean_status = inbox_status.strip()
        if clean_status not in {"new", "later", "done", "trashed"}:
            raise ValueError("Unknown document inbox status.")
        return Document(
            id=self.id,
            title=self.title,
            author=self.author,
            year=self.year,
            document_type=self.document_type,
            language=self.language,
            edition=self.edition,
            comment=self.comment,
            has_original_file=self.has_original_file,
            original_filename=self.original_filename,
            metadata_sources=self.metadata_sources,
            checksum_sha256=self.checksum_sha256,
            extracted_text_path=self.extracted_text_path,
            inbox_status=clean_status,
            project_ids=self.project_ids,
            created_at=self.created_at,
            updated_at=utc_now(),
        )

    def with_projects(self, project_ids: tuple[str, ...]) -> "Document":
        return Document(
            id=self.id,
            title=self.title,
            author=self.author,
            year=self.year,
            document_type=self.document_type,
            language=self.language,
            edition=self.edition,
            comment=self.comment,
            has_original_file=self.has_original_file,
            original_filename=self.original_filename,
            metadata_sources=self.metadata_sources,
            checksum_sha256=self.checksum_sha256,
            extracted_text_path=self.extracted_text_path,
            inbox_status=self.inbox_status,
            project_ids=_unique_project_ids(project_ids),
            created_at=self.created_at,
            updated_at=utc_now(),
        )


def _unique_project_ids(project_ids: object) -> tuple[str, ...]:
    unique: list[str] = []
    for project_id in project_ids:
        clean_project_id = str(project_id).strip()
        if clean_project_id and clean_project_id not in unique:
            unique.append(clean_project_id)
    return tuple(unique)


def metadata_from_filename(filename: str) -> dict[str, str]:
    stem = Path(filename).stem.strip()
    match = re.fullmatch(r"(\d{4})\s+(.+)", stem)
    if not match:
        return {}
    year, title = match.groups()
    return {"year": year, "title": title.strip()}


def choose_document_metadata(
    pdf_title: str = "",
    pdf_author: str = "",
    pdf_year: str = "",
    original_filename: str = "",
) -> tuple[str, str, str, dict[str, str]]:
    filename_metadata = metadata_from_filename(original_filename)
    title = ""
    author = ""
    year = ""
    sources: dict[str, str] = {}

    if _is_useful_metadata(pdf_title):
        title = pdf_title.strip()
        sources["title"] = "pdf"
    elif filename_metadata.get("title"):
        title = filename_metadata["title"]
        sources["title"] = "filename"
    elif original_filename:
        title = Path(original_filename).stem
        sources["title"] = "filename_stem"

    if _is_useful_metadata(pdf_author):
        author = pdf_author.strip()
        sources["author"] = "pdf"

    if _is_valid_year(pdf_year):
        year = pdf_year.strip()
        sources["year"] = "pdf"
    elif _is_valid_year(filename_metadata.get("year", "")):
        year = filename_metadata["year"]
        sources["year"] = "filename"

    return title, author, year, sources


def _with_manual_metadata_sources(
    sources: dict[str, str],
    title: str | None,
    author: str | None,
    year: str | None,
) -> dict[str, str]:
    updated = dict(sources)
    if title is not None:
        updated["title"] = "manual"
    if author is not None:
        updated["author"] = "manual"
    if year is not None:
        updated["year"] = "manual"
    return updated


def _is_useful_metadata(value: str) -> bool:
    clean = value.strip()
    if not clean:
        return False
    visible = 0
    suspicious = 0
    for char in clean:
        if char.isspace():
            continue
        visible += 1
        if ord(char) < 32 or ord(char) == 127:
            suspicious += 1
    if visible and suspicious / visible > 0.05:
        return False
    return True


def _validate_year(value: str) -> str:
    clean = value.strip()
    if clean and not _is_valid_year(clean):
        raise ValueError("Publication year must be a four digit year.")
    return clean


def _is_valid_year(value: str) -> bool:
    clean = value.strip()
    if not re.fullmatch(r"\d{4}", clean):
        return False
    return 1000 <= int(clean) <= 2999
