from __future__ import annotations

from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
import threading
import unittest
from pathlib import Path

from dokumentverkstad.archive import Archive
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
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertIn('href="/documents"', root_html)
            self.assertIn('href="/projects"', root_html)
            self.assertIn("Inga dokument ännu.", documents_html)
            self.assertIn("Inga projekt ännu.", projects_html)
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
                    self.assertEqual(location, f"/documents/{document.id}")
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
                self.assertEqual(location, f"/documents/{document.id}")

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
                    self.assertEqual(location, f"/documents/{document.id}")

                status, location = _post(
                    server,
                    f"/documents/{document.id}/candidates/{insight.id}",
                    "decision=later",
                )
                self.assertEqual(status, 303)
                self.assertEqual(location, f"/documents/{document.id}")

                status, _ = _post(
                    server,
                    f"/documents/{document.id}/candidates/{summary.id}",
                    "decision=reject&rejection_reason=annat",
                )
                self.assertEqual(status, 400)
            finally:
                server.shutdown()
                server.server_close()
                thread.join()

            self.assertEqual(archive.get_knowledge_object(summary.id).review_status, "accepted")
            self.assertEqual(
                archive.get_knowledge_object(first_claim.id).review_status, "accepted"
            )
            self.assertEqual(
                archive.get_knowledge_object(second_claim.id).review_status, "accepted"
            )
            self.assertEqual(archive.get_knowledge_object(insight.id).review_status, "later")
            self.assertEqual(archive.get_knowledge_object(question.id).review_status, "candidate")

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
                self.assertEqual(location, f"/documents/{document.id}")
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

    def test_render_documents_lists_manual_documents(self) -> None:
        with workspace_tempdir() as tmp:
            archive = Archive(Path(tmp) / "archive")
            archive.create_document("Andens fenomenologi")
            app = CaptureApp(archive)

            html = app.render_documents()

            self.assertIn("Andens fenomenologi", html)
            self.assertIn('action="/documents"', html)

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


if __name__ == "__main__":
    unittest.main()
