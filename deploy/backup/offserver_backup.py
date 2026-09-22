"""Deployment adapter: existing Archive ZIP -> rclone -> read-back restore check.

Scheduling and freezing/thawing writers belong to the accompanying systemd unit.
No remote deletion, sync, provider SDK, or Archive format changes.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from uuid import uuid4

from dokumentverkstad.backup import BackupError, create_backup, restore_backup
from dokumentverkstad.config import AppConfig, load_config


def log(message: str) -> None:
    print(message, flush=True)


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def preflight(config: AppConfig, spool: Path, remote: str, rclone_config: Path) -> None:
    # Require a named rclone remote, not a local directory or inline credentials.
    if not re.fullmatch(r"[A-Za-z0-9_-]+:[^\r\n]+", remote):
        raise BackupError("DOKUMENTVERKSTAD_BACKUP_REMOTE must be a named remote:path")
    if not rclone_config.is_file() or not shutil.which("rclone"):
        raise BackupError("rclone executable or protected configuration is missing")
    if not config.archive_root.is_dir():
        raise BackupError("Configured Archive does not exist")
    roots = [config.archive_root.resolve(), config.runtime_root.resolve(),
             config.ingest_source.resolve(), spool.resolve()]
    for index, first in enumerate(roots):
        for second in roots[index + 1:]:
            if first.is_relative_to(second) or second.is_relative_to(first):
                raise BackupError("Archive, Runtime, ingest and backup spool must be separate")
    for path in (config.secrets_path, config.encrypted_secrets_path, rclone_config):
        if path.resolve().is_relative_to(roots[0]):
            raise BackupError("Secrets must be outside Archive")
    # Archive symlinks could include external secrets or mutable runtime data.
    if any(path.is_symlink() for path in config.archive_root.rglob("*")):
        raise BackupError("Archive contains symlinks; inspect before backing up")
    spool.mkdir(parents=True, exist_ok=True)


def snapshot(config: AppConfig, spool: Path) -> None:
    generation = uuid4().hex
    directory = spool / generation
    directory.mkdir()
    log(f"snapshot started generation={generation}")
    result = create_backup(config, output_dir=directory)
    write_json(spool / "pending.json", {"generation": generation, "file": result.path.name})
    log(f"snapshot completed generation={generation} bytes={result.size_bytes}")


def copy(source: str, destination: str, rclone_config: Path) -> None:
    # Do not echo endpoints or provider output: either may contain private details.
    result = subprocess.run(
        ["rclone", "--config", str(rclone_config), "copyto", source, destination,
         "--immutable", "--retries", "3", "--contimeout", "30s", "--timeout", "5m"],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=3600,
    )
    if result.returncode:
        raise BackupError(f"rclone copyto failed exit={result.returncode}; check remote access/quota/config")


def upload(config: AppConfig, spool: Path, remote: str, rclone_config: Path) -> None:
    pending = json.loads((spool / "pending.json").read_text(encoding="utf-8"))
    generation, filename = pending["generation"], pending["file"]
    if not re.fullmatch(r"[0-9a-f]{32}", generation) or not re.fullmatch(
        r"dokumentverkstad-backup-[0-9TZ-]+\.zip", filename
    ):
        raise BackupError("Invalid pending backup path")
    directory = spool / generation
    local = directory / filename
    target = f"{remote.rstrip('/')}/{generation}/{filename}"
    expected = digest(local)
    log(f"upload started generation={generation}")
    copy(str(local), target, rclone_config)
    log(f"readback started generation={generation}")
    with tempfile.TemporaryDirectory(prefix="readback-", dir=spool) as temporary:
        root = Path(temporary)
        downloaded = root / "backup.zip"
        copy(target, str(downloaded), rclone_config)
        if digest(downloaded) != expected:
            raise BackupError("Remote read-back SHA-256 mismatch; generation is not verified")
        # Use the real restore path, including record loading and SQLite rebuild.
        restored = restore_backup(downloaded, replace(
            config, archive_root=root / "archive", runtime_root=root / "runtime",
            ingest_source=root / "ingest",
        ))
        log(f"restore check completed generation={generation} documents={restored.counts.documents}")
    receipt = {"generation": generation, "file": filename, "sha256": expected,
               "verified_at": datetime.now(UTC).isoformat()}
    marker = directory / "verified.json"
    write_json(marker, receipt)
    log(f"verification marker upload started generation={generation}")
    copy(str(marker), f"{remote.rstrip('/')}/{generation}/verified.json", rclone_config)
    write_json(spool / "last-success.json", receipt)
    # Only this successful local generation is removed. Never delete remote generations.
    (spool / "pending.json").unlink()
    shutil.rmtree(directory)
    log(f"backup verified generation={generation} sha256={expected}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("preflight", "snapshot", "upload"))
    parser.add_argument("--config", required=True)
    parser.add_argument("--spool", required=True, type=Path)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        remote = os.environ.get("DOKUMENTVERKSTAD_BACKUP_REMOTE", "")
        rclone_config = Path(os.environ.get("RCLONE_CONFIG", "/etc/dokumentverkstad/rclone/rclone.conf"))
        preflight(config, args.spool, remote, rclone_config)
        if args.phase == "snapshot":
            snapshot(config, args.spool)
        elif args.phase == "upload":
            upload(config, args.spool, remote, rclone_config)
    except Exception as error:
        # Known adapter errors contain no credentials; other errors only expose their type.
        detail = str(error) if isinstance(error, BackupError) else type(error).__name__
        log(f"backup failed phase={args.phase} reason={detail}")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
