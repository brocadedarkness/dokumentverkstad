from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import tomllib


@dataclass(frozen=True)
class AppConfig:
    archive_root: Path
    runtime_root: Path
    ingest_source: Path
    host: str = "127.0.0.1"
    port: int = 8000


def load_config(config_path: str | Path | None = None) -> AppConfig:
    path = _resolve_config_path(config_path)
    data = _read_config(path) if path else {}

    archive_root = Path(data.get("archive_root", ".dokumentverkstad/archive"))
    runtime_root = Path(data.get("runtime_root", ".dokumentverkstad/runtime"))
    ingest_source = Path(data.get("ingest_source", ".dokumentverkstad/ingest"))
    host = str(data.get("host", "127.0.0.1"))
    port = int(data.get("port", 8000))

    base = path.parent if path else Path.cwd()
    return AppConfig(
        archive_root=_resolve_path(base, archive_root),
        runtime_root=_resolve_path(base, runtime_root),
        ingest_source=_resolve_path(base, ingest_source),
        host=host,
        port=port,
    )


def _resolve_config_path(config_path: str | Path | None) -> Path | None:
    if config_path:
        return Path(config_path).expanduser().resolve()

    env_path = os.environ.get("DOKUMENTVERKSTAD_CONFIG")
    if env_path:
        return Path(env_path).expanduser().resolve()

    default_path = Path("dokumentverkstad.toml")
    if default_path.exists():
        return default_path.resolve()

    return None


def _read_config(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return data


def _resolve_path(base: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    return (base / path).resolve()
