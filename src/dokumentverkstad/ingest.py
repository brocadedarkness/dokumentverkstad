from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import shutil

from .archive import Archive
from .document import Document
from .pdf import extract_pdf


@dataclass(frozen=True)
class IngestResult:
    document: Document
    created: bool
    source_path: Path


def process_ingest_source(
    archive: Archive, ingest_source: str | Path, runtime_root: str | Path
) -> list[IngestResult]:
    source_root = Path(ingest_source)
    if not source_root.exists():
        return []

    staging_root = Path(runtime_root) / "ingest"
    staging_root.mkdir(parents=True, exist_ok=True)

    results: list[IngestResult] = []
    for pdf_path in sorted(source_root.glob("*.pdf"), key=lambda item: item.name.casefold()):
        staged_path = _stage_pdf(pdf_path, staging_root)
        checksum = calculate_checksum(staged_path)
        existing = archive.find_document_by_checksum(checksum)
        if existing:
            results.append(IngestResult(existing, created=False, source_path=pdf_path))
            continue

        extracted = extract_pdf(staged_path)
        document = archive.register_document_with_original_pdf(
            original_path=staged_path,
            title=extracted.title or pdf_path.stem,
            author=extracted.author,
            text=extracted.text,
            checksum_sha256=checksum,
        )
        results.append(IngestResult(document, created=True, source_path=pdf_path))
    return results


def calculate_checksum(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stage_pdf(pdf_path: Path, staging_root: Path) -> Path:
    staged_path = staging_root / pdf_path.name
    shutil.copy2(pdf_path, staged_path)
    return staged_path
