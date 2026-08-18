from __future__ import annotations

import argparse
from getpass import getpass
import os
from pathlib import Path
import sys

from .archive import Archive
from .backup import BackupError, create_backup, restore_backup
from .config import (
    AppConfig,
    ConfigurationError,
    default_config_path,
    ensure_app_directories,
    load_config,
    write_default_config,
)
from .index import rebuild_document_index
from .ingest import process_ingest_source
from .secrets import (
    SecretsError,
    encrypted_secrets_exists,
    has_unlocked_openai_api_key,
    initialize_encrypted_secrets,
    load_openai_api_key,
    remove_openai_api_key,
    set_openai_api_key,
)
from .web import main as run_web


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="dokumentverkstad")
    parser.add_argument("--config", help="Path to dokumentverkstad.toml")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("run")
    subparsers.add_parser("start")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--force", action="store_true")
    init_parser.add_argument("--with-secrets", action="store_true")
    init_parser.add_argument("--with-openai", action="store_true")

    subparsers.add_parser("status")

    secrets_parser = subparsers.add_parser("secrets")
    secrets_subparsers = secrets_parser.add_subparsers(dest="secrets_command")
    secrets_subparsers.add_parser("init")
    secrets_subparsers.add_parser("set-openai")
    secrets_subparsers.add_parser("remove-openai")

    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("--output-dir", help="Katalog där backupfilen skapas")

    restore_parser = subparsers.add_parser("restore")
    restore_parser.add_argument("backup_file")
    restore_parser.add_argument("--force", action="store_true")

    subparsers.add_parser("process-ingest")
    subparsers.add_parser("rebuild-index")

    args = parser.parse_args(argv)
    command = args.command or "run"

    try:
        if command in {"run", "start"}:
            run_web(args.config)
            return

        if command == "init":
            _initialize_installation(args)
            return

        config = load_config(args.config)
        ensure_app_directories(config)
        archive = Archive(config.archive_root)
        archive.initialize()

        if command == "status":
            _print_status(config, args.config)
            return

        if command == "secrets":
            _handle_secrets_command(args.secrets_command, config)
            return

        if command == "process-ingest":
            results = process_ingest_source(
                archive=archive,
                ingest_source=config.ingest_source,
                runtime_root=config.runtime_root,
                log=print,
            )
            rebuild_document_index(archive, config.runtime_root)
            created = sum(1 for result in results if result.created)
            failed = sum(1 for result in results if result.error)
            duplicates = len(results) - created - failed
            print(
                f"Registrerade {created} PDF-dokument. "
                f"Dubbletter: {duplicates}. Misslyckade: {failed}."
            )
            return

        if command == "backup":
            result = create_backup(config, output_dir=args.output_dir)
            print("Backup skapad:")
            print(result.path)
            _print_counts(result.counts)
            print(f"Storlek: {result.size_bytes} bytes")
            return

        if command == "restore":
            result = restore_backup(args.backup_file, config, force=args.force)
            print("Backup återställd:")
            print(f"Archive: {result.archive_root}")
            print(f"Index återskapat: {result.index_path}")
            _print_counts(result.counts)
            print("Secrets återställdes inte.")
            return

        if command == "rebuild-index":
            database_path = rebuild_document_index(archive, config.runtime_root)
            print(f"Index återskapat: {database_path}")
            return
    except (ConfigurationError, SecretsError, BackupError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(2) from error

    parser.error(f"Okänt kommando: {command}")


def _initialize_installation(args: argparse.Namespace) -> None:
    config_path = _configured_or_default_config_path(args.config)
    existed = config_path.exists()
    write_default_config(config_path, overwrite=args.force)
    config = load_config(config_path)
    ensure_app_directories(config)
    Archive(config.archive_root).initialize()
    print(f"Config: {config_path}")
    print(f"Archive: {config.archive_root}")
    print(f"Runtime: {config.runtime_root}")
    print(f"Ingest: {config.ingest_source}")
    if existed and not args.force:
        print("Befintlig config bevarades.")
    if config.secrets_path.exists():
        print(
            "Legacy secrets.toml hittades och lämnades oförändrad. "
            "Använd `secrets set-openai` för krypterad lagring."
        )
    if args.with_secrets or args.with_openai:
        _initialize_encrypted_secrets(config.encrypted_secrets_path, args.with_openai)


def _handle_secrets_command(command: str | None, config: AppConfig) -> None:
    if command == "init":
        _initialize_encrypted_secrets(config.encrypted_secrets_path, with_openai=False)
        return
    if command == "set-openai":
        if not encrypted_secrets_exists(config.encrypted_secrets_path):
            _initialize_encrypted_secrets(config.encrypted_secrets_path, with_openai=True)
            return
        password = getpass("Adminlösenord för Dokumentverkstad secrets: ")
        api_key = getpass("OpenAI API key: ")
        set_openai_api_key(config.encrypted_secrets_path, password, api_key)
        print("OpenAI API key sparad i krypterade secrets.")
        return
    if command == "remove-openai":
        password = getpass("Adminlösenord för Dokumentverkstad secrets: ")
        remove_openai_api_key(config.encrypted_secrets_path, password)
        print("OpenAI API key borttagen från krypterade secrets.")
        return
    raise ConfigurationError("Okänt secrets-kommando.")


def _initialize_encrypted_secrets(path: Path, with_openai: bool) -> None:
    if encrypted_secrets_exists(path):
        raise SecretsError("Krypterade secrets finns redan.")
    password = getpass("Nytt adminlösenord för Dokumentverkstad secrets: ")
    repeated = getpass("Upprepa adminlösenord: ")
    if password != repeated:
        raise SecretsError("Adminlösenorden matchar inte.")
    openai_api_key = getpass("OpenAI API key: ") if with_openai else ""
    initialize_encrypted_secrets(path, password, openai_api_key=openai_api_key)
    print(f"Krypterade secrets initierade: {path}")


def _print_status(config: AppConfig, config_path: str | None) -> None:
    print(f"Config: {_configured_or_default_config_path(config_path)}")
    print(f"Archive: {config.archive_root}")
    print(f"Archive tillgängligt: {'ja' if config.archive_root.is_dir() else 'nej'}")
    print(f"Runtime: {config.runtime_root}")
    print(f"Runtime tillgängligt: {'ja' if config.runtime_root.is_dir() else 'nej'}")
    print(f"Ingest: {config.ingest_source}")
    print(
        "Krypterade secrets: "
        f"{'konfigurerade' if config.encrypted_secrets_path.exists() else 'saknas'}"
    )
    if config.secrets_path.exists():
        print("Legacy secrets.toml: finns (lämnas oförändrad)")
    print(f"OpenAI credential: {_credential_status(config)}")

def _print_counts(counts: object) -> None:
    print(f"Documents: {counts.documents}")
    print(f"Knowledge Objects: {counts.knowledge_objects}")
    print(f"Projects: {counts.projects}")
    print(f"AI runs: {counts.ai_runs}")


def _credential_status(config: AppConfig) -> str:
    if os.environ.get("OPENAI_API_KEY", "").strip():
        return "miljövariabel"
    if has_unlocked_openai_api_key():
        return "upplåsta krypterade secrets"
    if config.encrypted_secrets_path.exists():
        return "krypterade secrets finns (låst)"
    if load_openai_api_key(config.secrets_path):
        return "legacy secrets.toml"
    return "saknas"


def _configured_or_default_config_path(config_path: str | None) -> Path:
    if config_path:
        return Path(config_path).expanduser().resolve()
    env_path = os.environ.get("DOKUMENTVERKSTAD_CONFIG", "").strip()
    if env_path:
        return Path(env_path).expanduser().resolve()
    return default_config_path()
