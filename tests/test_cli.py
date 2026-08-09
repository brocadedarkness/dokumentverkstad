from __future__ import annotations

from contextlib import redirect_stderr
import io
from pathlib import Path
import unittest

from dokumentverkstad.cli import main
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


if __name__ == "__main__":
    unittest.main()
