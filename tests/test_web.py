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

    def test_posted_form_creates_note(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            app = CaptureApp(archive)

            app.create_note_from_form("content=Ny+notering".encode("utf-8"))

            notes = archive.list_recent_knowledge_objects()
            self.assertEqual(len(notes), 1)
            self.assertEqual(notes[0].content, "Ny notering")


if __name__ == "__main__":
    unittest.main()
