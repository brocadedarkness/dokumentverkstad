from __future__ import annotations

import unittest
from pathlib import Path

from dokumentverkstad.archive import Archive
from helpers import workspace_tempdir


class ArchiveTests(unittest.TestCase):
    def test_create_and_read_knowledge_object(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")

            created = archive.create_knowledge_object("North påminner om Boyd.")
            loaded = archive.get_knowledge_object(created.id)

            self.assertEqual(loaded.content, "North påminner om Boyd.")
            self.assertEqual(loaded.creator, "user")
            self.assertEqual(loaded.history, ())

    def test_update_preserves_history(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            created = archive.create_knowledge_object("Första formuleringen.")

            updated = archive.update_knowledge_object(
                created.id, "Andra formuleringen."
            )

            self.assertEqual(updated.content, "Andra formuleringen.")
            self.assertEqual(len(updated.history), 1)
            self.assertEqual(updated.history[0].content, "Första formuleringen.")

    def test_data_survives_new_archive_instance(self) -> None:
        with workspace_tempdir() as tmp:
            archive_root = Path(tmp) / "archive"
            first_archive = Archive(archive_root)
            created = first_archive.create_knowledge_object("Finns kvar imorgon.")

            second_archive = Archive(archive_root)
            loaded = second_archive.get_knowledge_object(created.id)

            self.assertEqual(loaded.content, "Finns kvar imorgon.")

    def test_empty_content_is_rejected(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")

            with self.assertRaises(ValueError):
                archive.create_knowledge_object("   ")


if __name__ == "__main__":
    unittest.main()
