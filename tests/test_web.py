from __future__ import annotations

import unittest
from pathlib import Path

from dokumentverkstad.archive import Archive
from dokumentverkstad.ingest import calculate_checksum
from dokumentverkstad.web import CaptureApp
from helpers import workspace_tempdir, write_minimal_pdf


class CaptureAppTests(unittest.TestCase):
    def test_render_capture_has_empty_field_and_recent_notes(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            archive.create_knowledge_object("North påminner om Boyd.")
            app = CaptureApp(archive)

            html = app.render_capture()

            self.assertIn("<textarea", html)
            self.assertIn("autofocus", html)
            self.assertIn("North påminner om Boyd.", html)

    def test_render_capture_submits_on_enter_but_not_shift_enter(self) -> None:
        with workspace_tempdir() as tmp:
            app = CaptureApp(Archive(Path(tmp) / "archive"))

            html = app.render_capture()

            self.assertIn('event.key === "Enter" && !event.shiftKey', html)
            self.assertIn("event.preventDefault();", html)
            self.assertIn("captureForm.requestSubmit()", html)

    def test_posted_form_creates_note(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            app = CaptureApp(archive)

            app.create_note_from_form("content=Ny+notering".encode("utf-8"))

            notes = archive.list_recent_knowledge_objects()
            self.assertEqual(len(notes), 1)
            self.assertEqual(notes[0].content, "Ny notering")

    def test_document_form_creates_manual_document_without_original_file(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            app = CaptureApp(archive)

            document = app.create_document_from_form(
                "title=Andens+fenomenologi&author=Hegel".encode("utf-8")
            )

            loaded = archive.get_document(document.id)
            self.assertEqual(loaded.title, "Andens fenomenologi")
            self.assertEqual(loaded.author, "Hegel")
            self.assertFalse(loaded.has_original_file)

    def test_render_documents_lists_manual_documents(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            archive.create_document("Andens fenomenologi")
            app = CaptureApp(archive)

            html = app.render_documents()

            self.assertIn("Andens fenomenologi", html)
            self.assertIn('action="/documents"', html)

    def test_render_document_shows_capture_context_and_linked_notes(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Andens fenomenologi")
            archive.create_knowledge_object(
                "Detta liknar North.",
                document_id=document.id,
                source_location="kapitel 4",
            )
            archive.create_knowledge_object("Fristående notering.")
            app = CaptureApp(archive)

            html = app.render_document(document.id)

            self.assertIn("Andens fenomenologi", html)
            self.assertIn("Aktuellt dokument", html)
            self.assertIn(f'value="{document.id}"', html)
            self.assertIn("Källposition", html)
            self.assertIn("Detta liknar North.", html)
            self.assertIn("kapitel 4", html)
            self.assertNotIn("Fristående notering.", html)

    def test_render_pdf_document_links_to_original_file(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            archive = Archive(root / "archive")
            pdf_path = root / "rapport.pdf"
            write_minimal_pdf(pdf_path, title="Digital rapport")
            document = archive.register_document_with_original_pdf(
                original_path=pdf_path,
                title="Digital rapport",
                text="Extraherad text",
                checksum_sha256=calculate_checksum(pdf_path),
            )
            app = CaptureApp(archive)

            html = app.render_document(document.id)

            self.assertIn(f"/documents/{document.id}/original", html)
            self.assertIn("rapport.pdf", html)

    def test_document_context_capture_creates_linked_note_with_source(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Andens fenomenologi")
            app = CaptureApp(archive)

            app.create_note_from_form(
                (
                    f"content=Ny+notering&document_id={document.id}"
                    "&source_location=s.+35"
                ).encode("utf-8")
            )

            notes = archive.list_knowledge_objects_for_document(document.id)
            self.assertEqual(len(notes), 1)
            self.assertEqual(notes[0].content, "Ny notering")
            self.assertEqual(notes[0].source_location, "s. 35")

    def test_project_form_creates_project(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            app = CaptureApp(archive)

            project = app.create_project_from_form(
                "name=R%C3%A4vfilosofi&description=Ett+projekt".encode("utf-8")
            )

            loaded = archive.get_project(project.id)
            self.assertEqual(loaded.name, "Rävfilosofi")
            self.assertEqual(loaded.description, "Ett projekt")

    def test_project_form_updates_name_and_description(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            project = archive.create_project("Rävfilosofi")
            app = CaptureApp(archive)

            app.update_project_from_form(
                project.id,
                "name=Institutioner&description=Ny+beskrivning".encode("utf-8"),
            )

            loaded = archive.get_project(project.id)
            self.assertEqual(loaded.name, "Institutioner")
            self.assertEqual(loaded.description, "Ny beskrivning")

    def test_render_project_shows_linked_notes_and_derived_documents(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            project = archive.create_project("Rävfilosofi")
            document = archive.create_document("North")
            archive.create_knowledge_object(
                "Projektanteckning",
                document_id=document.id,
                project_ids=(project.id,),
            )
            archive.create_knowledge_object("Utanför projektet")
            app = CaptureApp(archive)

            html = app.render_project(project.id)

            self.assertIn("Rävfilosofi", html)
            self.assertIn("Projektanteckning", html)
            self.assertIn("North", html)
            self.assertNotIn("Utanför projektet</p><small>ID:", html)

    def test_project_capture_suggests_project_but_can_be_removed(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            project = archive.create_project("Rävfilosofi")
            app = CaptureApp(archive)

            html = app.render_capture(project=project)
            app.create_note_from_form("content=Utan+projekt".encode("utf-8"))
            app.create_note_from_form(
                f"content=Med+projekt&project_id={project.id}".encode("utf-8")
            )

            notes = archive.list_recent_knowledge_objects()
            linked_notes = archive.list_knowledge_objects_for_project(project.id)
            unlinked = [note for note in notes if note.content == "Utan projekt"][0]

            self.assertIn("Aktuellt project", html)
            self.assertIn('type="checkbox"', html)
            self.assertIn("checked", html)
            self.assertEqual(unlinked.project_ids, ())
            self.assertEqual([note.content for note in linked_notes], ["Med projekt"])

    def test_link_existing_note_to_project_from_form(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            project = archive.create_project("Rävfilosofi")
            note = archive.create_knowledge_object("Befintlig notering")
            app = CaptureApp(archive)

            app.link_note_to_project_from_form(
                project.id, f"object_id={note.id}".encode("utf-8")
            )

            linked = archive.list_knowledge_objects_for_project(project.id)
            self.assertEqual([item.id for item in linked], [note.id])

    def test_relation_form_creates_general_relation(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            first = archive.create_knowledge_object("North")
            second = archive.create_knowledge_object("Boyd")
            app = CaptureApp(archive)

            app.create_relation_from_form(
                (
                    f"source_id={first.id}&target_id={second.id}"
                    "&comment=Samma+tema"
                ).encode("utf-8")
            )

            relation_files = list((Path(tmp) / "archive" / "relations").glob("*/relation.json"))
            self.assertEqual(len(relation_files), 1)
            loaded = archive.get_relation(relation_files[0].parent.name)
            self.assertEqual(loaded.relation_type, "hör ihop med")
            self.assertEqual(loaded.comment, "Samma tema")


if __name__ == "__main__":
    unittest.main()
