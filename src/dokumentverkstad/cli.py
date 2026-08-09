from __future__ import annotations

import argparse

from .archive import Archive
from .config import load_config
from .index import rebuild_document_index
from .ingest import process_ingest_source
from .web import main as run_web


def main() -> None:
    parser = argparse.ArgumentParser(prog="dokumentverkstad")
    parser.add_argument("--config", help="Path to dokumentverkstad.toml")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("run")
    subparsers.add_parser("process-ingest")
    subparsers.add_parser("rebuild-index")

    args = parser.parse_args()
    command = args.command or "run"

    if command == "run":
        run_web(args.config)
        return

    config = load_config(args.config)
    archive = Archive(config.archive_root)
    archive.initialize()
    config.runtime_root.mkdir(parents=True, exist_ok=True)

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

    parser.error(f"OkÃ¤nt kommando: {command}")
