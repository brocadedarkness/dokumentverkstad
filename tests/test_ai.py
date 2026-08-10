from __future__ import annotations

import os
from pathlib import Path
import unittest

from dokumentverkstad.ai import (
    AiAnalysisResult,
    AiProvider,
    AiProviderError,
    AiUsage,
    MockAiProvider,
    estimate_cost,
    estimate_input_tokens,
)
from dokumentverkstad.archive import Archive
from dokumentverkstad.ingest import calculate_checksum
from dokumentverkstad.secrets import load_openai_api_key
from dokumentverkstad.web import CaptureApp
from helpers import workspace_tempdir, write_minimal_pdf


class FailingAiProvider(AiProvider):
    name = "mock"

    def analyze_document(
        self,
        title: str,
        text: str,
        projects: tuple[tuple[str, str], ...],
        model: str,
    ) -> AiAnalysisResult:
        raise AiProviderError("simulerat AI-fel")


class AiTests(unittest.TestCase):
    def test_mock_provider_returns_structured_candidates_and_usage(self) -> None:
        provider = MockAiProvider()

        result = provider.analyze_document(
            title="Rapport",
            text="Detta är en maskinläsbar rapport.",
            projects=(("project_1", "Institutioner"),),
            model="mock-model",
        )

        self.assertGreaterEqual(len(result.candidates), 4)
        self.assertEqual(result.candidates[0].capability, "summary")
        self.assertGreater(result.usage.input_tokens, 0)
        self.assertGreater(result.usage.output_tokens, 0)

    def test_secrets_loader_prefers_environment_over_file(self) -> None:
        with workspace_tempdir() as tmp:
            secrets_path = Path(tmp) / ".dokumentverkstad" / "secrets.toml"
            secrets_path.parent.mkdir()
            secrets_path.write_text('[openai]\napi_key = "file-key"\n', encoding="utf-8")
            previous = os.environ.get("OPENAI_API_KEY")
            os.environ["OPENAI_API_KEY"] = "env-key"
            try:
                key = load_openai_api_key(secrets_path)
            finally:
                if previous is None:
                    os.environ.pop("OPENAI_API_KEY", None)
                else:
                    os.environ["OPENAI_API_KEY"] = previous

            self.assertEqual(key, "env-key")

    def test_secrets_loader_reads_local_file_when_environment_is_missing(self) -> None:
        with workspace_tempdir() as tmp:
            secrets_path = Path(tmp) / ".dokumentverkstad" / "secrets.toml"
            secrets_path.parent.mkdir()
            secrets_path.write_text('[openai]\napi_key = "file-key"\n', encoding="utf-8")
            previous = os.environ.pop("OPENAI_API_KEY", None)
            try:
                key = load_openai_api_key(secrets_path)
            finally:
                if previous is not None:
                    os.environ["OPENAI_API_KEY"] = previous

            self.assertEqual(key, "file-key")

    def test_system_works_without_api_key_and_does_not_expose_key(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            app = CaptureApp(archive)

            html = app.render_inbox()

            self.assertIn("Inbox", html)
            self.assertNotIn("OPENAI_API_KEY", html)
            self.assertNotIn("api_key", html)

    def test_missing_api_key_is_reported_without_exposing_secret_values(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            secrets_path = Path(tmp) / ".dokumentverkstad" / "secrets.toml"
            secrets_path.parent.mkdir()
            secrets_path.write_text(
                '[openai]\napi_key = "super-secret-key"\n', encoding="utf-8"
            )
            app = CaptureApp(archive)
            app.secrets_path = Path(tmp) / "missing-secrets.toml"

            previous = os.environ.pop("OPENAI_API_KEY", None)
            try:
                html = app.render_document_ai_confirmation(document.id)
            finally:
                if previous is not None:
                    os.environ["OPENAI_API_KEY"] = previous

            self.assertIn("Ingen OpenAI API-nyckel", html)
            self.assertNotIn("super-secret-key", html)

    def test_cost_estimate_uses_local_token_estimate(self) -> None:
        input_tokens = estimate_input_tokens("abcd" * 100)
        estimate = estimate_cost(input_tokens=input_tokens, output_tokens=100)

        self.assertEqual(input_tokens, 100)
        self.assertGreater(estimate.estimated_cost, 0)
        self.assertEqual(estimate.currency, "USD")

    def test_ai_does_not_run_without_explicit_confirmation(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            app = CaptureApp(archive, ai_provider=MockAiProvider())

            with self.assertRaises(AiProviderError):
                app.run_document_ai_analysis_from_form(document.id, b"")

            self.assertEqual(archive.list_ai_candidates_for_inbox(), [])

    def test_ai_run_creates_candidates_with_provenance_and_usage(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            app = CaptureApp(archive, ai_provider=MockAiProvider())

            run = app.run_document_ai_analysis_from_form(
                document.id, b"confirm_ai=yes"
            )

            loaded_run = archive.get_ai_run(run.id)
            candidates = archive.list_ai_candidates_for_inbox()
            self.assertEqual(loaded_run.status, "completed")
            self.assertGreater(loaded_run.actual_input_tokens, 0)
            self.assertGreater(loaded_run.actual_cost, 0)
            self.assertGreaterEqual(len(candidates), 4)
            self.assertEqual(candidates[0].creator, "ai")
            self.assertEqual(candidates[0].review_status, "candidate")
            self.assertEqual(candidates[0].ai_provider, "mock")
            self.assertEqual(candidates[0].document_id, document.id)

    def test_ai_candidates_are_shown_in_inbox(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            app = CaptureApp(archive, ai_provider=MockAiProvider())
            app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            html = app.render_inbox()

            self.assertIn("AI-kandidater", html)
            self.assertIn("Proveniens: AI", html)
            self.assertIn("Acceptera", html)

    def test_pending_ai_candidates_are_not_listed_as_capture_notes(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            app = CaptureApp(archive, ai_provider=MockAiProvider())
            app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            html = app.render_capture()

            self.assertNotIn("Kort sammanfattning av Digital rapport.", html)

    def test_accepting_edited_candidate_preserves_original_suggestion(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            app = CaptureApp(archive, ai_provider=MockAiProvider())
            app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")
            candidate = archive.list_ai_candidates_for_inbox()[0]

            app.review_ai_candidate_from_form(
                candidate.id,
                "decision=accept&content=Anv%C3%A4ndarens+version".encode("utf-8"),
            )

            reviewed = archive.get_knowledge_object(candidate.id)
            self.assertEqual(reviewed.review_status, "accepted")
            self.assertEqual(reviewed.content, "Användarens version")
            self.assertEqual(reviewed.accepted_content, "Användarens version")
            self.assertEqual(reviewed.original_content, candidate.original_content)
            self.assertEqual(reviewed.creator, "user_after_ai")

    def test_reject_and_later_review_decisions_are_persistent(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            app = CaptureApp(archive, ai_provider=MockAiProvider())
            app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")
            first, second = archive.list_ai_candidates_for_inbox()[:2]

            app.review_ai_candidate_from_form(
                first.id,
                "decision=reject&rejection_reason=felaktig".encode("utf-8"),
            )
            app.review_ai_candidate_from_form(second.id, b"decision=later")

            restarted = Archive(Path(tmp) / "archive")
            self.assertEqual(
                restarted.get_knowledge_object(first.id).rejection_reason,
                "felaktig",
            )
            self.assertEqual(
                restarted.get_knowledge_object(second.id).review_status,
                "later",
            )

    def test_ai_error_leaves_archive_consistent(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            app = CaptureApp(archive, ai_provider=FailingAiProvider())

            with self.assertRaises(AiProviderError):
                app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            self.assertEqual(archive.list_ai_candidates_for_inbox(), [])
            runs = archive.list_ai_runs_for_document(document.id)
            self.assertEqual(runs[0].status, "failed")
            self.assertEqual(archive.get_document(document.id).title, "Digital rapport")

    def test_document_without_extracted_text_is_reported_clearly(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Fysisk bok")
            app = CaptureApp(archive, ai_provider=MockAiProvider())

            html = app.render_document_ai_confirmation(document.id)

            self.assertIn("saknar extraherad text", html)


def _archive_with_pdf_document(root: Path) -> tuple[Archive, object]:
    archive = Archive(root / "archive")
    pdf_path = root / "rapport.pdf"
    write_minimal_pdf(
        pdf_path,
        title="Digital rapport",
        text="Detta är en maskinläsbar rapport med flera påståenden.",
    )
    document = archive.register_document_with_original_pdf(
        original_path=pdf_path,
        title="Digital rapport",
        text="Detta är en maskinläsbar rapport med flera påståenden.",
        checksum_sha256=calculate_checksum(pdf_path),
    )
    return archive, document


if __name__ == "__main__":
    unittest.main()
