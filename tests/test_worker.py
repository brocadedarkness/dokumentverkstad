from __future__ import annotations

from pathlib import Path
import unittest

from dokumentverkstad.ai import AiAnalysisResult, AiProvider, AiProviderError, AiUsage
from dokumentverkstad.archive import Archive
from dokumentverkstad.config import AppConfig
from dokumentverkstad.index import list_indexed_documents
from dokumentverkstad.ingest import calculate_checksum, inspect_ingest_queue
from dokumentverkstad.web import CaptureApp
from dokumentverkstad.worker import process_worker_cycle
from helpers import workspace_tempdir, write_minimal_pdf, write_realistic_text_array_pdf


class EmptyAiProvider(AiProvider):
    name = "mock"

    def analyze_document(self, **kwargs):  # type: ignore[no-untyped-def]
        return AiAnalysisResult(candidates=(), usage=AiUsage(input_tokens=10, output_tokens=1))


class FailingAiProvider(AiProvider):
    name = "mock"

    def analyze_document(self, **kwargs):  # type: ignore[no-untyped-def]
        raise AiProviderError("simulerat AI-fel")


class WorkerTests(unittest.TestCase):
    def test_worker_cycle_processes_queued_pdf_and_rebuilds_index(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _config(root)
            config.ingest_source.mkdir(parents=True)
            write_minimal_pdf(
                config.ingest_source / "rapport.pdf",
                title="Köad rapport",
                text="Text från kö.",
            )
            archive = Archive(config.archive_root)

            result = process_worker_cycle(archive, config)

            self.assertTrue(result.did_work)
            documents = archive.list_documents()
            self.assertEqual(len(documents), 1)
            self.assertEqual(documents[0].title, "Köad rapport")
            self.assertEqual(inspect_ingest_queue(config.ingest_source).pending, 0)
            self.assertEqual(
                [row["title"] for row in list_indexed_documents(config.runtime_root)],
                ["Köad rapport"],
            )

    def test_worker_cycle_failed_ingest_item_does_not_block_next_pdf(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _config(root)
            config.ingest_source.mkdir(parents=True)
            (config.ingest_source / "bad.pdf").write_bytes(b"not a pdf")
            write_realistic_text_array_pdf(
                config.ingest_source / "good.pdf",
                title="Efter fel",
                text="Denna går igenom.",
            )
            archive = Archive(config.archive_root)

            result = process_worker_cycle(archive, config)

            self.assertEqual(len(result.ingest_results), 2)
            self.assertEqual(len(archive.list_documents()), 1)
            self.assertEqual(archive.list_documents()[0].title, "Efter fel")
            self.assertFalse((config.ingest_source / "bad.pdf").exists())
            self.assertTrue((config.ingest_source / "failed" / "bad.pdf").exists())
            self.assertEqual(inspect_ingest_queue(config.ingest_source).failed, 1)

    def test_worker_runs_planned_ai_job_to_completed(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            archive, document = _archive_with_pdf_document(root)
            config = _config(root)
            app = CaptureApp(archive, config=config, ai_provider=EmptyAiProvider())
            run = app.enqueue_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            result = process_worker_cycle(
                archive,
                config,
                run_next_ai_job=app.run_next_planned_ai_analysis,
            )

            self.assertEqual(result.ai_run_id, run.id)
            self.assertEqual(archive.get_ai_run(run.id).status, "completed")

    def test_worker_marks_failed_ai_job_persistently(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            archive, document = _archive_with_pdf_document(root)
            config = _config(root)
            app = CaptureApp(archive, config=config, ai_provider=FailingAiProvider())
            run = app.enqueue_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            with self.assertRaises(AiProviderError):
                process_worker_cycle(
                    archive,
                    config,
                    run_next_ai_job=app.run_next_planned_ai_analysis,
                )

            loaded = Archive(config.archive_root).get_ai_run(run.id)
            self.assertEqual(loaded.status, "failed")
            self.assertIn("simulerat AI-fel", loaded.error)

    def test_interrupted_running_ai_run_is_recovered_as_failed(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            archive, document = _archive_with_pdf_document(root)
            config = _config(root)
            app = CaptureApp(archive, config=config, ai_provider=EmptyAiProvider())
            run = app.enqueue_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")
            archive.save_ai_run(run.running())

            recovered = app.recover_interrupted_ai_runs()

            self.assertEqual(recovered, (run.id,))
            loaded = Archive(config.archive_root).get_ai_run(run.id)
            self.assertEqual(loaded.status, "failed")
            self.assertIn("avbröts", loaded.error)


def _config(root: Path) -> AppConfig:
    return AppConfig(
        archive_root=root / "archive",
        runtime_root=root / "runtime",
        ingest_source=root / "ingest",
        ai_provider="mock",
        encrypted_secrets_path=root / "secrets.enc",
        secrets_path=root / "secrets.toml",
    )


def _archive_with_pdf_document(root: Path) -> tuple[Archive, object]:
    archive = Archive(root / "archive")
    pdf_path = root / "rapport.pdf"
    write_minimal_pdf(pdf_path, title="AI rapport", text="Text för AI.")
    document = archive.register_document_with_original_pdf(
        original_path=pdf_path,
        title="AI rapport",
        text="Text för AI.",
        checksum_sha256=calculate_checksum(pdf_path),
    )
    return archive, document


if __name__ == "__main__":
    unittest.main()
