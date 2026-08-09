from __future__ import annotations

from pathlib import Path
import unittest

from dokumentverkstad.archive import Archive
from dokumentverkstad.index import (
    document_index_path,
    list_indexed_documents,
    rebuild_document_index,
)
from dokumentverkstad.ingest import process_ingest_source
from helpers import workspace_tempdir, write_minimal_pdf


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
            self.assertEqual(document.title, "Rapport om institutioner")
            self.assertEqual(document.author, "North")
            self.assertEqual(document.document_type, "PDF")
            self.assertTrue(document.has_original_file)
            self.assertEqual(document.original_filename, "rapport.pdf")
            self.assertEqual(len(document.checksum_sha256), 64)
            self.assertTrue(archive.original_file_path(document.id).exists())
            self.assertIn(
                "Institutions structure incentives.",
                archive.extracted_text_file_path(document.id).read_text(encoding="utf-8"),
            )

    def test_duplicate_pdf_does_not_create_second_document(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            ingest_source = root / "ingest"
            ingest_source.mkdir()
            write_minimal_pdf(ingest_source / "rapport.pdf")
            archive = Archive(root / "archive")

            first_results = process_ingest_source(archive, ingest_source, root / "runtime")
            second_results = process_ingest_source(archive, ingest_source, root / "runtime")

            self.assertTrue(first_results[0].created)
            self.assertFalse(second_results[0].created)
            self.assertEqual(len(archive.list_documents()), 1)
            self.assertEqual(first_results[0].document.id, second_results[0].document.id)

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


if __name__ == "__main__":
    unittest.main()
