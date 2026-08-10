from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace
import unittest

from dokumentverkstad.ai import (
    AiAnalysisResult,
    AiCandidate,
    AiRunRecord,
    AiProvider,
    AiProviderError,
    AiUsage,
    AI_CAPABILITIES,
    DEFAULT_MAX_OUTPUT_TOKENS,
    LONG_CONTEXT_INPUT_TOKEN_THRESHOLD,
    InvalidAiResultError,
    MockAiProvider,
    _analysis_result_from_openai_response,
    _response_format_schema,
    estimate_cost,
    estimate_input_tokens,
)
from dokumentverkstad.archive import Archive
from dokumentverkstad.config import AppConfig
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
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> AiAnalysisResult:
        raise AiProviderError("simulerat AI-fel")


class InvalidStructuredAiProvider(AiProvider):
    name = "mock"

    def analyze_document(
        self,
        title: str,
        text: str,
        projects: tuple[tuple[str, str], ...],
        model: str,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> AiAnalysisResult:
        return _analysis_result_from_openai_response(
            SimpleNamespace(
                status="completed",
                output_text=json.dumps({"summary": {"content": "Ofullständigt"}}),
                output=[],
                usage=SimpleNamespace(input_tokens=10, output_tokens=10),
            )
        )


class ProjectSuggestionProvider(AiProvider):
    name = "mock"

    def __init__(self, suggestion: AiCandidate):
        self.suggestion = suggestion

    def analyze_document(
        self,
        title: str,
        text: str,
        projects: tuple[tuple[str, str], ...],
        model: str,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> AiAnalysisResult:
        return AiAnalysisResult(
            candidates=(self.suggestion,),
            usage=AiUsage(input_tokens=10, output_tokens=10),
        )


class RecordingAiProvider(AiProvider):
    name = "mock"

    def __init__(self) -> None:
        self.max_output_tokens = 0

    def analyze_document(
        self,
        title: str,
        text: str,
        projects: tuple[tuple[str, str], ...],
        model: str,
        max_output_tokens: int = DEFAULT_MAX_OUTPUT_TOKENS,
    ) -> AiAnalysisResult:
        self.max_output_tokens = max_output_tokens
        return AiAnalysisResult(
            candidates=(AiCandidate("summary", "Sammanfattning", "medel"),),
            usage=AiUsage(input_tokens=10, output_tokens=10),
        )


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

    def test_openai_response_format_uses_explicit_json_schema(self) -> None:
        response_format = _response_format_schema()
        schema = response_format["schema"]

        self.assertEqual(response_format["type"], "json_schema")
        self.assertTrue(response_format["strict"])
        self.assertEqual(response_format["name"], "document_analysis")
        self.assertEqual(
            schema["required"],
            [
                "summary",
                "candidate_insights",
                "candidate_claims",
                "candidate_questions",
                "project_suggestions",
            ],
        )

    def test_openai_structured_output_parser_accepts_valid_payload(self) -> None:
        response = SimpleNamespace(
            status="completed",
            output_text=json.dumps(_valid_structured_payload()),
            output=[],
            usage=SimpleNamespace(input_tokens=123, output_tokens=45),
        )

        result = _analysis_result_from_openai_response(response)

        self.assertEqual(result.usage.input_tokens, 123)
        self.assertEqual(result.usage.output_tokens, 45)
        self.assertEqual(
            [candidate.capability for candidate in result.candidates],
            [
                "summary",
                "candidate_insight",
                "candidate_claim",
                "candidate_question",
                "project_suggestion",
            ],
        )
        self.assertEqual(result.candidates[-1].project_id, "project_1")

    def test_openai_structured_output_parser_rejects_schema_errors(self) -> None:
        response = SimpleNamespace(
            status="completed",
            output_text=json.dumps({"summary": {"content": "Saknar confidence"}}),
            output=[],
            usage=SimpleNamespace(input_tokens=1, output_tokens=1),
        )

        with self.assertRaises(InvalidAiResultError):
            _analysis_result_from_openai_response(response)

    def test_openai_refusal_is_reported_without_json_error(self) -> None:
        response = SimpleNamespace(
            status="completed",
            output_text="",
            output=[
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "refusal",
                            "refusal": "Kan inte hjälpa med detta.",
                        }
                    ],
                }
            ],
            usage=None,
        )

        with self.assertRaisesRegex(AiProviderError, "avböjde"):
            _analysis_result_from_openai_response(response)

    def test_openai_incomplete_response_is_reported_without_json_error(self) -> None:
        response = SimpleNamespace(
            status="incomplete",
            incomplete_details=SimpleNamespace(reason="max_output_tokens"),
            output_text="",
            output=[],
            usage=None,
        )

        with self.assertRaisesRegex(AiProviderError, "ofullständigt"):
            _analysis_result_from_openai_response(response)

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
        self.assertEqual(estimate.estimated_cost, 0.00014)
        self.assertEqual(estimate.currency, "USD")
        self.assertEqual(
            estimate.method, "estimated_tokens_x_configured_price_short_context"
        )

    def test_default_max_output_tokens_is_used_in_cost_estimate(self) -> None:
        estimate = estimate_cost(input_tokens=100)

        self.assertEqual(DEFAULT_MAX_OUTPUT_TOKENS, 6000)
        self.assertEqual(estimate.output_tokens, 6000)

    def test_configured_max_output_tokens_is_used_for_estimate_run_and_provider(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            archive, document = _archive_with_pdf_document(root)
            provider = RecordingAiProvider()
            app = CaptureApp(
                archive,
                config=AppConfig(
                    archive_root=root / "archive",
                    runtime_root=root / "runtime",
                    ingest_source=root / "ingest",
                    ai_provider="mock",
                    ai_max_output_tokens=4321,
                ),
                ai_provider=provider,
            )

            estimate_html = app.render_document_ai_confirmation(document.id)
            run = app.run_document_ai_analysis_from_form(
                document.id, b"confirm_ai=yes"
            )

            self.assertIn("<dd>4321</dd>", estimate_html)
            self.assertEqual(run.estimated_output_tokens, 4321)
            self.assertEqual(
                run.estimated_cost,
                estimate_cost(
                    estimate_input_tokens(
                        archive.extracted_text_file_path(document.id).read_text(
                            encoding="utf-8"
                        )
                    ),
                    output_tokens=4321,
                ).estimated_cost,
            )
            self.assertEqual(provider.max_output_tokens, 4321)

    def test_cost_estimate_uses_long_context_prices_above_threshold(self) -> None:
        estimate = estimate_cost(
            input_tokens=LONG_CONTEXT_INPUT_TOKEN_THRESHOLD + 1,
            output_tokens=100,
        )

        self.assertEqual(estimate.estimated_cost, 0.10898)
        self.assertEqual(
            estimate.method, "estimated_tokens_x_configured_price_long_context"
        )

    def test_completed_run_uses_same_pricing_logic_as_estimate(self) -> None:
        planned = AiRunRecord.create(
            document_id="doc_1",
            provider="mock",
            model="gpt-5.6-luna",
            capabilities=AI_CAPABILITIES,
            estimate=estimate_cost(input_tokens=10, output_tokens=10),
        )
        usage = AiUsage(
            input_tokens=LONG_CONTEXT_INPUT_TOKEN_THRESHOLD + 1,
            output_tokens=100,
        )

        completed = planned.completed(usage, candidate_ids=())

        self.assertEqual(
            completed.actual_cost,
            estimate_cost(usage.input_tokens, usage.output_tokens).estimated_cost,
        )

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

    def test_project_suggestions_keep_project_id_and_skip_existing_links(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            project = archive.create_project("Relevant projekt")
            app = CaptureApp(archive, ai_provider=MockAiProvider())

            app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            candidates = archive.list_ai_candidates_for_inbox()
            suggestions = [
                candidate
                for candidate in candidates
                if candidate.semantic_type == "ProjectSuggestion"
            ]
            self.assertEqual(len(suggestions), 1)
            self.assertEqual(suggestions[0].project_ids, (project.id,))

        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            project = archive.create_project("Relevant projekt")
            archive.set_document_projects(document.id, (project.id,))
            app = CaptureApp(archive, ai_provider=MockAiProvider())

            app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            candidates = archive.list_ai_candidates_for_inbox()
            suggestions = [
                candidate
                for candidate in candidates
                if candidate.semantic_type == "ProjectSuggestion"
            ]
            self.assertEqual(suggestions, [])

    def test_project_suggestion_can_resolve_existing_project_by_name(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            project = archive.create_project("Relevant projekt")
            provider = ProjectSuggestionProvider(
                AiCandidate(
                    "project_suggestion",
                    "Koppla dokumentet till Relevant projekt.",
                    "medel",
                    project_id="",
                    project_name="Relevant projekt",
                )
            )
            app = CaptureApp(archive, ai_provider=provider)

            app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            suggestions = [
                candidate
                for candidate in archive.list_ai_candidates_for_inbox()
                if candidate.semantic_type == "ProjectSuggestion"
            ]
            self.assertEqual(len(suggestions), 1)
            self.assertEqual(suggestions[0].project_ids, (project.id,))

    def test_unknown_project_suggestion_is_not_saved_as_actionable_candidate(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            archive.create_project("Relevant projekt")
            provider = ProjectSuggestionProvider(
                AiCandidate(
                    "project_suggestion",
                    "Koppla dokumentet till Okänt projekt.",
                    "medel",
                    project_id="missing_project",
                    project_name="Okänt projekt",
                )
            )
            app = CaptureApp(archive, ai_provider=provider)

            app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            self.assertEqual(archive.list_ai_candidates_for_inbox(), [])

    def test_ai_candidates_are_shown_in_inbox(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            app = CaptureApp(archive, ai_provider=MockAiProvider())
            app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            html = app.render_inbox()

            self.assertIn("AI-review", html)
            self.assertIn("väntar", html)
            self.assertIn(f"/documents/{document.id}", html)
            self.assertNotIn("Proveniens: AI", html)
            self.assertNotIn("Acceptera", html)

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

    def test_invalid_ai_result_does_not_create_candidates(self) -> None:
        with workspace_tempdir() as tmp:
            archive, document = _archive_with_pdf_document(Path(tmp))
            app = CaptureApp(archive, ai_provider=InvalidStructuredAiProvider())

            with self.assertRaises(InvalidAiResultError):
                app.run_document_ai_analysis_from_form(document.id, b"confirm_ai=yes")

            self.assertEqual(archive.list_ai_candidates_for_inbox(), [])
            runs = archive.list_ai_runs_for_document(document.id)
            self.assertEqual(runs[0].status, "failed")

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


def _valid_structured_payload() -> dict[str, object]:
    return {
        "summary": {"content": "Kort sammanfattning.", "confidence": "medel"},
        "candidate_insights": [
            {"content": "Ett möjligt tema.", "confidence": "medel"}
        ],
        "candidate_claims": [
            {"content": "Ett centralt påstående.", "confidence": "hög"}
        ],
        "candidate_questions": [
            {"content": "Vad behöver undersökas?", "confidence": "låg"}
        ],
        "project_suggestions": [
            {
                "content": "Relevant för projektet.",
                "confidence": "låg",
                "project_id": "project_1",
                "project_name": "Institutioner",
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
