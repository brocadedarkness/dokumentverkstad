from __future__ import annotations

import unittest
from pathlib import Path

from dokumentverkstad.archive import Archive
from dokumentverkstad.web import CaptureApp
from helpers import workspace_tempdir


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


if __name__ == "__main__":
    unittest.main()
