from __future__ import annotations

from pathlib import Path
import shutil
import unittest

from dokumentverkstad.ai import AiRunRecord
from dokumentverkstad.archive import Archive
from dokumentverkstad.config import AppConfig
from dokumentverkstad.index import rebuild_document_index
from dokumentverkstad.statistics import build_ai_statistics
from dokumentverkstad.web import CaptureApp
from helpers import workspace_tempdir


class StatisticsTest(unittest.TestCase):
    def test_ai_usage_cost_and_tokens_are_summed_from_completed_runs(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            _save_run(
                archive,
                run_id="airun_one",
                model="model-a",
                prompt_version="prompt-a",
                input_tokens=100,
                output_tokens=20,
                cost=0.001,
            )
            _save_run(
                archive,
                run_id="airun_two",
                model="model-a",
                prompt_version="prompt-b",
                input_tokens=200,
                output_tokens=30,
                cost=0.002,
            )
            _save_run(
                archive,
                run_id="airun_three",
                model="model-b",
                prompt_version="prompt-a",
                input_tokens=300,
                output_tokens=40,
                cost=0.003,
            )
            _save_run(
                archive,
                run_id="airun_failed",
                model="model-a",
                prompt_version="prompt-a",
                input_tokens=999,
                output_tokens=999,
                cost=9,
                status="failed",
            )

            statistics = build_ai_statistics(archive)

            self.assertEqual(statistics.completed_runs, 3)
            self.assertEqual(statistics.total_usage.input_tokens, 600)
            self.assertEqual(statistics.total_usage.output_tokens, 90)
            self.assertEqual(statistics.total_usage.cost, 0.006)
            self.assertEqual(statistics.usage_by_model["model-a"].cost, 0.003)
            self.assertEqual(statistics.usage_by_model["model-b"].input_tokens, 300)
            self.assertEqual(statistics.usage_by_prompt_version["prompt-a"].runs, 2)
            self.assertEqual(statistics.usage_by_prompt_version["prompt-b"].runs, 1)
            self.assertEqual(statistics.usage_by_month["2026-01"].runs, 3)

    def test_review_statistics_are_grouped_by_candidate_type(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Dokument")
            claim = _create_candidate(archive, document.id, "Claim", "Original claim")
            edited = _create_candidate(archive, document.id, "Claim", "Original edited")
            rejected = _create_candidate(archive, document.id, "Insight", "Svag insikt")
            later = _create_candidate(archive, document.id, "Question", "Fråga")
            handled = _create_candidate(
                archive,
                document.id,
                "ProjectSuggestion",
                "Koppla projekt",
            )
            archive.review_knowledge_candidate(claim.id, "accepted", content="Original claim")
            archive.review_knowledge_candidate(edited.id, "accepted", content="Redigerad")
            archive.review_knowledge_candidate(
                rejected.id, "rejected", rejection_reason="irrelevant"
            )
            archive.review_knowledge_candidate(later.id, "later")
            archive.review_knowledge_candidate(handled.id, "handled")

            statistics = build_ai_statistics(archive)

            self.assertEqual(statistics.candidate_reviews.total, 5)
            self.assertEqual(statistics.candidate_reviews.accepted, 2)
            self.assertEqual(statistics.candidate_reviews.edited_accepted, 1)
            self.assertEqual(statistics.candidate_reviews.rejected, 1)
            self.assertEqual(statistics.candidate_reviews.later, 1)
            self.assertEqual(statistics.candidate_reviews.handled, 1)
            self.assertEqual(statistics.review_by_candidate_type["Claim"].accepted, 2)
            self.assertEqual(
                statistics.review_by_candidate_type["Claim"].edited_accepted, 1
            )
            self.assertEqual(statistics.review_by_candidate_type["Insight"].rejected, 1)
            self.assertEqual(statistics.rejection_reasons["irrelevant"], 1)

    def test_statistics_are_rebuilt_from_archive_after_new_archive_instance(self) -> None:
        with workspace_tempdir() as tmp:
            archive_root = Path(tmp) / "archive"
            runtime_root = Path(tmp) / "runtime"
            runtime_root.mkdir()
            archive = Archive(archive_root)
            _save_run(
                archive,
                run_id="airun_one",
                model="model-a",
                prompt_version="prompt-a",
                input_tokens=10,
                output_tokens=5,
                cost=0.0001,
            )
            document = archive.create_document("Dokument")
            candidate = _create_candidate(archive, document.id, "Summary", "Sammanfattning")
            archive.review_knowledge_candidate(candidate.id, "accepted")

            shutil.rmtree(runtime_root)
            rebuilt_archive = Archive(archive_root)
            statistics = build_ai_statistics(rebuilt_archive)

            self.assertEqual(statistics.completed_runs, 1)
            self.assertEqual(statistics.total_usage.cost, 0.0001)
            self.assertEqual(statistics.review_by_candidate_type["Summary"].accepted, 1)

    def test_admin_view_handles_empty_archive(self) -> None:
        with workspace_tempdir() as tmp:
            app = CaptureApp(Archive(Path(tmp) / "archive"))

            html = app.render_admin()

            self.assertIn("Ingen AI-användning ännu.", html)
            self.assertIn("Genomförda AI-körningar", html)
            self.assertIn("0.000000 USD", html)

    def test_admin_view_includes_small_health_section_when_configured(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            archive = Archive(root / "archive")
            archive.create_document("Drift")
            config = AppConfig(
                archive_root=root / "archive",
                runtime_root=root / "runtime",
                ingest_source=root / "ingest",
                encrypted_secrets_path=root / "secrets.enc",
                secrets_path=root / "secrets.toml",
            )
            rebuild_document_index(archive, config.runtime_root)
            app = CaptureApp(archive, config=config)

            html = app.render_admin()

            self.assertIn("Driftstatus", html)
            self.assertIn("<dd>ok</dd>", html)
            self.assertIn("OpenAI credential", html)
            self.assertIn("saknas (AI är valfritt)", html)

    def test_admin_view_renders_multiple_models_and_prompt_versions(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            _save_run(
                archive,
                run_id="airun_one",
                model="model-a",
                prompt_version="prompt-a",
                input_tokens=10,
                output_tokens=5,
                cost=0.0001,
            )
            _save_run(
                archive,
                run_id="airun_two",
                model="model-b",
                prompt_version="prompt-b",
                input_tokens=20,
                output_tokens=10,
                cost=0.0002,
            )
            app = CaptureApp(archive)

            html = app.render_admin()

            self.assertIn("model-a", html)
            self.assertIn("model-b", html)
            self.assertIn("prompt-a", html)
            self.assertIn("prompt-b", html)
            self.assertIn("0.000300 USD", html)


def _save_run(
    archive: Archive,
    run_id: str,
    model: str,
    prompt_version: str,
    input_tokens: int,
    output_tokens: int,
    cost: float,
    status: str = "completed",
) -> None:
    archive.save_ai_run(
        AiRunRecord(
            id=run_id,
            document_id="doc_stats",
            provider="mock",
            model=model,
            prompt_version=prompt_version,
            capabilities=("summary",),
            created_at="2026-01-15T12:00:00+00:00",
            status=status,
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            estimated_cost=cost,
            actual_input_tokens=input_tokens,
            actual_output_tokens=output_tokens,
            actual_cost=cost,
            currency="USD",
        )
    )


def _create_candidate(
    archive: Archive, document_id: str, semantic_type: str, content: str
):
    return archive.create_ai_candidate(
        content=content,
        ai_run_id="airun_stats",
        ai_provider="mock",
        ai_model="model-a",
        prompt_version="prompt-a",
        capability=semantic_type,
        document_id=document_id,
        confidence="medel",
        semantic_type=semantic_type,
    )


if __name__ == "__main__":
    unittest.main()
