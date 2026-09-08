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
    ai_provider: str = "openai"
    ai_model: str = "gpt-5.6-luna"
    ai_max_output_tokens: int = 6000
    ai_output_language: str = "sv"
    ai_currency: str = "USD"
    ai_cost_limit: float = 0.0
    upload_max_bytes: int = 250 * 1024 * 1024
    secrets_path: Path = Path(".dokumentverkstad/secrets.toml")
    encrypted_secrets_path: Path = Path(".dokumentverkstad/secrets.enc")


class ConfigurationError(Exception):
    pass


def load_config(config_path: str | Path | None = None) -> AppConfig:
    path = _resolve_config_path(config_path)
    data = _read_config(path) if path else {}
    base = path.parent if path else Path.cwd()

    archive_root = _path_setting(
        data, "archive_root", "DOKUMENTVERKSTAD_ARCHIVE_ROOT", ".dokumentverkstad/archive", base
    )
    runtime_root = _path_setting(
        data, "runtime_root", "DOKUMENTVERKSTAD_RUNTIME_ROOT", ".dokumentverkstad/runtime", base
    )
    ingest_source = _path_setting(
        data, "ingest_source", "DOKUMENTVERKSTAD_INGEST_SOURCE", ".dokumentverkstad/ingest", base
    )
    host = str(_setting(data, "host", "DOKUMENTVERKSTAD_HOST", "127.0.0.1"))
    port = int(_setting(data, "port", "DOKUMENTVERKSTAD_PORT", 8000))
    ai_provider = str(data.get("ai_provider", "openai"))
    ai_model = str(data.get("ai_model", "gpt-5.6-luna"))
    ai_max_output_tokens = int(data.get("ai_max_output_tokens", 6000))
    ai_output_language = str(data.get("ai_output_language", "sv"))
    ai_currency = str(data.get("ai_currency", "USD"))
    ai_cost_limit = float(data.get("ai_cost_limit", 0.0))
    upload_max_bytes = int(data.get("upload_max_bytes", 250 * 1024 * 1024))
    secrets_path = _path_setting(
        data,
        "secrets_path",
        "DOKUMENTVERKSTAD_SECRETS_PATH",
        ".dokumentverkstad/secrets.toml",
        base,
    )
    encrypted_secrets_path = _path_setting(
        data,
        "encrypted_secrets_path",
        "DOKUMENTVERKSTAD_ENCRYPTED_SECRETS_PATH",
        ".dokumentverkstad/secrets.enc",
        base,
    )

    return AppConfig(
        archive_root=archive_root,
        runtime_root=runtime_root,
        ingest_source=ingest_source,
        host=host,
        port=port,
        ai_provider=ai_provider,
        ai_model=ai_model,
        ai_max_output_tokens=ai_max_output_tokens,
        ai_output_language=ai_output_language,
        ai_currency=ai_currency,
        ai_cost_limit=ai_cost_limit,
        upload_max_bytes=upload_max_bytes,
        secrets_path=secrets_path,
        encrypted_secrets_path=encrypted_secrets_path,
    )


def ensure_app_directories(config: AppConfig) -> None:
    ensure_directory(config.archive_root, "archive_root")
    ensure_directory(config.runtime_root, "runtime_root")
    ensure_directory(config.ingest_source, "ingest_source")


def default_config_path() -> Path:
    return Path("dokumentverkstad.toml").resolve()


def write_default_config(config_path: str | Path, overwrite: bool = False) -> Path:
    path = Path(config_path).expanduser().resolve()
    if path.exists() and not overwrite:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(default_config_text(), encoding="utf-8")
    return path


def default_config_text() -> str:
    return "\n".join(
        [
            'archive_root = ".dokumentverkstad/archive"',
            'runtime_root = ".dokumentverkstad/runtime"',
            'ingest_source = ".dokumentverkstad/ingest"',
            'host = "127.0.0.1"',
            "port = 8000",
            'ai_provider = "openai"',
            'ai_model = "gpt-5.6-luna"',
            "ai_max_output_tokens = 6000",
            'ai_output_language = "sv"',
            'ai_currency = "USD"',
            "ai_cost_limit = 0.0",
            "upload_max_bytes = 262144000",
            'encrypted_secrets_path = ".dokumentverkstad/secrets.enc"',
            'secrets_path = ".dokumentverkstad/secrets.toml"',
            "",
        ]
    )


def ensure_directory(path: str | Path, parameter_name: str) -> Path:
    resolved = Path(path).expanduser().resolve()
    try:
        resolved.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise ConfigurationError(
            _directory_error_message(resolved, parameter_name)
        ) from error

    if not resolved.is_dir():
        raise ConfigurationError(_directory_error_message(resolved, parameter_name))
    return resolved


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
    return tomllib.loads(path.read_text(encoding="utf-8-sig"))


def _resolve_path(base: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    return (base / path).resolve()


def _setting(
    data: dict[str, object], key: str, env_name: str, default: object
) -> object:
    value = os.environ.get(env_name)
    if value is not None and value.strip():
        return value
    return data.get(key, default)


def _path_setting(
    data: dict[str, object],
    key: str,
    env_name: str,
    default: str,
    config_base: Path,
) -> Path:
    value = os.environ.get(env_name)
    if value is not None and value.strip():
        return Path(value).expanduser().resolve()
    return _resolve_path(config_base, Path(data.get(key, default)))


def _directory_error_message(path: Path, parameter_name: str) -> str:
    return (
        f"Kunde inte skapa katalogen för `{parameter_name}`.\n"
        f"Sökväg: {path}\n"
        f"Ändra konfigurationsparametern `{parameter_name}` till en skrivbar katalog."
    )
