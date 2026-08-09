from __future__ import annotations

from pathlib import Path
import sqlite3

from .archive import Archive
from .document import Document


def rebuild_document_index(archive: Archive, runtime_root: str | Path) -> Path:
    database_path = document_index_path(runtime_root)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    try:
        connection.execute("DROP TABLE IF EXISTS documents")
        connection.execute(
            """
            CREATE TABLE documents (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year TEXT NOT NULL,
                document_type TEXT NOT NULL,
                has_original_file INTEGER NOT NULL,
                original_filename TEXT NOT NULL,
                checksum_sha256 TEXT NOT NULL
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO documents (
                id,
                title,
                author,
                year,
                document_type,
                has_original_file,
                original_filename,
                checksum_sha256
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [_document_row(document) for document in archive.list_documents()],
        )
        connection.commit()
    finally:
        connection.close()
    return database_path


def list_indexed_documents(runtime_root: str | Path) -> list[dict[str, object]]:
    database_path = document_index_path(runtime_root)
    if not database_path.exists():
        return []

    connection = sqlite3.connect(database_path)
    try:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT * FROM documents ORDER BY title COLLATE NOCASE"
        ).fetchall()
    finally:
        connection.close()
    return [dict(row) for row in rows]


def document_index_path(runtime_root: str | Path) -> Path:
    return Path(runtime_root) / "sqlite" / "documents.sqlite3"


def _document_row(document: Document) -> tuple[object, ...]:
    return (
        document.id,
        document.title,
        document.author,
        document.year,
        document.document_type,
        1 if document.has_original_file else 0,
        document.original_filename,
        document.checksum_sha256,
    )
