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
            self.assertEqual(loaded.document_id, "")
            self.assertEqual(loaded.source_location, "")

    def test_create_and_read_manual_document(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")

            created = archive.create_document(
                title="Andens fenomenologi",
                author="Hegel",
                year="1807",
                comment="Fysisk bok.",
            )
            loaded = archive.get_document(created.id)

            self.assertEqual(loaded.title, "Andens fenomenologi")
            self.assertEqual(loaded.author, "Hegel")
            self.assertEqual(loaded.year, "1807")
            self.assertEqual(loaded.comment, "Fysisk bok.")
            self.assertFalse(loaded.has_original_file)

    def test_document_metadata_can_be_updated(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            created = archive.create_document("Andens fenomenologi")

            updated = archive.update_document(
                created.id, title="Phänomenologie des Geistes", year="1807"
            )

            self.assertEqual(updated.title, "Phänomenologie des Geistes")
            self.assertEqual(updated.year, "1807")

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

    def test_knowledge_object_can_reference_document_and_source_location(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Andens fenomenologi")

            note = archive.create_knowledge_object(
                "Detta bör jämföras med North.",
                document_id=document.id,
                source_location="kapitel 4",
            )

            loaded = archive.get_knowledge_object(note.id)
            linked_notes = archive.list_knowledge_objects_for_document(document.id)

            self.assertEqual(loaded.document_id, document.id)
            self.assertEqual(loaded.source_location, "kapitel 4")
            self.assertEqual([item.id for item in linked_notes], [note.id])


if __name__ == "__main__":
    unittest.main()
