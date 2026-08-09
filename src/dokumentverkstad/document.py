from __future__ import annotations

from dataclasses import dataclass
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
    checksum_sha256: str = ""
    extracted_text_path: str = ""

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
    ) -> "Document":
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Document title cannot be empty.")

        now = utc_now()
        return cls(
            id=f"doc_{uuid4().hex}",
            title=clean_title,
            author=author.strip(),
            year=year.strip(),
            document_type=document_type.strip(),
            language=language.strip(),
            edition=edition.strip(),
            comment=comment.strip(),
            has_original_file=has_original_file,
            original_filename=original_filename.strip(),
            checksum_sha256=checksum_sha256.strip(),
            extracted_text_path=extracted_text_path.strip(),
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Document":
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            author=str(data.get("author", "")),
            year=str(data.get("year", "")),
            document_type=str(data.get("document_type", "")),
            language=str(data.get("language", "")),
            edition=str(data.get("edition", "")),
            comment=str(data.get("comment", "")),
            has_original_file=bool(data.get("has_original_file", False)),
            original_filename=str(data.get("original_filename", "")),
            checksum_sha256=str(data.get("checksum_sha256", "")),
            extracted_text_path=str(data.get("extracted_text_path", "")),
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
            "document_type": self.document_type,
            "language": self.language,
            "edition": self.edition,
            "comment": self.comment,
            "has_original_file": self.has_original_file,
            "original_filename": self.original_filename,
            "checksum_sha256": self.checksum_sha256,
            "extracted_text_path": self.extracted_text_path,
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

        return Document(
            id=self.id,
            title=new_title,
            author=self.author if author is None else author.strip(),
            year=self.year if year is None else year.strip(),
            document_type=(
                self.document_type if document_type is None else document_type.strip()
            ),
            language=self.language if language is None else language.strip(),
            edition=self.edition if edition is None else edition.strip(),
            comment=self.comment if comment is None else comment.strip(),
            has_original_file=self.has_original_file,
            original_filename=self.original_filename,
            checksum_sha256=self.checksum_sha256,
            extracted_text_path=self.extracted_text_path,
            created_at=self.created_at,
            updated_at=utc_now(),
        )
