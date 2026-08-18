from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import tempfile
from uuid import uuid4
from zipfile import BadZipFile, ZipFile, ZIP_DEFLATED

from . import __version__
from .archive import Archive
from .config import AppConfig, ConfigurationError
from .index import rebuild_document_index


BACKUP_FORMAT_VERSION = "1"
MANIFEST_PATH = "backup-manifest.json"
PORTABLE_CONFIG_PATH = "config/portable.json"
ARCHIVE_PREFIX = "archive/"
EXCLUDED_TOP_LEVEL_ARCHIVE_NAMES = {
    "runtime",
    "ingest",
    "staging",
    "secrets.enc",
    "secrets.toml",
}


class BackupError(Exception):
    pass


@dataclass(frozen=True)
class ArchiveCounts:
    documents: int
    knowledge_objects: int
    projects: int
    ai_runs: int


@dataclass(frozen=True)
class BackupResult:
    path: Path
    counts: ArchiveCounts
    size_bytes: int


@dataclass(frozen=True)
class RestoreResult:
    archive_root: Path
    counts: ArchiveCounts
    index_path: Path
    portable_config: dict[str, object]


def create_backup(config: AppConfig, output_dir: str | Path | None = None) -> BackupResult:
    archive = Archive(config.archive_root)
    archive.initialize()
    archive_root = config.archive_root.resolve()
    counts = count_archive_objects(archive)
    destination_dir = Path(output_dir) if output_dir else Path.cwd()
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = _unique_backup_path(destination_dir)

    with tempfile.NamedTemporaryFile(
        prefix=f".{destination.stem}.",
        suffix=".tmp",
        dir=destination_dir,
        delete=False,
    ) as handle:
        temp_path = Path(handle.name)

    try:
        with ZipFile(temp_path, "w", compression=ZIP_DEFLATED) as backup:
            manifest = _manifest(created_at=_timestamp(), counts=counts)
            backup.writestr(MANIFEST_PATH, _json_bytes(manifest))
            backup.writestr(PORTABLE_CONFIG_PATH, _json_bytes(_portable_config(config)))
            for path in _archive_files(archive_root):
                relative = path.relative_to(archive_root).as_posix()
                backup.write(path, f"{ARCHIVE_PREFIX}{relative}")
        verify_backup(temp_path)
        os.replace(temp_path, destination)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise

    return BackupResult(
        path=destination.resolve(),
        counts=counts,
        size_bytes=destination.stat().st_size,
    )


def restore_backup(
    backup_path: str | Path,
    config: AppConfig,
    force: bool = False,
) -> RestoreResult:
    source = Path(backup_path).expanduser().resolve()
    manifest, portable_config = validate_backup(source)
    counts = _counts_from_manifest(manifest)
    archive_root = config.archive_root

    if _archive_has_user_data(archive_root) and not force:
        raise BackupError(
            "Archive innehåller redan data. Avbryt eller kör restore med --force."
        )

    archive_root.parent.mkdir(parents=True, exist_ok=True)
    temp_root = archive_root.parent / f"restore-{uuid4().hex}"
    try:
        temp_root.mkdir()
        staging = temp_root / "archive"
        staging.mkdir()
        _extract_archive_to_staging(source, staging)
        Archive(staging).initialize()
        _verify_restored_archive(staging)

        if force and archive_root.exists():
            shutil.rmtree(archive_root)
        elif archive_root.exists():
            _remove_empty_archive_tree(archive_root)
        shutil.copytree(staging, archive_root)
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)

    restored_archive = Archive(archive_root)
    restored_archive.initialize()
    _verify_restored_archive(archive_root)
    index_path = rebuild_document_index(restored_archive, config.runtime_root)
    return RestoreResult(
        archive_root=archive_root,
        counts=counts,
        index_path=index_path,
        portable_config=portable_config,
    )


def validate_backup(backup_path: str | Path) -> tuple[dict[str, object], dict[str, object]]:
    path = Path(backup_path)
    try:
        with ZipFile(path, "r") as backup:
            broken_member = backup.testzip()
            if broken_member:
                raise BackupError(f"Backupen är trasig vid filen: {broken_member}")
            names = backup.namelist()
            _validate_member_names(names)
            if MANIFEST_PATH not in names:
                raise BackupError("Backupmanifest saknas.")
            if not any(name.startswith(ARCHIVE_PREFIX) for name in names):
                raise BackupError("Archive-root saknas i backupen.")
            manifest = json.loads(backup.read(MANIFEST_PATH).decode("utf-8"))
            if manifest.get("backup_format_version") != BACKUP_FORMAT_VERSION:
                raise BackupError("Backupformatet stöds inte.")
            portable_config = {}
            if PORTABLE_CONFIG_PATH in names:
                portable_config = json.loads(
                    backup.read(PORTABLE_CONFIG_PATH).decode("utf-8")
                )
    except BadZipFile as error:
        raise BackupError("Backupfilen är inte ett giltigt zip-arkiv.") from error
    except OSError as error:
        raise BackupError(f"Kunde inte läsa backupfilen: {path}") from error
    except json.JSONDecodeError as error:
        raise BackupError("Backupmanifestet är inte giltig JSON.") from error
    if not isinstance(manifest, dict):
        raise BackupError("Backupmanifestet har fel struktur.")
    if not isinstance(portable_config, dict):
        raise BackupError("Portabel backupkonfiguration har fel struktur.")
    return manifest, portable_config


def verify_backup(backup_path: str | Path) -> None:
    validate_backup(backup_path)


def count_archive_objects(archive: Archive) -> ArchiveCounts:
    return ArchiveCounts(
        documents=len(archive.list_documents(include_trashed=True)),
        knowledge_objects=len(archive.list_knowledge_objects()),
        projects=len(archive.list_projects()),
        ai_runs=len(archive.list_ai_runs()),
    )


def _archive_files(archive_root: Path) -> list[Path]:
    root = archive_root.resolve()
    files: list[Path] = []
    for path in root.rglob("*"):
        relative_parts = path.relative_to(root).parts
        if not relative_parts:
            continue
        if relative_parts[0] in EXCLUDED_TOP_LEVEL_ARCHIVE_NAMES:
            continue
        if path.is_file():
            files.append(path)
    files.sort(key=lambda item: item.relative_to(root).as_posix())
    return files


def _unique_backup_path(destination_dir: Path) -> Path:
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    base = destination_dir / f"dokumentverkstad-backup-{stamp}.zip"
    if not base.exists():
        return base
    for index in range(1, 1000):
        candidate = destination_dir / f"dokumentverkstad-backup-{stamp}-{index}.zip"
        if not candidate.exists():
            return candidate
    raise BackupError("Kunde inte välja ett unikt backupfilnamn.")


def _manifest(created_at: str, counts: ArchiveCounts) -> dict[str, object]:
    return {
        "backup_format_version": BACKUP_FORMAT_VERSION,
        "created_at": created_at,
        "application_version": __version__,
        "archive_path": ARCHIVE_PREFIX.rstrip("/"),
        "counts": {
            "documents": counts.documents,
            "knowledge_objects": counts.knowledge_objects,
            "projects": counts.projects,
            "ai_runs": counts.ai_runs,
        },
    }


def _portable_config(config: AppConfig) -> dict[str, object]:
    return {
        "ai_provider": config.ai_provider,
        "ai_model": config.ai_model,
        "ai_max_output_tokens": config.ai_max_output_tokens,
        "ai_output_language": config.ai_output_language,
        "ai_currency": config.ai_currency,
        "ai_cost_limit": config.ai_cost_limit,
    }


def _timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _json_bytes(data: dict[str, object]) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _validate_member_names(names: list[str]) -> None:
    for name in names:
        normalized = name.replace("\\", "/")
        path = PurePosixPath(normalized)
        has_windows_drive = bool(path.parts and path.parts[0].endswith(":"))
        if normalized != name or path.is_absolute() or has_windows_drive or ".." in path.parts:
            raise BackupError(f"Backupen innehåller osäker sökväg: {name}")
        if len(path.parts) >= 2 and path.parts[0] == ARCHIVE_PREFIX.rstrip("/"):
            if path.parts[1] in EXCLUDED_TOP_LEVEL_ARCHIVE_NAMES:
                raise BackupError(f"Backupen innehåller exkluderad fil: {name}")


def _extract_archive_to_staging(backup_path: Path, staging: Path) -> None:
    staging_root = staging.resolve()
    with ZipFile(backup_path, "r") as backup:
        for member in backup.infolist():
            name = member.filename
            if not name.startswith(ARCHIVE_PREFIX) or name.endswith("/"):
                continue
            relative_name = name[len(ARCHIVE_PREFIX) :]
            destination = (staging / PurePosixPath(relative_name)).resolve()
            if not _is_relative_to(destination, staging_root):
                raise BackupError(f"Backupen innehåller osäker sökväg: {name}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with backup.open(member, "r") as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)


def _verify_restored_archive(archive_root: Path) -> None:
    archive = Archive(archive_root)
    try:
        archive.list_documents(include_trashed=True)
        archive.list_knowledge_objects()
        archive.list_projects()
        archive.list_ai_runs()
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        raise BackupError("Det återställda Archive kunde inte läsas.") from error


def _archive_has_user_data(archive_root: Path) -> bool:
    if not archive_root.exists():
        return False
    if archive_root.is_file():
        raise ConfigurationError("archive_root är en fil, inte en katalog.")
    return any(path.is_file() for path in archive_root.rglob("*"))


def _remove_empty_archive_tree(archive_root: Path) -> None:
    if not archive_root.exists():
        return
    if _archive_has_user_data(archive_root):
        raise BackupError("Archive innehåller data och kan inte ersättas utan --force.")
    shutil.rmtree(archive_root)


def _counts_from_manifest(manifest: dict[str, object]) -> ArchiveCounts:
    counts = manifest.get("counts", {})
    if not isinstance(counts, dict):
        return ArchiveCounts(0, 0, 0, 0)
    return ArchiveCounts(
        documents=int(counts.get("documents", 0)),
        knowledge_objects=int(counts.get("knowledge_objects", 0)),
        projects=int(counts.get("projects", 0)),
        ai_runs=int(counts.get("ai_runs", 0)),
    )


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
