from __future__ import annotations

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import threading
import unittest
from pathlib import Path

from dokumentverkstad.ai import AiProvider, AiProviderError, AiRunRecord
from dokumentverkstad.archive import Archive
from dokumentverkstad.config import AppConfig
from dokumentverkstad.index import list_indexed_documents
from dokumentverkstad.ingest import calculate_checksum
from dokumentverkstad.web import CaptureApp, make_handler
from helpers import workspace_tempdir, write_minimal_pdf


def _get(server: ThreadingHTTPServer, path: str) -> str:
    connection = HTTPConnection(server.server_address[0], server.server_address[1])
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
    finally:
        connection.close()

    if response.status != 200:
        raise AssertionError(f"GET {path} returned {response.status}: {body}")
    return body


def _get_with_headers(
    server: ThreadingHTTPServer, path: str
) -> tuple[int, dict[str, str], str]:
    connection = HTTPConnection(server.server_address[0], server.server_address[1])
    try:
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read().decode("utf-8")
        headers = {key.lower(): value for key, value in response.getheaders()}
    finally:
        connection.close()
    return response.status, headers, body


def _post(server: ThreadingHTTPServer, path: str, body: str) -> tuple[int, str]:
    connection = HTTPConnection(server.server_address[0], server.server_address[1])
    try:
        connection.request(
            "POST",
            path,
            body=body.encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response = connection.getresponse()
        response_body = response.read().decode("utf-8")
        location = response.getheader("Location", "")
    finally:
        connection.close()
    return response.status, location or response_body


def _post_multipart_pdf(
    server: ThreadingHTTPServer,
    path: str,
    filename: str,
    content: bytes,
) -> tuple[int, str]:
    boundary = "----dokumentverkstad-test-boundary"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="pdf"; filename="{filename}"\r\n'
        "Content-Type: application/pdf\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("ascii")
    connection = HTTPConnection(server.server_address[0], server.server_address[1])
    try:
        connection.request(
            "POST",
            path,
            body=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        response = connection.getresponse()
        response_body = response.read().decode("utf-8")
    finally:
        connection.close()
    return response.status, response_body


class CaptureAppTests(unittest.TestCase):
    def test_first_run_routes_are_navigable_before_any_object_exists(self) -> None:
        with workspace_tempdir() as tmp:
            archive_root = Path(tmp) / "archive"
            app = CaptureApp(Archive(archive_root))
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                root_html = _get(server, "/")
                documents_html = _get(server, "/documents")
                projects_html = _get(server, "/projects")
                admin_html = _get(server, "/admin")
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertIn('href="/documents"', root_html)
            self.assertIn('href="/projects"', root_html)
            self.assertIn("Inga dokument ännu.", documents_html)
            self.assertIn("Inga projekt ännu.", projects_html)
            self.assertIn("Administration", admin_html)
            self.assertTrue((archive_root / "documents").is_dir())
            self.assertTrue((archive_root / "projects").is_dir())
            self.assertTrue((archive_root / "knowledge").is_dir())

    def test_empty_inbox_has_clear_empty_state(self) -> None:
        with workspace_tempdir() as tmp:
            app = CaptureApp(Archive(Path(tmp) / "archive"))

            html = app.render_inbox()

            self.assertIn("Inbox är tom.", html)
            self.assertIn("Trash", html)
            self.assertEqual(html.count("data-ai-inbox-document-id="), 0)

    def test_new_document_appears_in_inbox_and_can_be_opened(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Nytt dokument")
            app = CaptureApp(archive)

            html = app.render_inbox()

            self.assertIn("Nytt dokument", html)
            self.assertIn(f"/documents/{document.id}", html)

    def test_inbox_document_shows_original_filename_when_available(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            archive = Archive(root / "archive")
            pdf_path = root / "rapport.pdf"
            write_minimal_pdf(pdf_path, title="Svår metadata")
            document = archive.register_document_with_original_pdf(
                original_path=pdf_path,
                title="Svår metadata",
                text="Extraherad text",
                checksum_sha256=calculate_checksum(pdf_path),
            )
            app = CaptureApp(archive)

            html = app.render_inbox()

            self.assertIn("Svår metadata", html)
            self.assertIn("Originalfil: rapport.pdf", html)
            self.assertIn(f"/documents/{document.id}", html)

    def test_inbox_document_can_be_linked_to_multiple_projects_and_marked_done(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("North")
            first_project = archive.create_project("Rävfilosofi")
            second_project = archive.create_project("Institutioner")
            app = CaptureApp(archive)

            app.update_inbox_document_from_form(
                document.id,
                (
                    f"project_id={first_project.id}&project_id={second_project.id}"
                    "&decision=done"
                ).encode("utf-8"),
            )

            updated = archive.get_document(document.id)
            self.assertEqual(
                updated.project_ids, (first_project.id, second_project.id)
            )
            self.assertEqual(updated.inbox_status, "done")
            self.assertEqual(archive.list_inbox_documents(), [])

    def test_inbox_later_trash_and_restore_flow_over_http(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Väntande dokument")
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, location = _post(
                    server,
                    f"/inbox/documents/{document.id}",
                    "decision=later",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, "/inbox")
                self.assertEqual(archive.get_document(document.id).inbox_status, "later")

                status, location = _post(
                    server,
                    f"/inbox/documents/{document.id}",
                    "decision=trashed",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, "/inbox")
                self.assertIn("Väntande dokument", _get(server, "/trash"))

                status, location = _post(
                    server,
                    f"/trash/documents/{document.id}/restore",
                    "",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, "/trash")
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(archive.get_document(document.id).inbox_status, "new")

    def test_trash_view_identifies_documents_and_delete_requires_confirmation(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Slängd rapport", author="KB", year="2024")
            archive.set_document_inbox_status(document.id, "trashed")
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                html = _get(server, "/trash")
                self.assertIn("Document", html)
                self.assertIn("Slängd rapport", html)
                self.assertIn("KB | 2024", html)
                self.assertNotIn(f">{document.id}<", html)

                status, _ = _post(
                    server,
                    f"/trash/documents/{document.id}/delete",
                    "",
                )
                self.assertEqual(status, 400)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(archive.get_document(document.id).inbox_status, "trashed")

    def test_restore_from_trash_preserves_history_and_does_not_duplicate(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Historik")
            note = archive.create_knowledge_object("Gammal", document_id=document.id)
            archive.update_knowledge_object(note.id, "Ny")
            archive.set_document_inbox_status(document.id, "trashed")
            app = CaptureApp(archive)

            app.archive.restore_document(document.id)

            self.assertEqual(len(archive.list_documents()), 1)
            restored_note = archive.get_knowledge_object(note.id)
            self.assertEqual(restored_note.content, "Ny")
            self.assertEqual(restored_note.history[0].content, "Gammal")

    def test_permanent_delete_over_http_blocks_referenced_documents(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Refererat")
            archive.create_knowledge_object("Notering", document_id=document.id)
            archive.set_document_inbox_status(document.id, "trashed")
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                html = _get(server, "/trash")
                self.assertIn("Permanent radering spärrad", html)
                status, _ = _post(
                    server,
                    f"/trash/documents/{document.id}/delete",
                    "confirm_delete=yes",
                )
                self.assertEqual(status, 400)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(archive.get_document(document.id).inbox_status, "trashed")

    def test_permanent_delete_over_http_removes_unreferenced_trashed_document(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Orefererat")
            archive.set_document_inbox_status(document.id, "trashed")
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, location = _post(
                    server,
                    f"/trash/documents/{document.id}/delete",
                    "confirm_delete=yes",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, "/trash")
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(archive.list_documents(include_trashed=True), [])

    def test_ai_candidate_review_actions_return_http_response_and_persist(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI-dokument")
            suggested_project = archive.create_project("Föreslaget projekt")
            candidates = {
                "summary": _create_ai_candidate(
                    archive, document.id, "Summary", "Ursprunglig summary"
                ),
                "claim": _create_ai_candidate(
                    archive, document.id, "Claim", "Ursprungligt claim"
                ),
                "insight": _create_ai_candidate(
                    archive, document.id, "Insight", "Ursprunglig insight"
                ),
                "question": _create_ai_candidate(
                    archive, document.id, "Question", "Ursprunglig question"
                ),
                "project": _create_ai_candidate(
                    archive,
                    document.id,
                    "ProjectSuggestion",
                    "Ursprungligt projektförslag",
                    project_ids=(suggested_project.id,),
                ),
            }
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                requests = (
                    (
                        candidates["summary"].id,
                        "decision=accept&content=Redigerad+summary",
                    ),
                    (
                        candidates["claim"].id,
                        "decision=accept&content=Ursprungligt+claim",
                    ),
                    (
                        candidates["insight"].id,
                        "decision=reject&rejection_reason=felaktig",
                    ),
                    (candidates["question"].id, "decision=later"),
                    (
                        candidates["project"].id,
                        "decision=link_project",
                    ),
                )
                for candidate_id, body in requests:
                    status, location = _post(
                        server,
                        f"/documents/{document.id}/candidates/{candidate_id}",
                        body,
                    )
                    self.assertEqual(status, 303)
                    self.assertTrue(location.startswith(f"/documents/{document.id}#"))
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            summary = archive.get_knowledge_object(candidates["summary"].id)
            claim = archive.get_knowledge_object(candidates["claim"].id)
            insight = archive.get_knowledge_object(candidates["insight"].id)
            question = archive.get_knowledge_object(candidates["question"].id)
            project_suggestion = archive.get_knowledge_object(candidates["project"].id)

            self.assertEqual(summary.review_status, "accepted")
            self.assertEqual(summary.content, "Redigerad summary")
            self.assertEqual(summary.creator, "user_after_ai")
            self.assertEqual(summary.original_content, "Ursprunglig summary")
            self.assertEqual(summary.accepted_content, "Redigerad summary")
            self.assertEqual(claim.review_status, "accepted")
            self.assertEqual(insight.review_status, "rejected")
            self.assertEqual(insight.rejection_reason, "felaktig")
            self.assertEqual(question.review_status, "later")
            self.assertEqual(project_suggestion.review_status, "handled")
            self.assertEqual(
                archive.get_document(document.id).project_ids,
                (suggested_project.id,),
            )

    def test_ai_review_can_continue_after_summary_without_read_only_detour(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI-dokument")
            summary = _create_ai_candidate(
                archive, document.id, "Summary", "Sammanfattning"
            )
            first_claim = _create_ai_candidate(
                archive, document.id, "Claim", "Första claim"
            )
            second_claim = _create_ai_candidate(
                archive, document.id, "Claim", "Andra claim"
            )
            insight = _create_ai_candidate(archive, document.id, "Insight", "Insikt")
            question = _create_ai_candidate(archive, document.id, "Question", "Fråga")
            ordered_claims = sorted(
                (first_claim, second_claim),
                key=lambda item: (item.created_at, item.id),
            )
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, location = _post(
                    server,
                    f"/documents/{document.id}/candidates/{summary.id}",
                    "decision=accept&content=Sammanfattning",
                )
                self.assertEqual(status, 303)
                self.assertEqual(
                    location,
                    f"/documents/{document.id}#candidate-{ordered_claims[0].id}",
                )

                html = _get(server, f"/documents/{document.id}")
                self.assertNotIn(
                    f'data-ai-review-candidate-id="{summary.id}"', html
                )
                for candidate in (first_claim, second_claim, insight, question):
                    self.assertIn(
                        f'action="/documents/{document.id}/candidates/{candidate.id}"',
                        html,
                    )
                self.assertLess(html.index("Claims"), html.index("Insights"))

                for claim in (first_claim, second_claim):
                    status, location = _post(
                        server,
                        f"/documents/{document.id}/candidates/{claim.id}",
                        f"decision=accept&content={claim.content.replace(' ', '+')}",
                    )
                    self.assertEqual(status, 303)
                    self.assertTrue(location.startswith(f"/documents/{document.id}#"))

                status, location = _post(
                    server,
                    f"/documents/{document.id}/candidates/{insight.id}",
                    "decision=later",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, f"/documents/{document.id}#candidate-{question.id}")

                status, _ = _post(
                    server,
                    f"/documents/{document.id}/candidates/{summary.id}",
                    "decision=reject&rejection_reason=annat",
                )
                self.assertEqual(status, 303)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(archive.get_knowledge_object(summary.id).review_status, "rejected")
            self.assertEqual(
                archive.get_knowledge_object(summary.id).history[-1].review_status,
                "accepted",
            )
            self.assertEqual(
                archive.get_knowledge_object(first_claim.id).review_status, "accepted"
            )
            self.assertEqual(
                archive.get_knowledge_object(second_claim.id).review_status, "accepted"
            )
            self.assertEqual(archive.get_knowledge_object(insight.id).review_status, "later")
            self.assertEqual(archive.get_knowledge_object(question.id).review_status, "candidate")

    def test_ai_review_redirect_targets_next_candidate_by_display_order(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI-dokument")
            project = archive.create_project("Relevant projekt")
            first_claim = _create_ai_candidate(
                archive, document.id, "Claim", "Första claim"
            )
            second_claim = _create_ai_candidate(
                archive, document.id, "Claim", "Andra claim"
            )
            insight = _create_ai_candidate(archive, document.id, "Insight", "Insikt")
            question = _create_ai_candidate(archive, document.id, "Question", "Fråga")
            project_suggestion = _create_ai_candidate(
                archive,
                document.id,
                "ProjectSuggestion",
                "Projektförslag",
                project_ids=(project.id,),
            )
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, location = _post(
                    server,
                    f"/documents/{document.id}/candidates/{first_claim.id}",
                    "decision=accept&content=Första+claim",
                )
                self.assertEqual(status, 303)
                self.assertEqual(
                    location, f"/documents/{document.id}#candidate-{second_claim.id}"
                )

                status, location = _post(
                    server,
                    f"/documents/{document.id}/candidates/{second_claim.id}",
                    "decision=accept&content=Andra+claim",
                )
                self.assertEqual(status, 303)
                self.assertEqual(
                    location, f"/documents/{document.id}#candidate-{insight.id}"
                )

                status, location = _post(
                    server,
                    f"/documents/{document.id}/candidates/{insight.id}",
                    "decision=accept&content=Insikt",
                )
                self.assertEqual(status, 303)
                self.assertEqual(
                    location, f"/documents/{document.id}#candidate-{question.id}"
                )

                status, location = _post(
                    server,
                    f"/documents/{document.id}/candidates/{question.id}",
                    "decision=accept&content=Fråga",
                )
                self.assertEqual(status, 303)
                self.assertEqual(
                    location,
                    f"/documents/{document.id}#candidate-{project_suggestion.id}",
                )

                status, location = _post(
                    server,
                    f"/documents/{document.id}/candidates/{project_suggestion.id}",
                    "decision=reject",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, f"/documents/{document.id}#ai-review")
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

    def test_inbox_ai_review_posts_are_grouped_by_document_and_count_candidates(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            first_document = archive.create_document("Första dokumentet")
            second_document = archive.create_document("Andra dokumentet")
            first = _create_ai_candidate(archive, first_document.id, "Summary", "Ett")
            second = _create_ai_candidate(archive, first_document.id, "Claim", "Två")
            third = _create_ai_candidate(archive, second_document.id, "Insight", "Tre")
            app = CaptureApp(archive)

            html = app.render_inbox()

            self.assertEqual(html.count("data-ai-inbox-document-id="), 2)
            self.assertIn(
                f'data-ai-inbox-document-id="{first_document.id}"',
                html,
            )
            self.assertIn(
                f'data-ai-inbox-document-id="{second_document.id}"',
                html,
            )
            self.assertIn("2 AI-kandidater väntar", html)
            self.assertIn("1 AI-kandidat väntar", html)
            self.assertIn("2 document har obearbetade AI-granskningar.", html)
            self.assertIn(f'href="/documents/{first_document.id}"', html)
            self.assertIn(f'href="/documents/{second_document.id}"', html)
            self.assertNotIn("<textarea", html)
            self.assertNotIn("/candidates/", html)
            self.assertNotIn("data-ai-review-candidate-id=", html)
            self.assertNotIn("Acceptera", html)
            self.assertNotIn("Avvisa", html)

            app.review_ai_candidate_from_form(
                first.id,
                "decision=accept&content=Ett".encode("utf-8"),
            )
            html_after_one_review = app.render_inbox()
            self.assertEqual(
                html_after_one_review.count("data-ai-inbox-document-id="), 2
            )
            self.assertIn("1 AI-kandidat väntar", html_after_one_review)
            self.assertNotIn("2 AI-kandidater väntar", html_after_one_review)

            app.review_ai_candidate_from_form(
                second.id,
                "decision=reject&rejection_reason=annat".encode("utf-8"),
            )
            html_after_first_document_done = app.render_inbox()
            self.assertEqual(
                html_after_first_document_done.count("data-ai-inbox-document-id="), 1
            )
            self.assertNotIn(
                f'data-ai-inbox-document-id="{first_document.id}"',
                html_after_first_document_done,
            )
            self.assertIn(
                f'data-ai-inbox-document-id="{second_document.id}"',
                html_after_first_document_done,
            )

            app.review_ai_candidate_from_form(third.id, b"decision=accept&content=Tre")
            restarted = Archive(Path(tmp) / "archive")
            restarted_app = CaptureApp(restarted)
            final_html = restarted_app.render_inbox()
            self.assertEqual(final_html.count("data-ai-inbox-document-id="), 0)

    def test_document_main_flow_orders_accepted_content_before_captures(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI document")
            summary = _create_ai_candidate(archive, document.id, "Summary", "Summary text")
            claim = _create_ai_candidate(archive, document.id, "Claim", "Claim text")
            insight = _create_ai_candidate(archive, document.id, "Insight", "Insight text")
            question = _create_ai_candidate(archive, document.id, "Question", "Question text")
            capture = archive.create_knowledge_object(
                "Capture text", document_id=document.id
            )
            app = CaptureApp(archive)
            for candidate in (summary, claim, insight, question):
                app.review_ai_candidate_from_form(
                    candidate.id,
                    f"decision=accept&content={candidate.content.replace(' ', '+')}".encode("utf-8"),
                )

            html = app.render_document(document.id)

            positions = [
                html.index("Summary text"),
                html.index("Claim text"),
                html.index("Insight text"),
                html.index("Question text"),
                html.index("Capture text"),
            ]
            self.assertEqual(positions, sorted(positions))
            self.assertLess(html.index("Summary"), html.index("Claims"))
            self.assertLess(html.index("Claims"), html.index("Insights"))
            self.assertLess(html.index("Insights"), html.index("Questions"))
            self.assertLess(html.index("Questions"), html.index("Captures"))

    def test_review_history_is_linked_but_not_rendered_in_document_main_flow(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI document")
            candidate = _create_ai_candidate(archive, document.id, "Claim", "Original claim")
            app = CaptureApp(archive)
            app.review_ai_candidate_from_form(
                candidate.id,
                b"decision=reject&rejection_reason=felaktig",
            )

            main_html = app.render_document(document.id)
            history_html = app.render_review_history(document.id)

            self.assertIn(f"/documents/{document.id}/review-history", main_html)
            self.assertNotIn("AI-original: Original claim", main_html)
            self.assertNotIn("data-ai-reviewed-candidate-id", main_html)
            self.assertIn("AI-original: Original claim", history_html)
            self.assertIn("data-ai-reviewed-candidate-id", history_html)

    def test_document_groups_ai_candidates_by_semantic_type_order(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI-dokument")
            project = archive.create_project("Relevant projekt")
            _create_ai_candidate(archive, document.id, "Question", "Fråga")
            _create_ai_candidate(archive, document.id, "Insight", "Insikt")
            _create_ai_candidate(
                archive,
                document.id,
                "ProjectSuggestion",
                "Projektförslag",
                project_ids=(project.id,),
            )
            _create_ai_candidate(archive, document.id, "Summary", "Sammanfattning")
            _create_ai_candidate(archive, document.id, "Claim", "Påstående")
            app = CaptureApp(archive)

            html = app.render_document(document.id)

            positions = [
                html.index('id="ai-Summary"'),
                html.index('id="ai-Claim"'),
                html.index('id="ai-Insight"'),
                html.index('id="ai-Question"'),
                html.index('id="ai-ProjectSuggestion"'),
            ]
            self.assertEqual(positions, sorted(positions))
            self.assertIn('id="candidate-', html)

    def test_project_suggestion_can_link_document_without_creating_accepted_knowledge(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI-dokument")
            project = archive.create_project("Relevant projekt")
            suggestion = _create_ai_candidate(
                archive,
                document.id,
                "ProjectSuggestion",
                "Koppla till Relevant projekt.",
                project_ids=(project.id,),
            )
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                html = _get(server, f"/documents/{document.id}")
                self.assertIn("Koppla till projekt", html)
                self.assertIn("Avvisa", html)
                self.assertNotIn("Acceptera", html)
                self.assertNotIn("Senare", html)

                status, location = _post(
                    server,
                    f"/documents/{document.id}/candidates/{suggestion.id}",
                    "decision=link_project",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, f"/documents/{document.id}#ai-review")
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            reviewed = archive.get_knowledge_object(suggestion.id)
            self.assertEqual(reviewed.review_status, "handled")
            self.assertEqual(archive.get_document(document.id).project_ids, (project.id,))
            self.assertEqual(archive.list_knowledge_objects_for_document(document.id), [])

    def test_project_suggestion_reject_does_not_link_project(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI-dokument")
            project = archive.create_project("Relevant projekt")
            suggestion = _create_ai_candidate(
                archive,
                document.id,
                "ProjectSuggestion",
                "Koppla till Relevant projekt.",
                project_ids=(project.id,),
            )
            app = CaptureApp(archive)

            app.review_ai_candidate_from_form(
                suggestion.id,
                "decision=reject&rejection_reason=annat".encode("utf-8"),
            )

            reviewed = archive.get_knowledge_object(suggestion.id)
            self.assertEqual(reviewed.review_status, "rejected")
            self.assertEqual(archive.get_document(document.id).project_ids, ())

    def test_ai_review_decision_can_be_corrected_preserving_original_and_history(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI document")
            candidate = _create_ai_candidate(
                archive, document.id, "Claim", "Original claim"
            )
            app = CaptureApp(archive)

            app.review_ai_candidate_from_form(
                candidate.id,
                b"decision=accept&content=Accepted+claim",
            )
            corrected = app.review_ai_candidate_from_form(
                candidate.id,
                b"decision=reject&rejection_reason=felaktig",
            )

            self.assertEqual(corrected.review_status, "rejected")
            self.assertEqual(corrected.original_content, "Original claim")
            self.assertEqual(corrected.accepted_content, "Accepted claim")
            self.assertEqual(corrected.rejection_reason, "felaktig")
            self.assertEqual(len(corrected.history), 2)
            self.assertEqual(corrected.history[-1].review_status, "accepted")
            self.assertEqual(archive.list_knowledge_objects_for_document(document.id), [])

    def test_rejected_ai_candidate_can_be_corrected_to_accepted(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI document")
            candidate = _create_ai_candidate(
                archive, document.id, "Insight", "Original insight"
            )
            app = CaptureApp(archive)

            app.review_ai_candidate_from_form(
                candidate.id,
                b"decision=reject&rejection_reason=irrelevant",
            )
            corrected = app.review_ai_candidate_from_form(
                candidate.id,
                b"decision=accept&content=Useful+insight",
            )

            self.assertEqual(corrected.review_status, "accepted")
            self.assertEqual(corrected.content, "Useful insight")
            self.assertEqual(corrected.original_content, "Original insight")
            self.assertEqual(corrected.history[-1].review_status, "rejected")
            self.assertEqual(
                [item.id for item in archive.list_knowledge_objects_for_document(document.id)],
                [candidate.id],
            )

    def test_corrected_project_suggestion_unlinks_document_project(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI document")
            project = archive.create_project("Project")
            suggestion = _create_ai_candidate(
                archive,
                document.id,
                "ProjectSuggestion",
                "Link project.",
                project_ids=(project.id,),
            )
            app = CaptureApp(archive)

            app.review_ai_candidate_from_form(suggestion.id, b"decision=link_project")
            corrected = app.review_ai_candidate_from_form(
                suggestion.id,
                b"decision=reject",
            )

            self.assertEqual(corrected.review_status, "rejected")
            self.assertEqual(archive.get_document(document.id).project_ids, ())
            self.assertEqual(corrected.history[-1].review_status, "handled")

    def test_wrong_document_candidate_request_leaves_archive_consistent(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            first_document = archive.create_document("First")
            second_document = archive.create_document("Second")
            candidate = _create_ai_candidate(
                archive, first_document.id, "Claim", "Original claim"
            )
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, _ = _post(
                    server,
                    f"/documents/{second_document.id}/candidates/{candidate.id}",
                    b"decision=accept&content=Wrong".decode("utf-8"),
                )
                self.assertEqual(status, 400)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            loaded = archive.get_knowledge_object(candidate.id)
            self.assertEqual(loaded.review_status, "candidate")
            self.assertEqual(loaded.content, "Original claim")

    def test_slow_request_diagnostics_do_not_log_post_body(self) -> None:
        with workspace_tempdir() as tmp:
            messages: list[str] = []
            archive = Archive(Path(tmp) / "archive")
            app = CaptureApp(
                archive,
                log=messages.append,
                slow_request_threshold_seconds=0,
            )
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, _ = _post(
                    server,
                    "/capture",
                    "content=secret-body-value",
                )
                self.assertEqual(status, 303)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertTrue(any("slow request" in message for message in messages))
            joined = "\n".join(messages)
            self.assertIn("path=/capture", joined)
            self.assertNotIn("secret-body-value", joined)

    def test_ai_failure_is_logged_without_secret_or_document_text(self) -> None:
        class FailingProvider(AiProvider):
            name = "mock"

            def analyze_document(self, **kwargs):  # type: ignore[no-untyped-def]
                raise AiProviderError("simulerat fel med provider")

        with workspace_tempdir() as tmp:
            messages: list[str] = []
            root = Path(tmp)
            archive = Archive(root / "archive")
            pdf_path = root / "rapport.pdf"
            write_minimal_pdf(pdf_path, text="VERY SECRET DOCUMENT TEXT")
            document = archive.register_document_with_original_pdf(
                pdf_path,
                title="AI rapport",
                text="VERY SECRET DOCUMENT TEXT",
                checksum_sha256=calculate_checksum(pdf_path),
            )
            app = CaptureApp(archive, ai_provider=FailingProvider(), log=messages.append)

            with self.assertRaises(AiProviderError):
                app.run_document_ai_analysis_from_form(
                    document.id, b"confirm_ai=yes&api_key=sk-should-not-log"
                )

            joined = "\n".join(messages)
            self.assertIn("ai analysis failed", joined)
            self.assertIn(f"document_id={document.id}", joined)
            self.assertNotIn("sk-should-not-log", joined)
            self.assertNotIn("VERY SECRET DOCUMENT TEXT", joined)

    def test_existing_project_link_hides_project_suggestion_and_not_duplicate_link(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI-dokument")
            project = archive.create_project("Relevant projekt")
            archive.set_document_projects(document.id, (project.id,))
            suggestion = _create_ai_candidate(
                archive,
                document.id,
                "ProjectSuggestion",
                "Koppla till Relevant projekt.",
                project_ids=(project.id,),
            )
            app = CaptureApp(archive)

            document_html = app.render_document(document.id)
            inbox_html = app.render_inbox()
            self.assertNotIn(
                f'data-ai-review-candidate-id="{suggestion.id}"',
                document_html,
            )
            self.assertNotIn(f'data-ai-inbox-document-id="{document.id}"', inbox_html)

            reviewed = app.review_ai_candidate_from_form(
                suggestion.id,
                "decision=link_project".encode("utf-8"),
            )

            self.assertEqual(reviewed.review_status, "handled")
            self.assertEqual(
                archive.get_document(document.id).project_ids, (project.id,)
            )

    def test_project_suggestion_without_valid_project_is_not_actionable(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("AI-dokument")
            suggestion = _create_ai_candidate(
                archive,
                document.id,
                "ProjectSuggestion",
                "Koppla till ett okänt projekt.",
            )
            app = CaptureApp(archive)

            document_html = app.render_document(document.id)
            inbox_html = app.render_inbox()

            self.assertNotIn(
                f'data-ai-review-candidate-id="{suggestion.id}"',
                document_html,
            )
            self.assertNotIn("Koppla till projekt", document_html)
            self.assertNotIn(f'data-ai-inbox-document-id="{document.id}"', inbox_html)

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

    def test_document_metadata_can_be_edited_over_http(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Old")
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, location = _post(
                    server,
                    f"/documents/{document.id}/metadata",
                    "title=New&author=Org&year=2024",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, f"/documents/{document.id}")
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            loaded = Archive(Path(tmp) / "archive").get_document(document.id)
            self.assertEqual(loaded.title, "New")
            self.assertEqual(loaded.author, "Org")
            self.assertEqual(loaded.year, "2024")

    def test_invalid_document_year_over_http_does_not_persist(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Stable")
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, _ = _post(
                    server,
                    f"/documents/{document.id}/metadata",
                    "title=Changed&author=Org&year=24",
                )
                self.assertEqual(status, 400)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(archive.get_document(document.id).title, "Stable")

    def test_server_rendered_html_uses_utf8_and_repairs_mojibake(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Å Ä Ö", author="å ä ö", year="2024")
            project = archive.create_project("Projekt")
            _create_ai_candidate(
                archive,
                document.id,
                "ProjectSuggestion",
                "Förslag med å ä ö Å Ä Ö",
                project_ids=(project.id,),
            )
            archive.create_knowledge_object(
                "Capture å ä ö Å Ä Ö", document_id=document.id
            )
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, headers, html = _get_with_headers(
                    server, f"/documents/{document.id}"
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(status, 200)
            self.assertEqual(headers["content-type"], "text/html; charset=utf-8")
            self.assertIn('<meta charset="utf-8">', html)
            self.assertIn("Utgivningsår", html)
            self.assertIn("Källor", html)
            self.assertIn("Föreslaget projekt", html)
            self.assertIn("å ä ö Å Ä Ö", html)
            self.assertNotIn("Ã¥", html)
            self.assertNotIn("Ã¤", html)
            self.assertNotIn("Ã¶", html)

    def test_render_documents_lists_manual_documents(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            archive.create_document("Andens fenomenologi")
            app = CaptureApp(archive)

            html = app.render_documents()

            self.assertIn("Andens fenomenologi", html)
            self.assertIn('href="/documents/new"', html)
            self.assertNotIn('<form method="post" action="/documents">', html)

    def test_documents_overview_filters_by_metadata_only(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            matching = archive.create_document(
                "Nationell biblioteksstrategi",
                author="Kungliga biblioteket",
                year="2024",
            )
            other = archive.create_document("Kommunal rapport", author="Stad")
            archive.create_knowledge_object(
                "needle bara i capture", document_id=other.id
            )
            app = CaptureApp(archive)

            self.assertIn(matching.title, app.render_documents(query="biblioteks"))
            self.assertIn(matching.title, app.render_documents(query="kungliga"))
            self.assertIn(matching.title, app.render_documents(query="2024"))
            html = app.render_documents(query="needle")

            self.assertNotIn(matching.title, html)
            self.assertNotIn(other.title, html)
            self.assertIn("Inga dokument ännu.", html)

    def test_documents_overview_sorts_by_title_and_year(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            archive.create_document("Zeta", year="2020")
            archive.create_document("Alfa", year="2023")
            archive.create_document("Beta")
            app = CaptureApp(archive)

            default_html = app.render_documents()
            self.assertLess(default_html.index("Alfa"), default_html.index("Zeta"))
            self.assertLess(default_html.index("Zeta"), default_html.index("Beta"))

            by_title = app.render_documents(sort="title")
            self.assertLess(by_title.index("Alfa"), by_title.index("Beta"))
            self.assertLess(by_title.index("Beta"), by_title.index("Zeta"))

            by_year = app.render_documents(sort="year")
            self.assertLess(by_year.index("Alfa"), by_year.index("Zeta"))
            self.assertLess(by_year.index("Zeta"), by_year.index("Beta"))

    def test_manual_document_creation_is_available_on_secondary_page(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                overview_html = _get(server, "/documents")
                new_html = _get(server, "/documents/new")
                status, location = _post(
                    server,
                    "/documents",
                    "title=Manuellt+document&author=Bibliotek&year=2024",
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertIn('href="/documents/new"', overview_html)
            self.assertNotIn('<form method="post" action="/documents">', overview_html)
            self.assertIn('<form method="post" action="/documents">', new_html)
            self.assertEqual(status, 303)
            self.assertTrue(location.startswith("/documents/doc_"))
            self.assertEqual(archive.list_documents()[0].title, "Manuellt document")

    def test_documents_overview_filters_by_ai_status_and_project(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            project = archive.create_project("Prioriterat")
            analyzed = archive.create_document("Analyserad")
            unanalyzed = archive.create_document("Ej analyserad")
            outside_project = archive.create_document("Utanför projekt")
            archive.save_document(analyzed.with_projects((project.id,)))
            archive.save_document(unanalyzed.with_projects((project.id,)))
            _save_completed_ai_run(archive, analyzed.id)
            _save_completed_ai_run(archive, outside_project.id)
            app = CaptureApp(archive)

            html = app.render_documents(ai_status="analyzed", project_id=project.id)

            self.assertIn("Analyserad", html)
            self.assertNotIn("Ej analyserad", html)
            self.assertNotIn("Utanför projekt", html)
            self.assertIn("AI-analyserad", html)
            self.assertIn("Prioriterat", html)

    def test_documents_overview_shows_list_metadata_without_visible_ids(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document(
                "Årsrapport", author="Biblioteket", year="2024"
            )
            archive.create_knowledge_object("Egen capture", document_id=document.id)
            archive.create_knowledge_object(
                "AI-accepterad text",
                creator="user_after_ai",
                document_id=document.id,
            )
            _save_completed_ai_run(archive, document.id)
            app = CaptureApp(archive)

            html = app.render_documents()

            self.assertIn("Årsrapport", html)
            self.assertIn("Biblioteket", html)
            self.assertIn("2024", html)
            self.assertIn("AI-analyserad", html)
            self.assertIn("1 egen capture", html)
            self.assertNotIn("2 egna captures", html)
            self.assertNotIn(f">{document.id}<", html)
            self.assertNotIn("ID:", html)

    def test_documents_overview_uses_bounded_archive_reads(self) -> None:
        class CountingArchive(Archive):
            knowledge_reads = 0
            ai_run_reads = 0

            def list_knowledge_objects(self):  # type: ignore[no-untyped-def]
                self.knowledge_reads += 1
                return super().list_knowledge_objects()

            def list_ai_runs(self):  # type: ignore[no-untyped-def]
                self.ai_run_reads += 1
                return super().list_ai_runs()

            def extracted_text_file_path(self, document_id: str) -> Path:
                raise AssertionError("Documents overview must not read full text")

        with workspace_tempdir() as tmp:
            archive = CountingArchive(Path(tmp) / "archive")
            archive.create_document("Metadata only")
            archive.create_knowledge_object("Capture")
            app = CaptureApp(archive)

            html = app.render_documents(query="metadata")

            self.assertIn("Metadata only", html)
            self.assertEqual(archive.knowledge_reads, 1)
            self.assertEqual(archive.ai_run_reads, 1)

    def test_documents_route_accepts_filter_query_parameters(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            archive.create_document("Alfa")
            archive.create_document("Beta")
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                html = _get(server, "/documents?q=alfa&sort=title")
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertIn("Alfa", html)
            self.assertNotIn("Beta", html)

    def test_render_document_shows_capture_form_without_redundant_self_context(self) -> None:
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
            self.assertIn(f'value="{document.id}"', html)
            self.assertIn("Källposition", html)
            self.assertIn("Detta liknar North.", html)
            self.assertIn("kapitel 4", html)
            self.assertNotIn("Fristående notering.", html)
            self.assertNotIn("Aktuellt dokument", html)
            self.assertNotIn("Inbox-status", html)

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

    def test_upload_page_is_reachable_and_linked_from_inbox(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _web_config(root)
            app = CaptureApp(Archive(config.archive_root), config=config)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                inbox = _get(server, "/inbox")
                upload = _get(server, "/upload")
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertIn('href="/upload"', inbox)
            self.assertIn('type="file"', upload)
            self.assertIn('accept="application/pdf,.pdf"', upload)

    def test_valid_pdf_upload_creates_document_original_text_inbox_and_index(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _web_config(root)
            source_pdf = root / "2024 Mobil rapport.pdf"
            write_minimal_pdf(source_pdf, title="", author="Mobil", text="Upload text")
            app = CaptureApp(Archive(config.archive_root), config=config)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, body = _post_multipart_pdf(
                    server,
                    "/upload",
                    "2024 Mobil rapport.pdf",
                    source_pdf.read_bytes(),
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            archive = Archive(config.archive_root)
            documents = archive.list_documents()
            self.assertEqual(status, 200)
            self.assertIn("Dokumentet har lagts till i Inbox.", body)
            self.assertEqual(len(documents), 1)
            self.assertEqual(documents[0].title, "Mobil rapport")
            self.assertEqual(documents[0].year, "2024")
            self.assertEqual(documents[0].author, "Mobil")
            self.assertEqual(documents[0].original_filename, "2024 Mobil rapport.pdf")
            self.assertEqual(documents[0].inbox_status, "new")
            self.assertTrue(archive.original_file_path(documents[0].id).exists())
            self.assertIn(
                "Upload text",
                archive.extracted_text_file_path(documents[0].id).read_text(encoding="utf-8"),
            )
            self.assertEqual(
                [row["title"] for row in list_indexed_documents(config.runtime_root)],
                ["Mobil rapport"],
            )

    def test_upload_duplicate_does_not_create_second_document(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _web_config(root)
            source_pdf = root / "rapport.pdf"
            write_minimal_pdf(source_pdf, title="Dublett", text="Samma text")
            app = CaptureApp(Archive(config.archive_root), config=config)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                _post_multipart_pdf(server, "/upload", "rapport.pdf", source_pdf.read_bytes())
                status, body = _post_multipart_pdf(
                    server, "/upload", "rapport.pdf", source_pdf.read_bytes()
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(status, 200)
            self.assertIn("PDF-filen finns redan i Archive.", body)
            self.assertEqual(len(Archive(config.archive_root).list_documents()), 1)

    def test_directory_ingest_and_upload_share_checksum_duplicate_semantics(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _web_config(root)
            config.ingest_source.mkdir(parents=True)
            source_pdf = config.ingest_source / "rapport.pdf"
            write_minimal_pdf(source_pdf, title="Katalog först", text="Samma PDF")
            pdf_bytes = source_pdf.read_bytes()
            from dokumentverkstad.ingest import process_ingest_source

            process_ingest_source(Archive(config.archive_root), config.ingest_source, config.runtime_root)
            app = CaptureApp(Archive(config.archive_root), config=config)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, body = _post_multipart_pdf(
                    server, "/upload", "rapport.pdf", pdf_bytes
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(status, 200)
            self.assertIn("PDF-filen finns redan i Archive.", body)
            self.assertEqual(len(Archive(config.archive_root).list_documents()), 1)

    def test_upload_filename_traversal_is_reduced_to_safe_basename(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _web_config(root)
            source_pdf = root / "safe.pdf"
            write_minimal_pdf(source_pdf, title="Säker", text="Text")
            app = CaptureApp(Archive(config.archive_root), config=config)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                status, _ = _post_multipart_pdf(
                    server, "/upload", "../2025 Säker.pdf", source_pdf.read_bytes()
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            documents = Archive(config.archive_root).list_documents()
            self.assertEqual(status, 200)
            self.assertEqual(documents[0].original_filename, "2025 Säker.pdf")
            self.assertFalse((root / "2025 Säker.pdf").exists())

    def test_upload_rejects_absolute_and_windows_drive_filenames(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _web_config(root)
            source_pdf = root / "safe.pdf"
            write_minimal_pdf(source_pdf, title="Säker", text="Text")
            app = CaptureApp(Archive(config.archive_root), config=config)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                unix_status, unix_body = _post_multipart_pdf(
                    server, "/upload", "/tmp/rapport.pdf", source_pdf.read_bytes()
                )
                windows_status, windows_body = _post_multipart_pdf(
                    server, "/upload", "C:\\tmp\\rapport.pdf", source_pdf.read_bytes()
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(unix_status, 200)
            self.assertEqual(windows_status, 200)
            self.assertIn("Filnamnet är inte säkert att använda.", unix_body)
            self.assertIn("Filnamnet är inte säkert att använda.", windows_body)
            self.assertEqual(Archive(config.archive_root).list_documents(), [])

    def test_upload_rejects_non_pdf_and_oversized_request(self) -> None:
        with workspace_tempdir() as tmp:
            root = Path(tmp)
            config = _web_config(root)
            config = AppConfig(
                archive_root=config.archive_root,
                runtime_root=config.runtime_root,
                ingest_source=config.ingest_source,
                encrypted_secrets_path=config.encrypted_secrets_path,
                secrets_path=config.secrets_path,
                upload_max_bytes=20,
            )
            app = CaptureApp(Archive(config.archive_root), config=config)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                too_large_status, _ = _post_multipart_pdf(
                    server, "/upload", "large.pdf", b"%PDF-" + b"x" * 100
                )
                app.upload_max_bytes = 10_000
                bad_status, bad_body = _post_multipart_pdf(
                    server, "/upload", "not.pdf", b"not actually a pdf"
                )
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(too_large_status, 413)
            self.assertEqual(bad_status, 200)
            self.assertIn("Filen är inte en PDF.", bad_body)
            self.assertEqual(Archive(config.archive_root).list_documents(), [])

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

    def test_capture_can_be_edited_over_http_and_history_is_kept(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            document = archive.create_document("Document")
            note = archive.create_knowledge_object(
                "Original note", document_id=document.id, source_location="p. 1"
            )
            app = CaptureApp(archive)
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                edit_html = _get(server, f"/knowledge/{note.id}/edit")
                self.assertIn("Original note", edit_html)
                status, location = _post(
                    server,
                    f"/knowledge/{note.id}",
                    "content=Corrected+note&source_location=p.+2",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, f"/documents/{document.id}")
                document_html = _get(server, f"/documents/{document.id}")
                self.assertIn("Corrected note", document_html)
                self.assertIn("p. 2", document_html)
                self.assertNotIn("Original note</p>", document_html)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            loaded = Archive(Path(tmp) / "archive").get_knowledge_object(note.id)
            self.assertEqual(loaded.content, "Corrected note")
            self.assertEqual(loaded.source_location, "p. 2")
            self.assertEqual(loaded.history[0].content, "Original note")
            self.assertEqual(loaded.history[0].source_location, "p. 1")

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


def _create_ai_candidate(
    archive: Archive,
    document_id: str,
    semantic_type: str,
    content: str,
    project_ids: tuple[str, ...] = (),
):
    return archive.create_ai_candidate(
        content=content,
        ai_run_id="airun_test",
        ai_provider="mock",
        ai_model="mock-model",
        prompt_version="test",
        capability=semantic_type,
        document_id=document_id,
        confidence="medel",
        project_ids=project_ids,
        semantic_type=semantic_type,
    )


def _web_config(root: Path) -> AppConfig:
    return AppConfig(
        archive_root=root / "archive",
        runtime_root=root / "runtime",
        ingest_source=root / "ingest",
        encrypted_secrets_path=root / "secrets.enc",
        secrets_path=root / "secrets.toml",
    )


def _save_completed_ai_run(archive: Archive, document_id: str) -> AiRunRecord:
    run = AiRunRecord(
        id=f"airun_test_{document_id}",
        document_id=document_id,
        provider="mock",
        model="mock-model",
        prompt_version="test",
        capabilities=("Summary",),
        created_at="2024-01-01T00:00:00+00:00",
        status="completed",
        estimated_input_tokens=0,
        estimated_output_tokens=0,
        estimated_cost=0.0,
    )
    archive.save_ai_run(run)
    return run


if __name__ == "__main__":
    unittest.main()
