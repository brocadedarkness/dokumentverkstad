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
                        'ai_provider = "mock"',
                        'ai_model = "test-model"',
                        "ai_max_output_tokens = 4321",
                        "upload_max_bytes = 123456789",
                        'secrets_path = "local-secrets.toml"',
                        'encrypted_secrets_path = "local-secrets.enc"',
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
            self.assertEqual(config.ai_provider, "mock")
            self.assertEqual(config.ai_model, "test-model")
            self.assertEqual(config.ai_max_output_tokens, 4321)
            self.assertEqual(config.upload_max_bytes, 123456789)
            self.assertEqual(
                config.secrets_path, (Path(tmp) / "local-secrets.toml").resolve()
            )
            self.assertEqual(
                config.encrypted_secrets_path,
                (Path(tmp) / "local-secrets.enc").resolve(),
            )

    def test_loads_config_file_with_utf8_bom(self) -> None:
        with workspace_tempdir() as tmp:
            config_path = Path(tmp) / "dokumentverkstad.toml"
            config_path.write_text(
                'archive_root = "archive"\n',
                encoding="utf-8-sig",
            )

            config = load_config(config_path)

            self.assertEqual(config.archive_root, (Path(tmp) / "archive").resolve())

    def test_environment_overrides_server_paths_and_network_settings(self) -> None:
        names = {
            "DOKUMENTVERKSTAD_CONFIG": None,
            "DOKUMENTVERKSTAD_ARCHIVE_ROOT": None,
            "DOKUMENTVERKSTAD_RUNTIME_ROOT": None,
            "DOKUMENTVERKSTAD_INGEST_SOURCE": None,
            "DOKUMENTVERKSTAD_HOST": None,
            "DOKUMENTVERKSTAD_PORT": None,
            "DOKUMENTVERKSTAD_SECRETS_PATH": None,
            "DOKUMENTVERKSTAD_ENCRYPTED_SECRETS_PATH": None,
        }
        previous = {name: os.environ.get(name) for name in names}
        try:
            with workspace_tempdir() as tmp:
                root = Path(tmp)
                os.environ["DOKUMENTVERKSTAD_ARCHIVE_ROOT"] = str(root / "srv-archive")
                os.environ["DOKUMENTVERKSTAD_RUNTIME_ROOT"] = str(root / "srv-runtime")
                os.environ["DOKUMENTVERKSTAD_INGEST_SOURCE"] = str(root / "srv-ingest")
                os.environ["DOKUMENTVERKSTAD_HOST"] = "0.0.0.0"
                os.environ["DOKUMENTVERKSTAD_PORT"] = "8765"
                os.environ["DOKUMENTVERKSTAD_SECRETS_PATH"] = str(root / "legacy.toml")
                os.environ["DOKUMENTVERKSTAD_ENCRYPTED_SECRETS_PATH"] = str(
                    root / "secrets.enc"
                )

                config = load_config()

                self.assertEqual(config.archive_root, (root / "srv-archive").resolve())
                self.assertEqual(config.runtime_root, (root / "srv-runtime").resolve())
                self.assertEqual(config.ingest_source, (root / "srv-ingest").resolve())
                self.assertEqual(config.host, "0.0.0.0")
                self.assertEqual(config.port, 8765)
                self.assertEqual(config.secrets_path, (root / "legacy.toml").resolve())
                self.assertEqual(
                    config.encrypted_secrets_path, (root / "secrets.enc").resolve()
                )
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value

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
        self.assertEqual(
            config.encrypted_secrets_path,
            (Path.cwd() / ".dokumentverkstad" / "secrets.enc").resolve(),
        )
        self.assertEqual(config.upload_max_bytes, 250 * 1024 * 1024)

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
