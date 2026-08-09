from __future__ import annotations

import os
import unittest
from pathlib import Path

from dokumentverkstad.config import (
    AppConfig,
    ConfigurationError,
    ensure_app_directories,
    ensure_directory,
    load_config,
)
from helpers import workspace_tempdir


class ConfigTests(unittest.TestCase):
    def test_loads_archive_and_runtime_roots_from_config_file(self) -> None:
        with workspace_tempdir() as tmp:
            config_path = Path(tmp) / "dokumentverkstad.toml"
            config_path.write_text(
                "\n".join(
                    [
                        'archive_root = "archive"',
                        'runtime_root = "runtime"',
                        'ingest_source = "incoming"',
                        'host = "0.0.0.0"',
                        "port = 8123",
                    ]
                ),
                encoding="utf-8",
            )

            config = load_config(config_path)

            self.assertEqual(config.archive_root, (Path(tmp) / "archive").resolve())
            self.assertEqual(config.runtime_root, (Path(tmp) / "runtime").resolve())
            self.assertEqual(config.ingest_source, (Path(tmp) / "incoming").resolve())
            self.assertEqual(config.host, "0.0.0.0")
            self.assertEqual(config.port, 8123)

    def test_loads_config_file_with_utf8_bom(self) -> None:
        with workspace_tempdir() as tmp:
            config_path = Path(tmp) / "dokumentverkstad.toml"
            config_path.write_text(
                'archive_root = "archive"\n',
                encoding="utf-8-sig",
            )

            config = load_config(config_path)

            self.assertEqual(config.archive_root, (Path(tmp) / "archive").resolve())

    def test_defaults_are_local_to_current_working_directory(self) -> None:
        previous = os.environ.pop("DOKUMENTVERKSTAD_CONFIG", None)
        try:
            config = load_config()
        finally:
            if previous is not None:
                os.environ["DOKUMENTVERKSTAD_CONFIG"] = previous

        self.assertEqual(
            config.archive_root,
            (Path.cwd() / ".dokumentverkstad" / "archive").resolve(),
        )
        self.assertEqual(
            config.runtime_root,
            (Path.cwd() / ".dokumentverkstad" / "runtime").resolve(),
        )
        self.assertEqual(
            config.ingest_source,
            (Path.cwd() / ".dokumentverkstad" / "ingest").resolve(),
        )

    def test_missing_configured_directories_are_created(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = AppConfig(
                archive_root=root / "archive",
                runtime_root=root / "runtime",
                ingest_source=root / "ingest",
            )

            ensure_app_directories(config)

            self.assertTrue(config.archive_root.is_dir())
            self.assertTrue(config.runtime_root.is_dir())
            self.assertTrue(config.ingest_source.is_dir())

    def test_directory_error_names_parameter_and_full_path(self) -> None:
        with workspace_tempdir() as tmp:
            configured_path = Path(tmp) / "not-a-directory"
            configured_path.write_text("already a file", encoding="utf-8")

            with self.assertRaises(ConfigurationError) as context:
                ensure_directory(configured_path, "archive_root")

            message = str(context.exception)
            self.assertIn("archive_root", message)
            self.assertIn(str(configured_path.resolve()), message)
            self.assertIn("skrivbar katalog", message)


if __name__ == "__main__":
    unittest.main()
