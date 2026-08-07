from __future__ import annotations

import os
import unittest
from pathlib import Path

from dokumentverkstad.config import load_config
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
                        'host = "0.0.0.0"',
                        "port = 8123",
                    ]
                ),
                encoding="utf-8",
            )

            config = load_config(config_path)

            self.assertEqual(config.archive_root, (Path(tmp) / "archive").resolve())
            self.assertEqual(config.runtime_root, (Path(tmp) / "runtime").resolve())
            self.assertEqual(config.host, "0.0.0.0")
            self.assertEqual(config.port, 8123)

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


if __name__ == "__main__":
    unittest.main()
