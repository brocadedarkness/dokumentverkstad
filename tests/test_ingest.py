from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from dokumentverkstad.archive import Archive
from dokumentverkstad.index import (
    document_index_path,
    list_indexed_documents,
    rebuild_document_index,
)
from dokumentverkstad.ingest import process_ingest_source
from helpers import workspace_tempdir, write_minimal_pdf, write_realistic_text_array_pdf


class IngestTests(unittest.TestCase):
    def test_pdf_is_registered_with_original_text_and_metadata(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            ingest_source = root / "ingest"
            ingest_source.mkdir()
            write_minimal_pdf(
                ingest_source / "rapport.pdf",
                title="Rapport om institutioner",
                author="North",
                text="Institutions structure incentives.",
            )
            archive = Archive(root / "archive")

            results = process_ingest_source(archive, ingest_source, root / "runtime")

            self.assertEqual(len(results), 1)
            self.assertTrue(results[0].created)
            document = results[0].document
            self.assertIsNotNone(document)
            self.assertEqual(document.title, "Rapport om institutioner")
            self.assertEqual(document.author, "North")
            self.assertEqual(document.document_type, "PDF")
            self.assertTrue(document.has_original_file)
            self.assertEqual(document.original_filename, "rapport.pdf")
            self.assertEqual(document.inbox_status, "new")
            self.assertEqual(len(document.checksum_sha256), 64)
            self.assertTrue(archive.original_file_path(document.id).exists())
            self.assertIn(
                "Institutions structure incentives.",
                archive.extracted_text_file_path(document.id).read_text(encoding="utf-8"),
            )
            self.assertEqual(
                [item.id for item in archive.list_inbox_documents()],
                [document.id],
            )
            self.assertFalse((ingest_source / "rapport.pdf").exists())
            self.assertTrue(results[0].processed_path.exists())

    def test_duplicate_pdf_does_not_create_second_document(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            ingest_source = root / "ingest"
            ingest_source.mkdir()
            write_minimal_pdf(ingest_source / "rapport.pdf")
            archive = Archive(root / "archive")

            first_results = process_ingest_source(archive, ingest_source, root / "runtime")
            write_minimal_pdf(ingest_source / "rapport.pdf")
            second_results = process_ingest_source(archive, ingest_source, root / "runtime")

            self.assertTrue(first_results[0].created)
            self.assertFalse(second_results[0].created)
            self.assertEqual(len(archive.list_documents()), 1)
            self.assertEqual(first_results[0].document.id, second_results[0].document.id)
            self.assertFalse((ingest_source / "rapport.pdf").exists())
            self.assertTrue(second_results[0].processed_path.exists())

    def test_multiple_pdfs_are_registered_in_one_ingest_pass(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            ingest_source = root / "ingest"
            ingest_source.mkdir()
            write_realistic_text_array_pdf(
                ingest_source / "a.pdf",
                title="Första PDF",
                text="Första texten.",
            )
            write_realistic_text_array_pdf(
                ingest_source / "b.pdf",
                title="Andra PDF",
                text="Andra texten.",
            )
            messages: list[str] = []
            archive = Archive(root / "archive")

            results = process_ingest_source(
                archive, ingest_source, root / "runtime", log=messages.append
            )

            self.assertEqual(len(results), 2)
            self.assertTrue(all(result.created for result in results))
            self.assertEqual(
                [document.title for document in archive.list_documents()],
                ["Andra PDF", "Första PDF"],
            )
            self.assertEqual(list(ingest_source.glob("*.pdf")), [])
            self.assertTrue(all(result.processed_path.exists() for result in results))
            self.assertTrue(any("Behandlar PDF:" in message for message in messages))
            self.assertTrue(any("Steg: extraherar PDF-text" in message for message in messages))
            self.assertTrue(any("Klar: skapade Document" in message for message in messages))

    def test_failed_pdf_does_not_block_following_pdf(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            ingest_source = root / "ingest"
            ingest_source.mkdir()
            write_minimal_pdf(ingest_source / "bad.pdf", title="Felande PDF")
            write_realistic_text_array_pdf(
                ingest_source / "good.pdf",
                title="Efterföljande PDF",
                text="Denna ska gå igenom.",
            )
            messages: list[str] = []
            archive = Archive(root / "archive")

            def fake_extract_pdf(path: Path) -> object:
                if path.name == "bad.pdf":
                    raise ValueError("test failure")
                from dokumentverkstad.pdf import extract_pdf

                return extract_pdf(path)

            with patch("dokumentverkstad.ingest.extract_pdf", side_effect=fake_extract_pdf):
                results = process_ingest_source(
                    archive, ingest_source, root / "runtime", log=messages.append
                )

            self.assertEqual(len(results), 2)
            self.assertIsNone(results[0].document)
            self.assertEqual(results[0].error, "ValueError: test failure")
            self.assertFalse(results[0].created)
            self.assertTrue(results[1].created)
            self.assertEqual(archive.list_documents()[0].title, "Efterföljande PDF")
            self.assertTrue((ingest_source / "bad.pdf").exists())
            self.assertFalse((ingest_source / "good.pdf").exists())
            self.assertTrue(any("Misslyckades: ValueError: test failure" in message for message in messages))

    def test_index_can_be_rebuilt_from_archive(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            ingest_source = root / "ingest"
            runtime_root = root / "runtime"
            ingest_source.mkdir()
            write_minimal_pdf(ingest_source / "rapport.pdf", title="Digital rapport")
            archive = Archive(root / "archive")
            manual = archive.create_document("Fysisk bok")
            process_ingest_source(archive, ingest_source, runtime_root)

            database_path = rebuild_document_index(Archive(root / "archive"), runtime_root)
            rows = list_indexed_documents(runtime_root)

            self.assertEqual(database_path, document_index_path(runtime_root))
            self.assertTrue(database_path.exists())
            self.assertEqual([row["title"] for row in rows], ["Digital rapport", "Fysisk bok"])
            manual_row = [row for row in rows if row["id"] == manual.id][0]
            self.assertEqual(manual_row["has_original_file"], 0)

    def test_ingest_persistence_survives_new_archive_instance(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            ingest_source = root / "ingest"
            ingest_source.mkdir()
            write_minimal_pdf(ingest_source / "rapport.pdf", title="Persistent PDF")
            archive = Archive(root / "archive")

            document = process_ingest_source(archive, ingest_source, root / "runtime")[0].document
            restarted_archive = Archive(root / "archive")

            loaded = restarted_archive.get_document(document.id)
            self.assertEqual(loaded.title, "Persistent PDF")
            self.assertTrue(restarted_archive.original_file_path(document.id).exists())

    def test_process_ingest_creates_missing_ingest_and_runtime_directories(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            archive = Archive(root / "archive")

            results = process_ingest_source(
                archive=archive,
                ingest_source=root / "ingest",
                runtime_root=root / "runtime",
            )

            self.assertEqual(results, [])
            self.assertTrue((root / "ingest").is_dir())
            self.assertTrue((root / "runtime").is_dir())
            self.assertTrue((root / "runtime" / "ingest").is_dir())


if __name__ == "__main__":
    unittest.main()
