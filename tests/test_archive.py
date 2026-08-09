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
            self.assertEqual(loaded.inbox_status, "new")
            self.assertEqual(loaded.project_ids, ())

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

    def test_create_update_and_read_project(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")

            project = archive.create_project("Rävfilosofi", "Ett arbetsområde.")
            updated = archive.update_project(
                project.id, name="Rävfilosofi 2", description="Ny beskrivning."
            )
            loaded = archive.get_project(project.id)

            self.assertEqual(updated.name, "Rävfilosofi 2")
            self.assertEqual(loaded.description, "Ny beskrivning.")

    def test_knowledge_object_can_belong_to_multiple_projects(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            first_project = archive.create_project("Rävfilosofi")
            second_project = archive.create_project("Institutioner")
            note = archive.create_knowledge_object("North påminner om Boyd.")

            updated = archive.set_knowledge_object_projects(
                note.id, (first_project.id, second_project.id)
            )

            self.assertEqual(
                updated.project_ids, (first_project.id, second_project.id)
            )
            self.assertEqual(
                [item.id for item in archive.list_knowledge_objects_for_project(first_project.id)],
                [note.id],
            )
            self.assertEqual(
                [item.id for item in archive.list_knowledge_objects_for_project(second_project.id)],
                [note.id],
            )

    def test_project_documents_are_derived_from_linked_knowledge_objects(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            project = archive.create_project("Rävfilosofi")
            first_document = archive.create_document("Platon")
            second_document = archive.create_document("North")
            archive.create_knowledge_object(
                "Notering A",
                document_id=first_document.id,
                project_ids=(project.id,),
            )
            archive.create_knowledge_object(
                "Notering B",
                document_id=first_document.id,
                project_ids=(project.id,),
            )
            archive.create_knowledge_object(
                "Notering C",
                document_id=second_document.id,
                project_ids=(project.id,),
            )

            documents = archive.list_documents_for_project(project.id)

            self.assertEqual(
                [document.title for document in documents], ["North", "Platon"]
            )
            self.assertNotIn("project", first_document.to_dict())

    def test_document_can_be_linked_directly_to_multiple_projects(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            first_project = archive.create_project("Rävfilosofi")
            second_project = archive.create_project("Institutioner")
            document = archive.create_document("North")

            updated = archive.set_document_projects(
                document.id, (first_project.id, second_project.id)
            )

            self.assertEqual(
                updated.project_ids, (first_project.id, second_project.id)
            )
            self.assertEqual(
                [item.id for item in archive.list_documents_for_project(first_project.id)],
                [document.id],
            )
            self.assertEqual(
                [item.id for item in archive.list_documents_for_project(second_project.id)],
                [document.id],
            )

    def test_project_documents_include_direct_and_knowledge_derived_documents_once(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            project = archive.create_project("Rävfilosofi")
            direct_document = archive.create_document("Direkt dokument")
            shared_document = archive.create_document("Båda vägar")
            derived_document = archive.create_document("Via notering")
            archive.set_document_projects(shared_document.id, (project.id,))
            archive.set_document_projects(direct_document.id, (project.id,))
            archive.create_knowledge_object(
                "Notering",
                document_id=shared_document.id,
                project_ids=(project.id,),
            )
            archive.create_knowledge_object(
                "Annan notering",
                document_id=derived_document.id,
                project_ids=(project.id,),
            )

            documents = archive.list_documents_for_project(project.id)

            self.assertEqual(
                [document.title for document in documents],
                ["Båda vägar", "Direkt dokument", "Via notering"],
            )

    def test_knowledge_object_can_still_be_created_without_context(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")

            note = archive.create_knowledge_object("Fristående tanke.")

            self.assertEqual(note.document_id, "")
            self.assertEqual(note.project_ids, ())

    def test_relation_between_knowledge_objects_is_persistent(self) -> None:
        with workspace_tempdir() as tmp:
            archive_root = Path(tmp) / "archive"
            archive = Archive(archive_root)
            first = archive.create_knowledge_object("North.")
            second = archive.create_knowledge_object("Boyd.")

            relation = archive.create_relation(
                first.id, second.id, comment="Samma problem från olika håll."
            )

            restarted_archive = Archive(archive_root)
            loaded = restarted_archive.get_relation(relation.id)

            self.assertEqual(loaded.source_id, first.id)
            self.assertEqual(loaded.target_id, second.id)
            self.assertEqual(loaded.relation_type, "hör ihop med")
            self.assertEqual(loaded.comment, "Samma problem från olika håll.")

    def test_document_inbox_status_and_restore_are_persistent(self) -> None:
        with workspace_tempdir() as tmp:
            archive_root = Path(tmp) / "archive"
            archive = Archive(archive_root)
            document = archive.create_document("Nytt dokument")

            self.assertEqual([item.id for item in archive.list_inbox_documents()], [document.id])

            archive.set_document_inbox_status(document.id, "later")
            restarted_archive = Archive(archive_root)
            later_document = restarted_archive.get_document(document.id)

            self.assertEqual(later_document.inbox_status, "later")
            self.assertEqual(
                [item.id for item in restarted_archive.list_inbox_documents()],
                [document.id],
            )

            restarted_archive.set_document_inbox_status(document.id, "trashed")
            self.assertEqual(restarted_archive.list_inbox_documents(), [])
            self.assertEqual(
                [item.id for item in restarted_archive.list_trashed_documents()],
                [document.id],
            )

            restored = Archive(archive_root).restore_document(document.id)
            self.assertEqual(restored.inbox_status, "new")
            self.assertEqual(
                [item.id for item in Archive(archive_root).list_inbox_documents()],
                [document.id],
            )


if __name__ == "__main__":
    unittest.main()
