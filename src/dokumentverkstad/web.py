from __future__ import annotations

from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from .ai import (
    AI_CAPABILITIES,
    DEFAULT_AI_MODEL,
    DEFAULT_AI_PROVIDER,
    DEFAULT_MAX_OUTPUT_TOKENS,
    AiCost,
    AiProvider,
    AiProviderError,
    AiRunRecord,
    MissingCredentialError,
    MockAiProvider,
    OpenAiProvider,
    PROMPT_VERSION,
    estimate_cost,
    estimate_input_tokens,
    validate_document_size,
)
from .archive import Archive
from .config import AppConfig, ensure_app_directories, load_config
from .document import Document
from .knowledge import KnowledgeObject
from .project import Project
from .secrets import load_openai_api_key


class CaptureApp:
    def __init__(
        self,
        archive: Archive,
        config: AppConfig | None = None,
        ai_provider: AiProvider | None = None,
    ):
        self.archive = archive
        self.config = config
        self.ai_provider_override = ai_provider
        self.ai_provider_name = (
            ai_provider.name if ai_provider else config.ai_provider if config else DEFAULT_AI_PROVIDER
        )
        self.ai_model = config.ai_model if config else DEFAULT_AI_MODEL
        self.secrets_path = (
            config.secrets_path if config else archive.root.parent / "secrets.toml"
        )
        self.archive.initialize()

    def render_capture(
        self, document: Document | None = None, project: Project | None = None
    ) -> str:
        notes = (
            self.archive.list_knowledge_objects_for_document(document.id)
            if document
            else self.archive.list_knowledge_objects_for_project(project.id)
            if project
            else self._accepted_recent_notes()
        )
        return self._page(
            title="Capture",
            body=f"""
    <h1>Capture</h1>
    {self._render_capture_form(document=document, project=project)}
    <section aria-labelledby="recent-notes">
      <h2 id="recent-notes">Senaste noteringar</h2>
      <ul>
        {self._render_notes(notes, "Inga noteringar ännu.")}
      </ul>
    </section>
""",
        )

    def render_inbox(self) -> str:
        documents = self.archive.list_inbox_documents()
        candidates = self._visible_ai_candidates_for_inbox()
        rendered_documents = "\n".join(
            self._render_inbox_document(document) for document in documents
        )
        rendered_candidates = self._render_ai_inbox_candidates(candidates)
        empty_notice = "<p>Inbox är tom.</p>" if not documents and not candidates else ""
        if not rendered_documents:
            rendered_documents = "<p>Inga väntande documents.</p>"
        if not rendered_candidates:
            rendered_candidates = "<p>Inga documents har väntande AI-review.</p>"

        return self._page(
            title="Inbox",
            body=f"""
    <h1>Inbox</h1>
    {empty_notice}
    <section aria-labelledby="inbox-documents">
      <h2 id="inbox-documents">Väntande documents</h2>
      {rendered_documents}
    </section>
    <section aria-labelledby="inbox-candidates">
      <h2 id="inbox-candidates">AI-review</h2>
      {rendered_candidates}
    </section>
    <p><a href="/trash">Trash</a></p>
""",
        )

    def render_trash(self) -> str:
        documents = self.archive.list_trashed_documents()
        rendered_documents = "\n".join(
            f"""
      <li>
        <a href="/documents/{escape(document.id)}">{escape(document.title)}</a>
        <form method="post" action="/trash/documents/{escape(document.id)}/restore">
          <button type="submit">Återställ</button>
        </form>
      </li>
"""
            for document in documents
        )
        if not rendered_documents:
            rendered_documents = "<li>Trash är tom.</li>"

        return self._page(
            title="Trash",
            body=f"""
    <h1>Trash</h1>
    <ul>
      {rendered_documents}
    </ul>
    <p><a href="/inbox">Inbox</a></p>
""",
        )

    def render_documents(self) -> str:
        documents = self.archive.list_documents()
        rendered_documents = "\n".join(
            f"<li><a href=\"/documents/{escape(document.id)}\">"
            f"{escape(document.title)}</a></li>"
            for document in documents
        )
        if not rendered_documents:
            rendered_documents = "<li>Inga dokument ännu.</li>"

        return self._page(
            title="Documents",
            body=f"""
    <h1>Documents</h1>
    <form method="post" action="/documents">
      <label for="title">Titel</label>
      <input id="title" name="title" type="text" required>
      <button type="submit">Skapa document</button>
    </form>
    <h2>Registrerade documents</h2>
    <ul>
      {rendered_documents}
    </ul>
    <p><a href="/capture">Capture utan dokument</a></p>
""",
        )

    def render_document(self, document_id: str) -> str:
        document = self.archive.get_document(document_id)
        notes = self.archive.list_knowledge_objects_for_document(document.id)
        candidates = self._visible_ai_candidates_for_document(document)
        runs = self.archive.list_ai_runs_for_document(document.id)
        linked_projects = [
            project
            for project in self.archive.list_projects()
            if project.id in document.project_ids
        ]
        rendered_projects = ", ".join(
            f"<a href=\"/projects/{escape(project.id)}\">{escape(project.name)}</a>"
            for project in linked_projects
        )
        if not rendered_projects:
            rendered_projects = "Inga projects"
        original_file = (
            f"<a href=\"/documents/{escape(document.id)}/original\">"
            f"{escape(document.original_filename or 'original.pdf')}</a>"
            if document.has_original_file
            else "Ingen digital originalfil"
        )
        return self._page(
            title=document.title,
            body=f"""
    <p><a href="/documents">Documents</a></p>
    <h1>{escape(document.title)}</h1>
    <dl>
      <dt>Originalfil</dt>
      <dd>{original_file}</dd>
      <dt>Projects</dt>
      <dd>{rendered_projects}</dd>
    </dl>
    {self._render_document_ai_panel(document, candidates, runs)}
    <section aria-labelledby="document-capture">
      <h2 id="document-capture">Capture</h2>
      {self._render_capture_form(document=document, show_context=False)}
    </section>
    <section aria-labelledby="document-notes">
      <h2 id="document-notes">Kopplade noteringar</h2>
      <ul>
        {self._render_notes(notes, "Inga kopplade noteringar ännu.")}
      </ul>
    </section>
""",
        )

    def render_document_ai_confirmation(self, document_id: str) -> str:
        document = self.archive.get_document(document_id)
        try:
            text = self._read_document_text(document)
            estimate = self._estimate_document_ai_cost(text)
            validate_document_size(estimate.input_tokens)
        except AiProviderError as error:
            return self.render_ai_message(document, str(error))

        credential_note = ""
        if self.ai_provider_name == "openai" and not load_openai_api_key(self.secrets_path):
            credential_note = (
                "<p>Ingen OpenAI API-nyckel är konfigurerad. "
                "Lägg till OPENAI_API_KEY eller .dokumentverkstad/secrets.toml innan AI kan köras.</p>"
            )

        return self._page(
            title="AI-analys",
            body=f"""
    <p><a href="/documents/{escape(document.id)}">{escape(document.title)}</a></p>
    <h1>AI-analys</h1>
    {credential_note}
    <p>Dokumentets extraherade text skickas till extern AI-provider först när du startar analysen.</p>
    <dl>
      <dt>Document</dt>
      <dd>{escape(document.title)}</dd>
      <dt>Provider</dt>
      <dd>{escape(self.ai_provider_name)}</dd>
      <dt>Modell</dt>
      <dd>{escape(self.ai_model)}</dd>
      <dt>Capabilities</dt>
      <dd>{escape(', '.join(AI_CAPABILITIES))}</dd>
      <dt>Uppskattade input-token</dt>
      <dd>{estimate.input_tokens}</dd>
      <dt>Planerade max output-token</dt>
      <dd>{estimate.output_tokens}</dd>
      <dt>Uppskattad kostnad</dt>
      <dd>{self._format_cost(estimate)}</dd>
      <dt>Beräkningsmetod</dt>
      <dd>Konservativ lokal uppskattning. Ingen dokumenttext skickas till AI-provider för estimatet.</dd>
    </dl>
    <form method="post" action="/documents/{escape(document.id)}/ai/run">
      <button name="confirm_ai" type="submit" value="yes">Starta AI-analys</button>
    </form>
""",
        )

    def render_ai_message(self, document: Document, message: str) -> str:
        return self._page(
            title="AI-analys",
            body=f"""
    <p><a href="/documents/{escape(document.id)}">{escape(document.title)}</a></p>
    <h1>AI-analys</h1>
    <p>{escape(message)}</p>
""",
        )

    def render_projects(self) -> str:
        projects = self.archive.list_projects()
        rendered_projects = "\n".join(
            f"<li><a href=\"/projects/{escape(project.id)}\">"
            f"{escape(project.name)}</a></li>"
            for project in projects
        )
        if not rendered_projects:
            rendered_projects = "<li>Inga projekt ännu.</li>"

        return self._page(
            title="Projects",
            body=f"""
    <h1>Projects</h1>
    <form method="post" action="/projects">
      <label for="name">Namn</label>
      <input id="name" name="name" type="text" required>
      <label for="description">Beskrivning</label>
      <input id="description" name="description" type="text">
      <button type="submit">Skapa project</button>
    </form>
    <h2>Registrerade projects</h2>
    <ul>
      {rendered_projects}
    </ul>
    <p><a href="/capture">Capture utan projekt</a></p>
""",
        )

    def render_project(self, project_id: str) -> str:
        project = self.archive.get_project(project_id)
        notes = self.archive.list_knowledge_objects_for_project(project.id)
        documents = self.archive.list_documents_for_project(project.id)
        unlinked_notes = [
            note
            for note in self.archive.list_recent_knowledge_objects(limit=10_000)
            if project.id not in note.project_ids and note.review_status == "accepted"
        ]
        rendered_documents = "\n".join(
            f"<li><a href=\"/documents/{escape(document.id)}\">"
            f"{escape(document.title)}</a></li>"
            for document in documents
        )
        if not rendered_documents:
            rendered_documents = "<li>Inga relevanta documents ännu.</li>"

        return self._page(
            title=project.name,
            body=f"""
    <p><a href="/projects">Projects</a></p>
    <h1>{escape(project.name)}</h1>
    <p>{escape(project.description)}</p>
    <form method="post" action="/projects/{escape(project.id)}">
      <label for="name">Namn</label>
      <input id="name" name="name" type="text" value="{escape(project.name)}" required>
      <label for="description">Beskrivning</label>
      <input id="description" name="description" type="text" value="{escape(project.description)}">
      <button type="submit">Spara project</button>
    </form>
    <section aria-labelledby="project-capture">
      <h2 id="project-capture">Capture</h2>
      {self._render_capture_form(project=project)}
    </section>
    <section aria-labelledby="project-notes">
      <h2 id="project-notes">Kopplade noteringar</h2>
      <ul>
        {self._render_notes(notes, "Inga kopplade noteringar ännu.")}
      </ul>
    </section>
    <section aria-labelledby="project-documents">
      <h2 id="project-documents">Relevanta documents</h2>
      <ul>
        {rendered_documents}
      </ul>
    </section>
    {self._render_project_link_form(project, unlinked_notes)}
    {self._render_relation_form(notes)}
""",
        )

    def create_document_from_form(self, body: bytes) -> Document:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        return self.archive.create_document(
            title=form.get("title", [""])[0],
            author=form.get("author", [""])[0],
            year=form.get("year", [""])[0],
            document_type=form.get("document_type", [""])[0],
            language=form.get("language", [""])[0],
            edition=form.get("edition", [""])[0],
            comment=form.get("comment", [""])[0],
        )

    def create_project_from_form(self, body: bytes) -> Project:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        return self.archive.create_project(
            name=form.get("name", [""])[0],
            description=form.get("description", [""])[0],
        )

    def update_project_from_form(self, project_id: str, body: bytes) -> Project:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        return self.archive.update_project(
            project_id,
            name=form.get("name", [""])[0],
            description=form.get("description", [""])[0],
        )

    def link_note_to_project_from_form(self, project_id: str, body: bytes) -> None:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        object_id = form.get("object_id", [""])[0]
        self.archive.add_knowledge_object_to_project(object_id, project_id)

    def create_relation_from_form(self, body: bytes) -> None:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        self.archive.create_relation(
            source_id=form.get("source_id", [""])[0],
            target_id=form.get("target_id", [""])[0],
            comment=form.get("comment", [""])[0],
        )

    def review_ai_candidate_from_form(self, object_id: str, body: bytes) -> KnowledgeObject:
        candidate = self.archive.get_knowledge_object(object_id)
        if candidate.review_status not in {"candidate", "later"}:
            raise ValueError("AI candidate has already been reviewed.")
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        decision = form.get("decision", [""])[0]
        content = form.get("content", [""])[0]
        rejection_reason = form.get("rejection_reason", [""])[0]
        if candidate.semantic_type == "ProjectSuggestion":
            if decision == "link_project":
                project_id = candidate.project_ids[0] if candidate.project_ids else ""
                if not project_id:
                    raise ValueError("Project suggestion has no project.")
                self.archive.get_project(project_id)
                document = self.archive.get_document(candidate.document_id)
                self.archive.set_document_projects(
                    document.id, (*document.project_ids, project_id)
                )
                return self.archive.review_knowledge_candidate(
                    object_id, "handled", content=candidate.content
                )
            if decision == "reject":
                return self.archive.review_knowledge_candidate(
                    object_id, "rejected", rejection_reason=rejection_reason
                )
            raise ValueError("Unknown project suggestion review decision.")
        if decision == "accept":
            return self.archive.review_knowledge_candidate(
                object_id, "accepted", content=content
            )
        if decision == "later":
            return self.archive.review_knowledge_candidate(object_id, "later")
        if decision == "reject":
            return self.archive.review_knowledge_candidate(
                object_id, "rejected", rejection_reason=rejection_reason
            )
        raise ValueError("Unknown AI candidate review decision.")

    def run_document_ai_analysis_from_form(
        self, document_id: str, body: bytes
    ) -> AiRunRecord:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        if form.get("confirm_ai", [""])[0] != "yes":
            raise AiProviderError("AI-analys kräver uttryckligt godkännande.")

        document = self.archive.get_document(document_id)
        text = self._read_document_text(document)
        estimate = self._estimate_document_ai_cost(text)
        validate_document_size(estimate.input_tokens)
        run = AiRunRecord.create(
            document_id=document.id,
            provider=self.ai_provider_name,
            model=self.ai_model,
            capabilities=AI_CAPABILITIES,
            estimate=estimate,
        )
        self.archive.save_ai_run(run)

        try:
            provider = self._make_ai_provider()
            projects = tuple(
                (project.id, project.name) for project in self.archive.list_projects()
            )
            result = provider.analyze_document(
                title=document.title,
                text=text,
                projects=projects,
                model=self.ai_model,
            )
            candidate_ids = tuple(
                self.archive.create_ai_candidate(
                    content=candidate.content,
                    ai_run_id=run.id,
                    ai_provider=self.ai_provider_name,
                    ai_model=self.ai_model,
                    prompt_version=PROMPT_VERSION,
                    capability=candidate.capability,
                    document_id=document.id,
                    confidence=candidate.confidence,
                    project_ids=(
                        (candidate.project_id,)
                        if candidate.capability == "project_suggestion"
                        and candidate.project_id
                        and candidate.project_id not in document.project_ids
                        else ()
                    ),
                    semantic_type=self._semantic_type_for_capability(
                        candidate.capability
                    ),
                ).id
                for candidate in result.candidates
                if candidate.capability != "project_suggestion"
                or not candidate.project_id
                or candidate.project_id not in document.project_ids
            )
            completed = run.completed(result.usage, candidate_ids)
            self.archive.save_ai_run(completed)
            return completed
        except AiProviderError:
            failed = run.failed("AI-körningen misslyckades.")
            self.archive.save_ai_run(failed)
            raise

    def update_inbox_document_from_form(self, document_id: str, body: bytes) -> None:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        project_ids = tuple(form.get("project_id", []))
        decision = form.get("decision", [""])[0]
        self.archive.set_document_projects(document_id, project_ids)
        if decision:
            self.archive.set_document_inbox_status(document_id, decision)

    def create_note_from_form(self, body: bytes) -> None:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        content = form.get("content", [""])[0]
        document_id = form.get("document_id", [""])[0]
        project_id = form.get("project_id", [""])[0]
        source_location = form.get("source_location", [""])[0]
        self.archive.create_knowledge_object(
            content,
            document_id=document_id,
            source_location=source_location,
            project_ids=(project_id,) if project_id else (),
        )

    def _render_capture_form(
        self,
        document: Document | None = None,
        project: Project | None = None,
        show_context: bool = True,
    ) -> str:
        action = "/capture"
        context = ""
        hidden_document = ""
        source_location = ""
        project_choice = ""
        if document:
            action = f"/capture?document_id={escape(document.id)}"
            hidden_document = (
                f"<input name=\"document_id\" type=\"hidden\" value=\"{escape(document.id)}\">"
            )
            if show_context:
                context = (
                    "<p>Aktuellt dokument: "
                    f"<a href=\"/documents/{escape(document.id)}\">"
                    f"{escape(document.title)}</a></p>"
                )
            source_location = """
      <label for="source_location">Källposition</label>
      <input id="source_location" name="source_location" type="text" placeholder="s. 35 eller kapitel 4">
"""
        if project:
            action = f"/capture?project_id={escape(project.id)}"
            if show_context:
                context = (
                    "<p>Aktuellt project: "
                    f"<a href=\"/projects/{escape(project.id)}\">"
                    f"{escape(project.name)}</a></p>"
                )
            project_choice = (
                "<label>"
                f"<input name=\"project_id\" type=\"checkbox\" value=\"{escape(project.id)}\" checked>"
                f"Koppla till {escape(project.name)}</label>"
            )

        return f"""
    {context}
    <form method="post" action="{action}">
      {hidden_document}
      <label for="content">Ny notering</label>
      <textarea id="content" name="content" autofocus required></textarea>
      {source_location}
      {project_choice}
      <button type="submit">Spara</button>
    </form>
"""

    def _render_project_link_form(self, project: Project, notes: list[object]) -> str:
        options = "\n".join(
            f"<option value=\"{escape(note.id)}\">{escape(note.content)}</option>"
            for note in notes
        )
        if not options:
            options = "<option value=\"\">Inga fristående noteringar</option>"
        return f"""
    <section aria-labelledby="link-note">
      <h2 id="link-note">Koppla befintlig notering</h2>
      <form method="post" action="/projects/{escape(project.id)}/links">
        <label for="object_id">Knowledge Object</label>
        <select id="object_id" name="object_id">
          {options}
        </select>
        <button type="submit">Koppla</button>
      </form>
    </section>
"""

    def _render_inbox_document(self, document: Document) -> str:
        project_options = "\n".join(
            (
                "<label>"
                f"<input name=\"project_id\" type=\"checkbox\" value=\"{escape(project.id)}\""
                f"{' checked' if project.id in document.project_ids else ''}>"
                f"{escape(project.name)}</label>"
            )
            for project in self.archive.list_projects()
        )
        if not project_options:
            project_options = "<p>Inga projects finns ännu.</p>"
        original_filename = (
            f"<p>Originalfil: {escape(document.original_filename)}</p>"
            if document.original_filename
            else ""
        )

        return f"""
      <article>
        <h3><a href="/documents/{escape(document.id)}">{escape(document.title)}</a></h3>
        {original_filename}
        <p>Status: {escape(document.inbox_status)}</p>
        <form method="post" action="/inbox/documents/{escape(document.id)}">
          <fieldset>
            <legend>Koppla till projects</legend>
            {project_options}
          </fieldset>
          <button name="decision" type="submit" value="done">Klar</button>
          <button name="decision" type="submit" value="later">Senare</button>
          <button name="decision" type="submit" value="trashed">Kasta</button>
        </form>
      </article>
"""

    def _render_ai_inbox_candidates(self, candidates: list[KnowledgeObject]) -> str:
        grouped = self._group_ai_candidates_by_document(candidates)
        if not grouped:
            return ""
        summary = (
            f"<p>{len(grouped)} document har obearbetade AI-granskningar.</p>"
        )
        rendered_items = "\n".join(
            self._render_ai_inbox_document(document, pending_count)
            for document, pending_count in grouped
        )
        return f"{summary}\n{rendered_items}"

    def _group_ai_candidates_by_document(
        self, candidates: list[KnowledgeObject]
    ) -> list[tuple[Document, int]]:
        counts: dict[str, int] = {}
        for candidate in candidates:
            if not candidate.document_id:
                continue
            counts[candidate.document_id] = counts.get(candidate.document_id, 0) + 1
        documents = [
            (self.archive.get_document(document_id), pending_count)
            for document_id, pending_count in counts.items()
        ]
        documents.sort(key=lambda item: item[0].title.casefold())
        return documents

    def _render_ai_inbox_document(
        self, document: Document, pending_count: int
    ) -> str:
        document_href = f"/documents/{escape(document.id)}"
        candidate_text = (
            "1 AI-kandidat väntar"
            if pending_count == 1
            else f"{pending_count} AI-kandidater väntar"
        )
        return f"""
      <article data-ai-inbox-document-id="{escape(document.id)}">
        <h3>{escape(document.title)}</h3>
        <p>{candidate_text}</p>
        <p><a href="{document_href}">Granska</a></p>
      </article>
"""

    def _render_ai_candidate_groups(self, candidates: list[KnowledgeObject]) -> str:
        groups = (
            ("Summary", "Summary"),
            ("Claims", "Claim"),
            ("Insights", "Insight"),
            ("Questions", "Question"),
            ("Project Suggestions", "ProjectSuggestion"),
        )
        rendered_groups: list[str] = []
        for heading, semantic_type in groups:
            items = [
                candidate
                for candidate in self._sort_ai_candidates_for_review(candidates)
                if candidate.semantic_type == semantic_type
            ]
            if not items:
                continue
            rendered_groups.append(
                f"""
      <section aria-labelledby="ai-{escape(semantic_type)}">
        <h3 id="ai-{escape(semantic_type)}">{escape(heading)}</h3>
        {"".join(self._render_ai_candidate(candidate) for candidate in items)}
      </section>
"""
            )
        return "\n".join(rendered_groups)

    def _visible_ai_candidates_for_inbox(self) -> list[KnowledgeObject]:
        return [
            candidate
            for candidate in self.archive.list_ai_candidates_for_inbox()
            if self._ai_candidate_should_be_visible(candidate)
        ]

    def _visible_ai_candidates_for_document(
        self, document: Document
    ) -> list[KnowledgeObject]:
        return [
            candidate
            for candidate in self.archive.list_ai_candidates_for_inbox()
            if candidate.document_id == document.id
            and self._ai_candidate_should_be_visible(candidate, document=document)
        ]

    def _ai_candidate_should_be_visible(
        self, candidate: KnowledgeObject, document: Document | None = None
    ) -> bool:
        if candidate.semantic_type != "ProjectSuggestion":
            return True
        if not candidate.project_ids:
            return True
        if document is None and candidate.document_id:
            document = self.archive.get_document(candidate.document_id)
        if document is None:
            return True
        return not any(
            project_id in document.project_ids for project_id in candidate.project_ids
        )

    def _sort_ai_candidates_for_review(
        self, candidates: list[KnowledgeObject]
    ) -> list[KnowledgeObject]:
        order = {
            "Summary": 0,
            "Claim": 1,
            "Insight": 2,
            "Question": 3,
            "ProjectSuggestion": 4,
        }
        return sorted(
            candidates,
            key=lambda item: (
                order.get(item.semantic_type, 99),
                item.created_at,
                item.id,
            ),
        )

    def _render_ai_candidate(self, candidate: KnowledgeObject) -> str:
        if candidate.semantic_type == "ProjectSuggestion":
            return self._render_project_suggestion_candidate(candidate)
        rejection_options = "\n".join(
            f"<option value=\"{escape(reason)}\">{escape(reason)}</option>"
            for reason in (
                "",
                "irrelevant",
                "trivial",
                "felaktig",
                "överdriven",
                "redan känd",
                "annat",
            )
        )
        document_link = ""
        if candidate.document_id:
            document = self.archive.get_document(candidate.document_id)
            document_link = (
                f"<p>Källa: <a href=\"/documents/{escape(document.id)}\">"
                f"{escape(document.title)}</a></p>"
            )
        confidence = (
            f"<p>Confidence: {escape(candidate.confidence)}</p>"
            if candidate.confidence
            else ""
        )
        provenance = (
            f"{escape(candidate.ai_provider)} / {escape(candidate.ai_model)} / "
            f"{escape(candidate.prompt_version)}"
        )
        return f"""
      <article data-ai-review-candidate-id="{escape(candidate.id)}">
        <h3>{escape(candidate.semantic_type)}</h3>
        {document_link}
        <p>{escape(candidate.original_content or candidate.content)}</p>
        {confidence}
        <p>Proveniens: AI - {provenance}</p>
        <form method="post" action="/documents/{escape(candidate.document_id)}/candidates/{escape(candidate.id)}">
          <label for="content-{escape(candidate.id)}">Formulering</label>
          <textarea id="content-{escape(candidate.id)}" name="content">{escape(candidate.content)}</textarea>
          <label for="reason-{escape(candidate.id)}">Avvisningsorsak</label>
          <select id="reason-{escape(candidate.id)}" name="rejection_reason">
            {rejection_options}
          </select>
          <button name="decision" type="submit" value="accept">Acceptera</button>
          <button name="decision" type="submit" value="later">Senare</button>
          <button name="decision" type="submit" value="reject">Avvisa</button>
        </form>
      </article>
"""

    def _render_project_suggestion_candidate(self, candidate: KnowledgeObject) -> str:
        project_name = "Okänt project"
        project_id = candidate.project_ids[0] if candidate.project_ids else ""
        if project_id:
            project = self.archive.get_project(project_id)
            project_name = project.name
        confidence = (
            f"<p>Confidence: {escape(candidate.confidence)}</p>"
            if candidate.confidence
            else ""
        )
        provenance = (
            f"{escape(candidate.ai_provider)} / {escape(candidate.ai_model)} / "
            f"{escape(candidate.prompt_version)}"
        )
        return f"""
      <article data-ai-review-candidate-id="{escape(candidate.id)}">
        <h3>{escape(candidate.semantic_type)}</h3>
        <p>Föreslaget project: {escape(project_name)}</p>
        <p>{escape(candidate.original_content or candidate.content)}</p>
        {confidence}
        <p>Proveniens: AI - {provenance}</p>
        <form method="post" action="/documents/{escape(candidate.document_id)}/candidates/{escape(candidate.id)}">
          <button name="decision" type="submit" value="link_project">Koppla till projekt</button>
          <button name="decision" type="submit" value="reject">Avvisa</button>
        </form>
      </article>
"""

    def _render_document_ai_panel(
        self,
        document: Document,
        candidates: list[KnowledgeObject],
        runs: list[AiRunRecord],
    ) -> str:
        text_available = (
            bool(document.extracted_text_path)
            and self.archive.extracted_text_file_path(document.id).exists()
        )
        ai_action = (
            f"<p><a href=\"/documents/{escape(document.id)}/ai\">Förbered AI-analys</a></p>"
            if text_available
            else "<p>AI-analys kräver extraherad dokumenttext.</p>"
        )
        rendered_candidates = self._render_ai_candidate_groups(candidates)
        if not rendered_candidates:
            rendered_candidates = "<p>Inga väntande AI-kandidater för dokumentet.</p>"
        rendered_runs = "\n".join(
            (
                f"<li>{escape(run.status)} - {escape(run.model)} - "
                f"{run.actual_input_tokens}/{run.actual_output_tokens} token - "
                f"{run.actual_cost:.6f} {escape(run.currency)}</li>"
            )
            for run in runs
        )
        if not rendered_runs:
            rendered_runs = "<li>Ingen AI-körning ännu.</li>"
        return f"""
    <section aria-labelledby="document-ai">
      <h2 id="document-ai">AI</h2>
      {ai_action}
      <h3>Väntande kandidater</h3>
      {rendered_candidates}
      <h3>AI-körningar</h3>
      <ul>{rendered_runs}</ul>
    </section>
"""

    def _render_relation_form(self, notes: list[object]) -> str:
        options = "\n".join(
            f"<option value=\"{escape(note.id)}\">{escape(note.content)}</option>"
            for note in notes
        )
        if not options:
            options = "<option value=\"\">Inga kopplade noteringar</option>"
        return f"""
    <section aria-labelledby="new-relation">
      <h2 id="new-relation">Relation</h2>
      <form method="post" action="/relations">
        <label for="source_id">Från</label>
        <select id="source_id" name="source_id">
          {options}
        </select>
        <label for="target_id">Till</label>
        <select id="target_id" name="target_id">
          {options}
        </select>
        <label for="comment">Kommentar</label>
        <input id="comment" name="comment" type="text">
        <button type="submit">Skapa relation</button>
      </form>
    </section>
"""

    def _render_notes(self, notes: list[object], empty_text: str) -> str:
        rendered_notes = "\n".join(
            self._render_note(note.id, note.content, note.source_location)
            for note in notes
        )
        if not rendered_notes:
            return f"<li><p>{escape(empty_text)}</p></li>"
        return rendered_notes

    def _render_note(self, note_id: str, content: str, source_location: str = "") -> str:
        source = ""
        if source_location:
            source = f"<small>Källa: {escape(source_location)}</small>"
        return f"<li><p>{escape(content)}</p><small>ID: {escape(note_id)}</small>{source}</li>"

    def _accepted_recent_notes(self) -> list[KnowledgeObject]:
        return [
            note
            for note in self.archive.list_recent_knowledge_objects()
            if note.review_status == "accepted"
        ]

    def _read_document_text(self, document: Document) -> str:
        if not document.extracted_text_path:
            raise AiProviderError(
                "Dokumentet saknar extraherad text och kan inte AI-analyseras."
            )
        text_path = self.archive.extracted_text_file_path(document.id)
        if not text_path.exists():
            raise AiProviderError("Dokumentets extraherade text saknas i Archive.")
        text = text_path.read_text(encoding="utf-8").strip()
        if not text:
            raise AiProviderError("Dokumentets extraherade text är tom.")
        return text

    def _estimate_document_ai_cost(self, text: str) -> AiCost:
        input_tokens = estimate_input_tokens(text)
        return estimate_cost(
            input_tokens=input_tokens,
            output_tokens=DEFAULT_MAX_OUTPUT_TOKENS,
            model=self.ai_model,
        )

    def _make_ai_provider(self) -> AiProvider:
        if self.ai_provider_override:
            return self.ai_provider_override
        if self.ai_provider_name == "mock":
            return MockAiProvider()
        if self.ai_provider_name == "openai":
            return OpenAiProvider(load_openai_api_key(self.secrets_path))
        raise MissingCredentialError("Ingen känd AI-provider är konfigurerad.")

    def _semantic_type_for_capability(self, capability: str) -> str:
        return {
            "summary": "Summary",
            "candidate_insight": "Insight",
            "candidate_claim": "Claim",
            "candidate_question": "Question",
            "project_suggestion": "ProjectSuggestion",
        }.get(capability, "unknown")

    def _format_cost(self, cost: AiCost) -> str:
        if cost.method == "unknown_model_price":
            return "Kan inte beräknas tillförlitligt för vald modell."
        return f"{cost.estimated_cost:.6f} {escape(cost.currency)}"

    def _page(self, title: str, body: str) -> str:
        return f"""<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    body {{
      color: #111;
      background: #fff;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
      margin: 0;
    }}
    main {{
      max-width: 48rem;
      margin: 0 auto;
      padding: 1rem;
    }}
    textarea {{
      box-sizing: border-box;
      width: 100%;
      min-height: 10rem;
      font: inherit;
      padding: 0.75rem;
      border: 1px solid #555;
    }}
    input, select {{
      box-sizing: border-box;
      width: 100%;
      font: inherit;
      padding: 0.55rem;
      border: 1px solid #555;
      margin-bottom: 0.75rem;
    }}
    input[type="checkbox"] {{
      width: auto;
      margin-right: 0.35rem;
    }}
    button {{
      font: inherit;
      margin-top: 0.75rem;
      padding: 0.55rem 0.85rem;
      border: 1px solid #111;
      background: #f7f7f7;
      color: #111;
    }}
    ul {{
      padding-left: 1.25rem;
    }}
  </style>
</head>
<body>
  <nav aria-label="Huvudnavigation">
    <a href="/inbox">Inbox</a>
    <a href="/capture">Capture</a>
    <a href="/documents">Documents</a>
    <a href="/projects">Projects</a>
  </nav>
  <main>
{body}
  </main>
  <script>
    const captureField = document.getElementById("content");
    if (captureField) {{
      const captureForm = captureField.form;

      captureField.addEventListener("keydown", (event) => {{
        if (event.key === "Enter" && !event.shiftKey) {{
          event.preventDefault();
          if (captureForm.requestSubmit) {{
            captureForm.requestSubmit();
          }} else {{
            captureForm.submit();
          }}
        }}
      }});
    }}
  </script>
</body>
</html>
"""


def make_handler(app: CaptureApp) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/inbox"):
                self._send_html(app.render_inbox())
                return
            if parsed.path == "/capture":
                params = parse_qs(parsed.query)
                document_id = params.get("document_id", [""])[0]
                project_id = params.get("project_id", [""])[0]
                document = app.archive.get_document(document_id) if document_id else None
                project = app.archive.get_project(project_id) if project_id else None
                self._send_html(app.render_capture(document=document, project=project))
                return
            if parsed.path == "/documents":
                self._send_html(app.render_documents())
                return
            if parsed.path == "/projects":
                self._send_html(app.render_projects())
                return
            if parsed.path == "/trash":
                self._send_html(app.render_trash())
                return
            if parsed.path.startswith("/documents/"):
                document_path = unquote(parsed.path.removeprefix("/documents/"))
                if document_path.endswith("/original"):
                    document_id = document_path.removesuffix("/original")
                    self._send_pdf(app.archive.original_file_path(document_id))
                    return
                if document_path.endswith("/ai"):
                    document_id = document_path.removesuffix("/ai")
                    self._send_html(app.render_document_ai_confirmation(document_id))
                    return
                document_id = document_path
                self._send_html(app.render_document(document_id))
                return
            if parsed.path.startswith("/projects/"):
                project_id = unquote(parsed.path.removeprefix("/projects/"))
                self._send_html(app.render_project(project_id))
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)

            if parsed.path == "/documents":
                document = app.create_document_from_form(body)
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", f"/documents/{document.id}")
                self.end_headers()
                return

            if parsed.path == "/projects":
                project = app.create_project_from_form(body)
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", f"/projects/{project.id}")
                self.end_headers()
                return

            if parsed.path == "/relations":
                app.create_relation_from_form(body)
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/projects")
                self.end_headers()
                return

            if parsed.path.startswith("/inbox/documents/"):
                document_id = unquote(parsed.path.removeprefix("/inbox/documents/"))
                app.update_inbox_document_from_form(document_id, body)
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/inbox")
                self.end_headers()
                return

            if parsed.path.startswith("/inbox/candidates/"):
                object_id = unquote(parsed.path.removeprefix("/inbox/candidates/"))
                try:
                    candidate = app.review_ai_candidate_from_form(object_id, body)
                except ValueError as error:
                    self.send_error(HTTPStatus.BAD_REQUEST, str(error))
                    return
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header(
                    "Location",
                    f"/documents/{candidate.document_id}"
                    if candidate.document_id
                    else "/inbox",
                )
                self.end_headers()
                return

            if parsed.path.startswith("/documents/") and "/candidates/" in parsed.path:
                document_path = unquote(parsed.path.removeprefix("/documents/"))
                document_id, separator, object_id = document_path.partition("/candidates/")
                if not separator:
                    self.send_error(HTTPStatus.BAD_REQUEST)
                    return
                existing_candidate = app.archive.get_knowledge_object(object_id)
                if existing_candidate.document_id and existing_candidate.document_id != document_id:
                    self.send_error(HTTPStatus.BAD_REQUEST, "Candidate belongs to another document.")
                    return
                try:
                    candidate = app.review_ai_candidate_from_form(object_id, body)
                except ValueError as error:
                    self.send_error(HTTPStatus.BAD_REQUEST, str(error))
                    return
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", f"/documents/{document_id}")
                self.end_headers()
                return

            if parsed.path.startswith("/documents/") and parsed.path.endswith("/ai/run"):
                document_path = unquote(parsed.path.removeprefix("/documents/"))
                document_id = document_path.removesuffix("/ai/run")
                try:
                    app.run_document_ai_analysis_from_form(document_id, body)
                except AiProviderError as error:
                    document = app.archive.get_document(document_id)
                    self._send_html(app.render_ai_message(document, str(error)))
                    return
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/inbox")
                self.end_headers()
                return

            if parsed.path.startswith("/trash/documents/") and parsed.path.endswith("/restore"):
                document_path = unquote(parsed.path.removeprefix("/trash/documents/"))
                document_id = document_path.removesuffix("/restore")
                app.archive.restore_document(document_id)
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", "/trash")
                self.end_headers()
                return

            if parsed.path.startswith("/projects/"):
                project_path = unquote(parsed.path.removeprefix("/projects/"))
                if project_path.endswith("/links"):
                    project_id = project_path.removesuffix("/links")
                    app.link_note_to_project_from_form(project_id, body)
                    self.send_response(HTTPStatus.SEE_OTHER)
                    self.send_header("Location", f"/projects/{project_id}")
                    self.end_headers()
                    return

                app.update_project_from_form(project_path, body)
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", f"/projects/{project_path}")
                self.end_headers()
                return

            if parsed.path != "/capture":
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            app.create_note_from_form(body)
            params = parse_qs(parsed.query)
            document_id = params.get("document_id", [""])[0]
            project_id = params.get("project_id", [""])[0]
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header(
                "Location",
                f"/documents/{document_id}"
                if document_id
                else f"/projects/{project_id}"
                if project_id
                else "/capture",
            )
            self.end_headers()

        def log_message(self, format: str, *args: object) -> None:
            return

        def _send_html(self, html: str) -> None:
            encoded = html.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _send_pdf(self, path: Path) -> None:
            if not path.exists():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            content = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    return Handler


def main(config_path: str | None = None) -> None:
    config = load_config(config_path)
    ensure_app_directories(config)
    app = CaptureApp(Archive(config.archive_root), config=config)
    server = ThreadingHTTPServer((config.host, config.port), make_handler(app))
    print(f"Dokumentverkstad Capture körs på http://{config.host}:{config.port}/")
    server.serve_forever()
