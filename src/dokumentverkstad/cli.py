from __future__ import annotations

import argparse
import sys

from .archive import Archive
from .config import ConfigurationError, ensure_app_directories, load_config
from .index import rebuild_document_index
from .ingest import process_ingest_source
from .web import main as run_web


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="dokumentverkstad")
    parser.add_argument("--config", help="Path to dokumentverkstad.toml")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("run")
    subparsers.add_parser("process-ingest")
    subparsers.add_parser("rebuild-index")

    args = parser.parse_args(argv)
    command = args.command or "run"

    try:
        if command == "run":
            run_web(args.config)
            return

        config = load_config(args.config)
        ensure_app_directories(config)
        archive = Archive(config.archive_root)
        archive.initialize()

        if command == "process-ingest":
            results = process_ingest_source(
                archive=archive,
                ingest_source=config.ingest_source,
                runtime_root=config.runtime_root,
            )
            rebuild_document_index(archive, config.runtime_root)
            created = sum(1 for result in results if result.created)
            duplicates = len(results) - created
            print(f"Registrerade {created} PDF-dokument. Dubbletter: {duplicates}.")
            return

        if command == "rebuild-index":
            database_path = rebuild_document_index(archive, config.runtime_root)
            print(f"Index Ã¥terskapat: {database_path}")
            return
    except ConfigurationError as error:
        print(error, file=sys.stderr)
        raise SystemExit(2) from error

    parser.error(f"OkÃ¤nt kommando: {command}")
