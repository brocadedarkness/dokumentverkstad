from __future__ import annotations

from dataclasses import dataclass
import os

from .archive import Archive
from .config import AppConfig
from .diagnostics import runtime_log_path
from .index import document_index_path
from .secrets import encrypted_secrets_exists, has_unlocked_openai_api_key, load_openai_api_key


@dataclass(frozen=True)
class HealthCounts:
    documents: int = 0
    knowledge_objects: int = 0
    projects: int = 0
    ai_runs: int = 0
    trash_objects: int = 0


@dataclass(frozen=True)
class HealthResult:
    status: str
    messages: tuple[str, ...]
    counts: HealthCounts
    archive_readable: bool
    runtime_exists: bool
    index_exists: bool
    encrypted_secrets: bool
    credential_status: str
    log_path: str


def check_health(config: AppConfig) -> HealthResult:
    messages: list[tuple[str, str]] = []
    counts = HealthCounts()
    archive_readable = False

    if not config.archive_root.exists():
        messages.append(("error", "Archive saknas. Kör init eller restore."))
    elif not config.archive_root.is_dir():
        messages.append(("error", "Archive-path är inte en katalog."))
    else:
        try:
            archive = Archive(config.archive_root)
            counts = HealthCounts(
                documents=len(archive.list_documents(include_trashed=True)),
                knowledge_objects=len(archive.list_knowledge_objects()),
                projects=len(archive.list_projects()),
                ai_runs=len(archive.list_ai_runs()),
                trash_objects=len(archive.list_trashed_documents()),
            )
            archive_readable = True
        except Exception as error:
            messages.append(
                ("error", f"Archive kunde inte läsas: {error.__class__.__name__}")
            )

    runtime_exists = config.runtime_root.is_dir()
    if not runtime_exists:
        messages.append(("warning", "Runtime saknas men kan återskapas."))

    index_exists = document_index_path(config.runtime_root).is_file()
    if runtime_exists and not index_exists:
        messages.append(("warning", "SQLite-index saknas. Kör rebuild-index."))

    encrypted = encrypted_secrets_exists(config.encrypted_secrets_path)
    credential_status = _credential_status(config, encrypted)
    if encrypted and not has_unlocked_openai_api_key():
        messages.append(("warning", "Krypterade secrets finns men är låsta."))

    if any(level == "error" for level, _ in messages):
        status = "error"
    elif any(level == "warning" for level, _ in messages):
        status = "warning"
    else:
        status = "ok"

    return HealthResult(
        status=status,
        messages=tuple(f"{level}: {message}" for level, message in messages),
        counts=counts,
        archive_readable=archive_readable,
        runtime_exists=runtime_exists,
        index_exists=index_exists,
        encrypted_secrets=encrypted,
        credential_status=credential_status,
        log_path=str(runtime_log_path(config.runtime_root)),
    )


def _credential_status(config: AppConfig, encrypted: bool) -> str:
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return "miljövariabel"
    if encrypted and has_unlocked_openai_api_key():
        return "upplåsta krypterade secrets"
    if encrypted:
        return "krypterade secrets finns (låst)"
    if load_openai_api_key(config.secrets_path):
        return "legacy secrets.toml"
    return "saknas (AI är valfritt)"
