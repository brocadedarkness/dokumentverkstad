from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import unittest
from unittest.mock import patch

from dokumentverkstad.cli import main
from dokumentverkstad.secrets import decrypt_secrets_file, initialize_encrypted_secrets
from dokumentverkstad.web import main as web_main
from helpers import workspace_tempdir


class CliTests(unittest.TestCase):
    def test_clear_error_when_configured_directory_cannot_be_created(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            bad_archive_root = root / "archive"
            bad_archive_root.write_text("not a directory", encoding="utf-8")
            config_path = root / "dokumentverkstad.toml"
            config_path.write_text(
                "\n".join(
                    [
                        'archive_root = "archive"',
                        'runtime_root = "runtime"',
                        'ingest_source = "ingest"',
                    ]
                ),
                encoding="utf-8",
            )
            stderr = io.StringIO()

            with self.assertRaises(SystemExit) as context, redirect_stderr(stderr):
                main(["--config", str(config_path), "rebuild-index"])

            self.assertEqual(context.exception.code, 2)
            message = stderr.getvalue()
            self.assertIn("archive_root", message)
            self.assertIn(str(bad_archive_root.resolve()), message)
            self.assertIn("skrivbar katalog", message)

    def test_init_creates_config_directories_and_archive(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config_path = root / "dokumentverkstad.toml"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                main(["--config", str(config_path), "init"])

            self.assertTrue(config_path.exists())
            self.assertTrue((root / ".dokumentverkstad" / "archive").is_dir())
            self.assertTrue((root / ".dokumentverkstad" / "runtime").is_dir())
            self.assertTrue((root / ".dokumentverkstad" / "ingest").is_dir())
            self.assertTrue(
                (root / ".dokumentverkstad" / "archive" / "documents").is_dir()
            )
            self.assertIn("Config:", stdout.getvalue())

    def test_repeated_init_preserves_existing_config(self) -> None:
        with workspace_tempdir() as tmp:
            config_path = Path(tmp) / "dokumentverkstad.toml"
            config_path.write_text(
                'archive_root = "custom-archive"\n',
                encoding="utf-8",
            )

            main(["--config", str(config_path), "init"])

            self.assertIn("custom-archive", config_path.read_text(encoding="utf-8"))
            self.assertTrue((Path(tmp) / "custom-archive").is_dir())

    def test_init_can_create_encrypted_secrets_without_logging_secret_values(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config_path = root / "dokumentverkstad.toml"
            stdout = io.StringIO()
            stderr = io.StringIO()

            with (
                patch(
                    "dokumentverkstad.cli.getpass",
                    side_effect=["admin-passphrase", "admin-passphrase", "sk-secret"],
                ),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                main(["--config", str(config_path), "init", "--with-openai"])

            secrets_path = root / ".dokumentverkstad" / "secrets.enc"
            self.assertTrue(secrets_path.exists())
            self.assertNotIn("admin-passphrase", secrets_path.read_text(encoding="utf-8"))
            self.assertNotIn("sk-secret", secrets_path.read_text(encoding="utf-8"))
            self.assertNotIn("admin-passphrase", stdout.getvalue())
            self.assertNotIn("sk-secret", stdout.getvalue())
            self.assertNotIn("sk-secret", stderr.getvalue())

    def test_status_reports_locations_without_exposing_api_key(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config_path = root / "dokumentverkstad.toml"
            main(["--config", str(config_path), "init"])
            legacy_path = root / ".dokumentverkstad" / "secrets.toml"
            legacy_path.write_text(
                '[openai]\napi_key = "sk-legacy-secret"\n', encoding="utf-8"
            )
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                main(["--config", str(config_path), "status"])

            output = stdout.getvalue()
            self.assertIn("Archive:", output)
            self.assertIn("Runtime:", output)
            self.assertIn("Krypterade secrets:", output)
            self.assertIn("OpenAI credential:", output)
            self.assertNotIn("sk-legacy-secret", output)

    def test_secrets_set_and_remove_openai(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config_path = root / "dokumentverkstad.toml"
            main(["--config", str(config_path), "init"])

            with patch(
                "dokumentverkstad.cli.getpass",
                side_effect=["admin-passphrase", "admin-passphrase", "sk-new-secret"],
            ):
                main(["--config", str(config_path), "secrets", "set-openai"])

            secrets_path = root / ".dokumentverkstad" / "secrets.enc"
            payload = decrypt_secrets_file(secrets_path, "admin-passphrase")
            self.assertEqual(
                payload["providers"]["openai"]["api_key"], "sk-new-secret"
            )

            with patch(
                "dokumentverkstad.cli.getpass",
                side_effect=["admin-passphrase"],
            ):
                main(["--config", str(config_path), "secrets", "remove-openai"])

            payload = decrypt_secrets_file(secrets_path, "admin-passphrase")
            self.assertNotIn("openai", payload["providers"])

    def test_start_with_correct_password_unlocks_before_server_start(self) -> None:
        class FakeServer:
            started = False

            def __init__(self, address, handler):  # type: ignore[no-untyped-def]
                self.address = address
                self.handler = handler

            def serve_forever(self) -> None:
                FakeServer.started = True

        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config_path = root / "dokumentverkstad.toml"
            main(["--config", str(config_path), "init"])
            initialize_encrypted_secrets(
                root / ".dokumentverkstad" / "secrets.enc",
                "admin-passphrase",
                openai_api_key="sk-secret",
                overwrite=True,
            )

            with patch("dokumentverkstad.web.ThreadingHTTPServer", FakeServer):
                web_main(str(config_path), password="admin-passphrase")

            self.assertTrue(FakeServer.started)

    def test_start_with_wrong_password_does_not_start_server(self) -> None:
        class FailingIfCreatedServer:
            def __init__(self, address, handler):  # type: ignore[no-untyped-def]
                raise AssertionError("Server must not start with wrong password")

        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config_path = root / "dokumentverkstad.toml"
            main(["--config", str(config_path), "init"])
            initialize_encrypted_secrets(
                root / ".dokumentverkstad" / "secrets.enc",
                "admin-passphrase",
                openai_api_key="sk-secret",
                overwrite=True,
            )

            with (
                patch(
                    "dokumentverkstad.web.ThreadingHTTPServer",
                    FailingIfCreatedServer,
                ),
                self.assertRaises(SystemExit),
            ):
                web_main(str(config_path), password="wrong")


if __name__ == "__main__":
    unittest.main()
