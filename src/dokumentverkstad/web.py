from __future__ import annotations

from dataclasses import dataclass
from getpass import getpass
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from time import perf_counter
from typing import Callable
from urllib.parse import parse_qs, unquote, urlparse
from uuid import uuid4

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
from .diagnostics import runtime_log_sink
from .document import Document
from .health import check_health
from .knowledge import KnowledgeObject
from .project import Project
from .secrets import (
    SecretsError,
    encrypted_secrets_exists,
    load_openai_api_key,
    unlock_encrypted_secrets,
)
from .statistics import (
    AiStatistics,
    CandidateReviewSummary,
    UsageSummary,
    build_ai_statistics,
)


@dataclass(frozen=True)
class DocumentListItem:
    document: Document
    ai_analyzed: bool
    capture_count: int


@dataclass(frozen=True)
class AiCandidateVisibilityContext:
    documents: dict[str, Document]
    project_ids: set[str]


class CaptureApp:
    def __init__(
        self,
        archive: Archive,
        config: AppConfig | None = None,
        ai_provider: AiProvider | None = None,
        log: Callable[[str], None] | None = None,
        slow_request_threshold_seconds: float = 0.5,
        render_step_threshold_seconds: float = 0.05,
    ):
        self.archive = archive
        self.config = config
        self.ai_provider_override = ai_provider
        self.ai_provider_name = (
            ai_provider.name if ai_provider else config.ai_provider if config else DEFAULT_AI_PROVIDER
        )
        self.ai_model = config.ai_model if config else DEFAULT_AI_MODEL
        self.ai_max_output_tokens = (
            config.ai_max_output_tokens if config else DEFAULT_MAX_OUTPUT_TOKENS
        )
        self.upload_max_bytes = config.upload_max_bytes if config else 250 * 1024 * 1024
        self.secrets_path = (
            config.secrets_path if config else archive.root.parent / "secrets.toml"
        )
        self.encrypted_secrets_path = (
            config.encrypted_secrets_path
            if config
            else archive.root.parent / "secrets.enc"
        )
        self.log = log
        self.slow_request_threshold_seconds = slow_request_threshold_seconds
        self.render_step_threshold_seconds = render_step_threshold_seconds
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
            title="Notering",
            active_nav="capture",
            context=self._render_capture_context(document=document, project=project),
            body=f"""
    <h1>Notering</h1>
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
        started = perf_counter()
        all_documents = self._timed_render_step(
            "inbox",
            "list_documents",
            self.archive.list_documents,
        )
        documents = [
            document
            for document in all_documents
            if document.inbox_status in {"new", "later"}
        ]
        documents.sort(key=lambda item: item.updated_at, reverse=True)
        knowledge_objects = self._timed_render_step(
            "inbox",
            "list_knowledge_objects",
            self.archive.list_knowledge_objects,
        )
        projects = self._timed_render_step(
            "inbox",
            "list_projects",
            self.archive.list_projects,
        )
        visibility = AiCandidateVisibilityContext(
            documents={document.id: document for document in all_documents},
            project_ids={project.id for project in projects},
        )
        candidates = self._visible_ai_candidates_for_inbox(
            knowledge_objects, visibility
        )
        queue_count = len(documents) + len(candidates)
        rendered_documents = "\n".join(
            self._render_inbox_document(document, projects) for document in documents
        )
        rendered_candidates = self._render_ai_inbox_candidates(
            candidates, visibility.documents
        )
        empty_notice = (
            '<p class="empty-state">Inget väntar på behandling.</p>'
            if not documents and not candidates
            else ""
        )
        if not rendered_documents:
            rendered_documents = (
                '<p class="empty-state">Inga dokument väntar på beslut.</p>'
            )
        if not rendered_candidates:
            rendered_candidates = (
                '<p class="empty-state">Inga AI-förslag väntar på granskning.</p>'
            )
        context = f"""
    <h2 class="context-title">Inkorg</h2>
    <div class="context-group">
      <p class="system-label">Väntande</p>
      <p class="queue-count">{queue_count} objekt</p>
    </div>
    <div class="context-group">
      <p class="system-label">Snabblänkar</p>
      <nav class="context-actions" aria-label="Inkorgslänkar">
        <a href="/upload">Lägg till PDF</a>
        <a href="/trash">Papperskorg</a>
        <a href="/admin">Administration</a>
      </nav>
    </div>
"""

        html = self._page(
            title="Inkorg",
            active_nav="inbox",
            context=context,
            body=f"""
    <h1>Inkorg</h1>
    <section class="queue-summary" aria-labelledby="inbox-queue">
      <h2 id="inbox-queue">Väntande</h2>
      <p><span class="queue-summary__number">{queue_count}</span> objekt behöver beslut eller granskning.</p>
      {empty_notice}
    </section>
    <section aria-labelledby="inbox-documents">
      <h2 id="inbox-documents">Dokument som väntar</h2>
      {rendered_documents}
    </section>
    <section aria-labelledby="inbox-candidates">
      <h2 id="inbox-candidates">AI-granskning</h2>
      {rendered_candidates}
    </section>
""",
        )
        self._log_render_total("inbox", started)
        return html

    def render_upload(self, message: str = "", error: str = "") -> str:
        feedback = ""
        if message:
            feedback = f"<p>{escape(message)}</p>"
        if error:
            feedback = f"<p>{escape(error)}</p>"
        return self._page(
            title="Lägg till PDF",
            active_nav="inbox",
            body=f"""
    <p><a href="/inbox">Inkorg</a></p>
    <h1>Lägg till PDF</h1>
    {feedback}
    <form method="post" action="/upload" enctype="multipart/form-data">
      <label for="pdf">PDF-fil</label>
      <input id="pdf" name="pdf" type="file" accept="application/pdf,.pdf" required>
      <button type="submit">Ladda upp</button>
    </form>
""",
        )

    def render_trash(self) -> str:
        documents = self.archive.list_trashed_documents()
        rendered_documents = "\n".join(
            self._render_trashed_document(document)
            for document in documents
        )
        if not rendered_documents:
            rendered_documents = "<li>Papperskorgen är tom.</li>"

        return self._page(
            title="Papperskorg",
            active_nav="inbox",
            body=f"""
    <h1>Papperskorg</h1>
    <ul>
      {rendered_documents}
    </ul>
    <p><a href="/inbox">Inkorg</a></p>
""",
        )

    def _render_trashed_document(self, document: Document) -> str:
        references = self.archive.document_reference_summary(document.id)
        reference_note = (
            f"<p>Permanent radering spärrad: {escape(', '.join(references))} refererar till dokumentet.</p>"
            if references
            else "<p>Permanent radering kan inte ångras genom vanlig återställning.</p>"
        )
        delete_form = (
            ""
            if references
            else f"""
        <form method="post" action="/trash/documents/{escape(document.id)}/delete">
          <label>
            <input type="checkbox" name="confirm_delete" value="yes" required>
            Radera permanent
          </label>
          <button type="submit">Radera permanent</button>
        </form>
"""
        )
        metadata = document.author or "Okänt upphov"
        if document.year:
            metadata = f"{metadata} | {document.year}"
        return f"""
      <li>
        <p>Dokument</p>
        <a href="/documents/{escape(document.id)}">{escape(document.title)}</a>
        <p>{escape(metadata)}</p>
        <form method="post" action="/trash/documents/{escape(document.id)}/restore">
          <button type="submit">Återställ</button>
        </form>
        {reference_note}
        {delete_form}
      </li>
"""

    def render_admin(self) -> str:
        statistics = build_ai_statistics(self.archive)
        health_section = self._render_health_section()
        empty_notice = (
            "<p>Ingen AI-användning ännu.</p>"
            if statistics.completed_runs == 0 and statistics.candidate_reviews.total == 0
            else ""
        )
        return self._page(
            title="Administration",
            body=f"""
    <h1>Administration</h1>
    {empty_notice}
    {health_section}
    <section aria-labelledby="ai-totals">
      <h2 id="ai-totals">AI-statistik</h2>
      {self._render_ai_statistics_totals(statistics)}
    </section>
    <section aria-labelledby="ai-models">
      <h2 id="ai-models">Per modell</h2>
      {self._render_usage_summary_table(statistics.usage_by_model, "modell")}
    </section>
    <section aria-labelledby="ai-prompts">
      <h2 id="ai-prompts">Per promptversion</h2>
      {self._render_usage_summary_table(statistics.usage_by_prompt_version, "promptversion")}
    </section>
    <section aria-labelledby="ai-months">
      <h2 id="ai-months">Per månad</h2>
      {self._render_usage_summary_table(statistics.usage_by_month, "månad")}
    </section>
    <section aria-labelledby="ai-reviews">
      <h2 id="ai-reviews">Granskning per kandidattyp</h2>
      {self._render_candidate_review_table(statistics.review_by_candidate_type)}
    </section>
    <section aria-labelledby="ai-rejection-reasons">
      <h2 id="ai-rejection-reasons">Avvisningsorsaker</h2>
      {self._render_rejection_reasons(statistics.rejection_reasons)}
    </section>
""",
        )

    def _render_health_section(self) -> str:
        if not self.config:
            return ""
        health = check_health(self.config)
        messages = "\n".join(
            f"<li>{escape(message)}</li>" for message in health.messages
        )
        if not messages:
            messages = "<li>Inga kända driftproblem.</li>"
        return f"""
    <section aria-labelledby="health">
      <h2 id="health">Driftstatus</h2>
      <dl>
        <dt>Status</dt>
        <dd>{escape(health.status)}</dd>
        <dt>Arkiv</dt>
        <dd>{'OK' if health.archive_readable else 'problem'}</dd>
        <dt>Index</dt>
        <dd>{'OK' if health.index_exists else 'saknas'}</dd>
        <dt>Ingest väntande</dt>
        <dd>{health.counts.ingest_pending}</dd>
        <dt>Ingest misslyckade</dt>
        <dd>{health.counts.ingest_failed}</dd>
        <dt>AI väntande</dt>
        <dd>{health.counts.ai_planned}</dd>
        <dt>AI pågående</dt>
        <dd>{health.counts.ai_running}</dd>
        <dt>AI misslyckade</dt>
        <dd>{health.counts.ai_failed}</dd>
        <dt>OpenAI credential</dt>
        <dd>{escape(health.credential_status)}</dd>
        <dt>Papperskorg</dt>
        <dd>{health.counts.trash_objects}</dd>
      </dl>
      <ul>{messages}</ul>
    </section>
"""

    def render_documents(
        self,
        query: str = "",
        sort: str = "year",
        ai_status: str = "",
        project_id: str = "",
    ) -> str:
        started = perf_counter()
        projects = self._timed_render_step(
            "documents",
            "list_projects",
            self.archive.list_projects,
        )
        project_names = {project.id: project.name for project in projects}
        items = self._timed_render_step(
            "documents",
            "document_list_items",
            self._document_list_items,
        )
        total_count = len(items)
        items = self._filter_document_list_items(
            items,
            query=query,
            ai_status=ai_status,
            project_id=project_id,
        )
        items = self._sort_document_list_items(items, sort=sort)
        rendered_documents = "\n".join(
            self._render_document_list_item(item, project_names) for item in items
        )
        if not rendered_documents:
            rendered_documents = "<li>Inga dokument ännu.</li>"

        selected_sort = sort if sort in {"latest", "title", "year"} else "year"
        selected_ai_status = (
            ai_status if ai_status in {"analyzed", "not_analyzed"} else ""
        )
        selected_project_id = project_id if project_id in project_names else ""
        project_options = "\n".join(
            f'<option value="{escape(project.id)}"'
            f'{" selected" if project.id == selected_project_id else ""}>'
            f"{escape(project.name)}</option>"
            for project in projects
        )

        html = self._page(
            title="Dokument",
            active_nav="documents",
            body=f"""
    <h1>Dokument</h1>
    <div class="documents-heading">
      <h2>Registrerade dokument</h2>
      <p class="metadata-provenance">{len(items)} av {total_count}</p>
    </div>
    <ul class="document-list">
      {rendered_documents}
    </ul>
""",
            context=f"""
    <h2 class="context-title">Dokument</h2>
    <form class="filter-form" id="documents-filter" method="get" action="/documents">
      <div class="filter-field">
        <label for="document-filter-q">Sök</label>
        <input id="document-filter-q" name="q" type="search" value="{escape(query)}">
      </div>
      <div class="filter-field">
        <label for="document-sort">Sortering</label>
        <select id="document-sort" name="sort">
          <option value="latest"{" selected" if selected_sort == "latest" else ""}>Senast tillagd</option>
          <option value="title"{" selected" if selected_sort == "title" else ""}>Titel</option>
          <option value="year"{" selected" if selected_sort == "year" else ""}>Utgivningsår</option>
        </select>
      </div>
      <div class="filter-field">
        <label for="document-project">Projekt</label>
        <select id="document-project" name="project_id">
          <option value=""{" selected" if selected_project_id == "" else ""}>Alla</option>
          {project_options}
        </select>
      </div>
      <div class="filter-field">
        <label for="document-ai-status">AI-status</label>
        <select id="document-ai-status" name="ai_status">
          <option value=""{" selected" if selected_ai_status == "" else ""}>Alla</option>
          <option value="analyzed"{" selected" if selected_ai_status == "analyzed" else ""}>AI-analyserade</option>
          <option value="not_analyzed"{" selected" if selected_ai_status == "not_analyzed" else ""}>Ej AI-analyserade</option>
        </select>
      </div>
      <button type="submit">Filtrera</button>
    </form>
    <div class="context-group context-actions">
      <a href="/documents">Nollställ filter</a>
      <a href="/documents/new">Skapa dokument manuellt</a>
      <a href="/capture">Notering utan dokument</a>
    </div>
""",
        )
        self._log_render_total("documents", started)
        return html

    def render_new_document(self) -> str:
        return self._page(
            title="Skapa dokument manuellt",
            active_nav="documents",
            body="""
    <p><a href="/documents">Dokument</a></p>
    <h1>Skapa dokument manuellt</h1>
    <form method="post" action="/documents">
      <label for="title">Titel</label>
      <input id="title" name="title" type="text" required>
      <label for="author">Upphov</label>
      <input id="author" name="author" type="text">
      <label for="year">Utgivningsår</label>
      <input id="year" name="year" type="text" inputmode="numeric" pattern="\\d{4}">
      <button type="submit">Skapa dokument</button>
    </form>
""",
        )

    def _document_list_items(self) -> list[DocumentListItem]:
        documents = self.archive.list_documents()
        accepted_user_captures = [
            item
            for item in self.archive.list_knowledge_objects()
            if item.creator == "user"
            and item.review_status == "accepted"
            and item.document_id
        ]
        completed_ai_document_ids = {
            run.document_id
            for run in self.archive.list_ai_runs()
            if run.status == "completed"
        }

        capture_counts: dict[str, int] = {}
        for capture in accepted_user_captures:
            capture_counts[capture.document_id] = (
                capture_counts.get(capture.document_id, 0) + 1
            )

        return [
            DocumentListItem(
                document=document,
                ai_analyzed=document.id in completed_ai_document_ids,
                capture_count=capture_counts.get(document.id, 0),
            )
            for document in documents
        ]

    def _filter_document_list_items(
        self,
        items: list[DocumentListItem],
        query: str,
        ai_status: str,
        project_id: str,
    ) -> list[DocumentListItem]:
        clean_query = query.strip().casefold()

        def matches(item: DocumentListItem) -> bool:
            document = item.document
            if clean_query:
                searchable = " ".join(
                    value
                    for value in (document.title, document.author, document.year)
                    if value
                ).casefold()
                if clean_query not in searchable:
                    return False
            if ai_status == "analyzed" and not item.ai_analyzed:
                return False
            if ai_status == "not_analyzed" and item.ai_analyzed:
                return False
            if project_id and project_id not in document.project_ids:
                return False
            return True

        return [item for item in items if matches(item)]

    def _sort_document_list_items(
        self, items: list[DocumentListItem], sort: str
    ) -> list[DocumentListItem]:
        if sort == "title":
            return sorted(
                items,
                key=lambda item: (
                    item.document.title.casefold(),
                    item.document.year or "9999",
                    item.document.created_at,
                    item.document.id,
                ),
            )
        if sort == "year":
            return sorted(
                items,
                key=lambda item: (
                    item.document.year == "",
                    -(int(item.document.year) if item.document.year.isdigit() else 0),
                    item.document.title.casefold(),
                    item.document.id,
                ),
            )
        return sorted(
            items,
            key=lambda item: (
                item.document.created_at,
                item.document.title.casefold(),
                item.document.id,
            ),
            reverse=True,
        )

    def _render_document_list_item(
        self, item: DocumentListItem, project_names: dict[str, str]
    ) -> str:
        document = item.document
        metadata = []
        if document.year:
            metadata.append(escape(document.year))
        if document.author:
            metadata.append(escape(document.author))
        metadata.append(self._format_capture_count(item.capture_count))
        project_labels = [
            escape(project_names[project_id])
            for project_id in document.project_ids
            if project_id in project_names
        ]
        metadata_text = " | ".join(metadata)
        ai_status = "AI-analyserad" if item.ai_analyzed else "Ej AI-analyserad"
        status_class = " is-complete" if item.ai_analyzed else ""
        projects = (
            f'<p class="document-list__projects">{" | ".join(project_labels)}</p>'
            if project_labels
            else ""
        )
        return (
            '<li class="document-list__item">'
            "<div>"
            f'<a class="document-list__title" href="/documents/{escape(document.id)}">{escape(document.title)}</a>'
            f'<p class="document-list__metadata">{metadata_text}</p>'
            "</div>"
            f'<p class="document-list__status"><span class="status-mark{status_class}" aria-hidden="true"></span>{ai_status}</p>'
            f"{projects}"
            "</li>"
        )

    def _format_capture_count(self, count: int) -> str:
        if count == 1:
            return "1 egen notering"
        return f"{count} egna noteringar"

    def render_document(self, document_id: str) -> str:
        started = perf_counter()
        document = self._timed_render_step(
            "document",
            "get_document",
            lambda: self.archive.get_document(document_id),
        )
        knowledge_objects = self._timed_render_step(
            "document",
            "list_knowledge_objects",
            self.archive.list_knowledge_objects,
        )
        projects = self._timed_render_step(
            "document",
            "list_projects",
            self.archive.list_projects,
        )
        runs = self._timed_render_step(
            "document",
            "list_ai_runs_for_document",
            lambda: self.archive.list_ai_runs_for_document(document.id),
        )
        notes = [
            item
            for item in knowledge_objects
            if item.document_id == document.id and item.review_status == "accepted"
        ]
        notes.sort(key=lambda item: item.created_at, reverse=True)
        visibility = AiCandidateVisibilityContext(
            documents={document.id: document},
            project_ids={project.id for project in projects},
        )
        candidates = self._visible_ai_candidates_for_document(
            document, knowledge_objects, visibility
        )
        linked_projects = [project for project in projects if project.id in document.project_ids]
        rendered_projects = ", ".join(
            f"<a href=\"/projects/{escape(project.id)}\">{escape(project.name)}</a>"
            for project in linked_projects
        )
        if not rendered_projects:
            rendered_projects = "Inga projekt"
        original_file = (
            f"<a href=\"/documents/{escape(document.id)}/original\">"
            f"{escape(document.original_filename or 'original.pdf')}</a>"
            if document.has_original_file
            else "Ingen digital originalfil"
        )
        html = self._page(
            title=document.title,
            active_nav="documents",
            body=f"""
    <p><a href="/documents">Dokument</a></p>
    <h1>{escape(document.title)}</h1>
    <dl>
      <dt>Upphov</dt>
      <dd>{escape(document.author or "Okänt")}</dd>
      <dt>Utgivningsår</dt>
      <dd>{escape(document.year or "Okänt")}</dd>
      <dt>Originalfil</dt>
      <dd>{original_file}</dd>
      <dt>Projekt</dt>
      <dd>{rendered_projects}</dd>
    </dl>
    {self._render_document_metadata_form(document)}
    {self._render_document_ai_panel(document, candidates, runs)}
    <section aria-labelledby="document-capture">
      <h2 id="document-capture">Notering</h2>
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
        if self.ai_provider_name == "openai" and not load_openai_api_key(
            self.secrets_path,
            self.encrypted_secrets_path,
        ):
            credential_note = (
                "<p>Ingen OpenAI API-nyckel är konfigurerad. "
                "Lägg till OPENAI_API_KEY eller initiera krypterade secrets innan AI kan köras.</p>"
            )

        return self._page(
            title="AI-analys",
            active_nav="documents",
            body=f"""
    <p><a href="/documents/{escape(document.id)}">{escape(document.title)}</a></p>
    <h1>AI-analys</h1>
    {credential_note}
    <p>Dokumentets extraherade text skickas till extern AI-provider först när du startar analysen.</p>
    <dl>
      <dt>Dokument</dt>
      <dd>{escape(document.title)}</dd>
      <dt>Provider</dt>
      <dd>{escape(self.ai_provider_name)}</dd>
      <dt>Modell</dt>
      <dd>{escape(self.ai_model)}</dd>
      <dt>Funktioner</dt>
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
            active_nav="documents",
            body=f"""
    <p><a href="/documents/{escape(document.id)}">{escape(document.title)}</a></p>
    <h1>AI-analys</h1>
    <p>{escape(message)}</p>
""",
        )

    def render_projects(self) -> str:
        projects = self.archive.list_projects()
        project_document_ids: dict[str, set[str]] = {project.id: set() for project in projects}
        project_note_counts: dict[str, int] = {project.id: 0 for project in projects}
        for document in self.archive.list_documents():
            for project_id in document.project_ids:
                if project_id in project_document_ids:
                    project_document_ids[project_id].add(document.id)
        for note in self.archive.list_recent_knowledge_objects(limit=10_000):
            if note.review_status != "accepted":
                continue
            for project_id in note.project_ids:
                if project_id not in project_note_counts:
                    continue
                project_note_counts[project_id] += 1
                if note.document_id:
                    project_document_ids[project_id].add(note.document_id)
        rendered_projects = "\n".join(
            self._render_project_list_item(
                project,
                document_count=len(project_document_ids[project.id]),
                note_count=project_note_counts[project.id],
            )
            for project in projects
        )
        if not rendered_projects:
            rendered_projects = (
                '<li><p class="empty-state">Inga projekt ännu.</p></li>'
            )
        context = f"""
    <h2 class="context-title">Projekt</h2>
    <div class="context-group">
      <p class="system-label">Sammanhang</p>
      <p>{self._format_project_count(len(projects))}</p>
    </div>
    <details class="metadata-editor">
      <summary>Skapa projekt</summary>
      <form method="post" action="/projects">
        <label for="name">Namn</label>
        <input id="name" name="name" type="text" required>
        <label for="description">Beskrivning</label>
        <input id="description" name="description" type="text">
        <button type="submit">Skapa projekt</button>
      </form>
    </details>
    <div class="context-group">
      <p><a href="/capture">Notering utan projekt</a></p>
    </div>
"""

        return self._page(
            title="Projekt",
            active_nav="projects",
            context=context,
            body=f"""
    <h1>Projekt</h1>
    <section aria-labelledby="registered-projects">
      <h2 id="registered-projects">Befintliga projekt</h2>
      <ul class="project-list">
      {rendered_projects}
      </ul>
    </section>
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
            self._render_project_document_item(document) for document in documents
        )
        if not rendered_documents:
            rendered_documents = (
                '<li><p class="empty-state">Inga dokument i detta projekt ännu.</p></li>'
            )
        rendered_notes = self._render_notes(
            notes, "Inga noteringar i detta projekt ännu."
        )
        context = f"""
    <h2 class="context-title">Projekt</h2>
    <div class="context-group">
      <p class="system-label">Namn</p>
      <p>{escape(project.name)}</p>
    </div>
    <div class="context-group">
      <p class="system-label">Beskrivning</p>
      <p>{escape(project.description or "Ingen beskrivning ännu.")}</p>
    </div>
    <div class="context-group">
      <p class="system-label">Innehåll</p>
      <dl>
        <dt>Dokument</dt>
        <dd>{len(documents)}</dd>
        <dt>Noteringar</dt>
        <dd>{len(notes)}</dd>
      </dl>
    </div>
    <details class="metadata-editor">
      <summary>Redigera projekt</summary>
      <form method="post" action="/projects/{escape(project.id)}">
        <label for="name">Namn</label>
        <input id="name" name="name" type="text" value="{escape(project.name)}" required>
        <label for="description">Beskrivning</label>
        <input id="description" name="description" type="text" value="{escape(project.description)}">
        <button type="submit">Spara projekt</button>
      </form>
    </details>
    <div class="context-group">
      <p><a href="/projects">Alla projekt</a></p>
      <p><a href="/capture?project_id={escape(project.id)}">Notering i projekt</a></p>
    </div>
"""

        return self._page(
            title=project.name,
            active_nav="projects",
            context=context,
            body=f"""
    <h1>{escape(project.name)}</h1>
    <section aria-labelledby="project-notes">
      <h2 id="project-notes">Noteringar och kunskapsobjekt</h2>
      <ul>
        {rendered_notes}
      </ul>
    </section>
    <section aria-labelledby="project-documents">
      <h2 id="project-documents">Dokument</h2>
      <ul class="project-document-list">
        {rendered_documents}
      </ul>
    </section>
    <section aria-labelledby="project-capture">
      <h2 id="project-capture">Ny notering</h2>
      {self._render_capture_form(project=project)}
    </section>
    <details class="metadata-editor">
      <summary>Organisera befintligt material</summary>
      {self._render_project_link_form(project, unlinked_notes)}
      {self._render_relation_form(notes)}
    </details>
""",
        )

    def _render_project_list_item(
        self, project: Project, document_count: int, note_count: int
    ) -> str:
        description = (
            f"<p class=\"metadata-provenance\">{escape(project.description)}</p>"
            if project.description
            else '<p class="metadata-provenance">Ingen beskrivning ännu.</p>'
        )
        return f"""
        <li class="project-list__item">
          <a class="project-list__title" href="/projects/{escape(project.id)}">{escape(project.name)}</a>
          {description}
          <p class="project-list__metadata">{self._format_document_count(document_count)} | {self._format_note_count(note_count)}</p>
        </li>
"""

    def _format_document_count(self, count: int) -> str:
        if count == 1:
            return "1 dokument"
        return f"{count} dokument"

    def _format_note_count(self, count: int) -> str:
        if count == 1:
            return "1 notering"
        return f"{count} noteringar"

    def _format_project_count(self, count: int) -> str:
        if count == 1:
            return "1 projekt"
        return f"{count} projekt"

    def _render_project_document_item(self, document: Document) -> str:
        metadata = " | ".join(
            value
            for value in (document.year, document.author)
            if value
        )
        rendered_metadata = (
            f"<p class=\"document-list__metadata\">{escape(metadata)}</p>"
            if metadata
            else ""
        )
        return f"""
        <li class="document-list__item">
          <div>
            <a class="document-list__title" href="/documents/{escape(document.id)}">{escape(document.title)}</a>
            {rendered_metadata}
          </div>
        </li>
"""

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

    def update_document_from_form(self, document_id: str, body: bytes) -> Document:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        return self.archive.update_document(
            document_id,
            title=form.get("title", [""])[0],
            author=form.get("author", [""])[0],
            year=form.get("year", [""])[0],
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
        if not candidate.ai_run_id:
            raise ValueError("Only AI candidates can be reviewed.")
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
                if candidate.review_status == "handled" and candidate.document_id:
                    self.archive.remove_document_projects(
                        candidate.document_id, candidate.project_ids
                    )
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
        started = perf_counter()
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
        self._log(
            "ai analysis queued "
            f"document_id={document.id} "
            f"run_id={run.id} "
            f"duration_ms={(perf_counter() - started) * 1000:.1f}"
        )
        return self.run_ai_run(run.id)

    def enqueue_document_ai_analysis_from_form(
        self, document_id: str, body: bytes
    ) -> AiRunRecord:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        if form.get("confirm_ai", [""])[0] != "yes":
            raise AiProviderError("AI-analys kräver uttryckligt godkännande.")

        document = self.archive.get_document(document_id)
        started = perf_counter()
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
        self._log(
            "ai analysis queued "
            f"document_id={document.id} "
            f"run_id={run.id} "
            f"duration_ms={(perf_counter() - started) * 1000:.1f}"
        )
        return run

    def run_ai_run(self, run_id: str) -> AiRunRecord:
        run = self.archive.get_ai_run(run_id)
        if run.status not in {"planned", "running"}:
            return run

        document = self.archive.get_document(run.document_id)
        started = perf_counter()
        running = run.running()
        self.archive.save_ai_run(running)
        self._log(f"ai analysis start document_id={document.id} run_id={run.id}")
        text = self._read_document_text(document)
        try:
            provider = self._make_ai_provider()
            projects = tuple(
                (project.id, project.name) for project in self.archive.list_projects()
            )
            provider_started = perf_counter()
            result = provider.analyze_document(
                title=document.title,
                text=text,
                projects=projects,
                model=self.ai_model,
                max_output_tokens=self.ai_max_output_tokens,
            )
            self._log(
                "ai provider completed "
                f"document_id={document.id} "
                f"duration_ms={(perf_counter() - provider_started) * 1000:.1f}"
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
                    project_ids=self._project_ids_for_ai_candidate(
                        candidate, document, projects
                    ),
                    semantic_type=self._semantic_type_for_capability(
                        candidate.capability
                    ),
                ).id
                for candidate in result.candidates
                if self._should_create_ai_candidate(candidate, document, projects)
            )
            completed = run.completed(result.usage, candidate_ids)
            self.archive.save_ai_run(completed)
            self._log(
                "ai analysis completed "
                f"document_id={document.id} "
                f"run_id={run.id} "
                f"candidate_count={len(candidate_ids)} "
                f"duration_ms={(perf_counter() - started) * 1000:.1f}"
            )
            return completed
        except Exception as error:
            failed = running.failed(_safe_ai_error_message(error))
            self.archive.save_ai_run(failed)
            self._log(
                "ai analysis failed "
                f"document_id={document.id} "
                f"run_id={run.id} "
                f"error={error.__class__.__name__} "
                f"duration_ms={(perf_counter() - started) * 1000:.1f}"
            )
            raise

    def run_next_planned_ai_analysis(self) -> str | None:
        planned_runs = [
            run for run in reversed(self.archive.list_ai_runs()) if run.status == "planned"
        ]
        if not planned_runs:
            return None
        run = self.run_ai_run(planned_runs[0].id)
        return run.id

    def recover_interrupted_ai_runs(self) -> tuple[str, ...]:
        recovered: list[str] = []
        for run in self.archive.list_ai_runs():
            if run.status != "running":
                continue
            failed = run.failed(
                "AI-analysen avbröts innan den slutfördes. Starta analysen igen."
            )
            self.archive.save_ai_run(failed)
            recovered.append(run.id)
            self._log(f"ai analysis recovered interrupted run_id={run.id}")
        return tuple(recovered)

    def update_inbox_document_from_form(self, document_id: str, body: bytes) -> None:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        project_ids = tuple(form.get("project_id", []))
        decision = form.get("decision", [""])[0]
        self.archive.set_document_projects(document_id, project_ids)
        if decision:
            self.archive.set_document_inbox_status(document_id, decision)

    def delete_trashed_document_from_form(self, document_id: str, body: bytes) -> None:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        if form.get("confirm_delete", [""])[0] != "yes":
            raise ValueError("Permanent radering kräver uttrycklig bekräftelse.")
        self.archive.delete_trashed_document_permanently(document_id)
        self._log(f"trash document permanently deleted document_id={document_id}")

    def enqueue_uploaded_pdf(self, body: bytes, content_type: str) -> Path:
        if not self.config:
            raise ValueError("Webb-upload kräver konfigurerad runtime.")
        started = perf_counter()
        filename, content = _multipart_pdf_upload(body, content_type)
        safe_filename = _safe_upload_filename(filename)
        _ensure_uploaded_pdf_content(content)
        self._log(
            "upload queued "
            f"filename={safe_filename} "
            f"size_bytes={len(content)}"
        )
        queue_path = _unique_queue_path(self.config.ingest_source / safe_filename)
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            queue_path.write_bytes(content)
            self._log(
                "upload enqueue completed "
                f"path={queue_path} "
                f"duration_ms={(perf_counter() - started) * 1000:.1f}"
            )
            return queue_path
        except Exception as error:
            self._log(
                "upload enqueue failed "
                f"filename={safe_filename} "
                f"error={error.__class__.__name__} "
                f"duration_ms={(perf_counter() - started) * 1000:.1f}"
            )
            raise

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

    def update_note_from_form(self, object_id: str, body: bytes) -> KnowledgeObject:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        return self.archive.update_knowledge_object(
            object_id,
            content=form.get("content", [""])[0],
            source_location=form.get("source_location", [""])[0],
        )

    def render_note_edit(self, object_id: str) -> str:
        note = self.archive.get_knowledge_object(object_id)
        context = self._render_note_edit_context(note)
        return self._page(
            title="Redigera notering",
            active_nav="capture",
            context=context,
            body=f"""
    <h1>Redigera notering</h1>
    <form class="capture-form" method="post" action="/knowledge/{escape(note.id)}">
      <label for="content">Notering</label>
      <textarea id="content" name="content" required>{escape(note.content)}</textarea>
      <details>
        <summary>Källposition</summary>
        <label for="source_location">Källposition</label>
        <input id="source_location" name="source_location" type="text" value="{escape(note.source_location)}">
      </details>
      <button type="submit">Spara</button>
    </form>
""",
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
                    '<p class="capture-context"><span class="system-label">Till dokument</span> '
                    f"<a href=\"/documents/{escape(document.id)}\">"
                    f"{escape(document.title)}</a></p>"
                )
            source_location = """
      <details>
        <summary>Källposition</summary>
        <label for="source_location">Källposition</label>
        <input id="source_location" name="source_location" type="text" placeholder="s. 35 eller kapitel 4">
      </details>
"""
        if project:
            action = f"/capture?project_id={escape(project.id)}"
            if show_context:
                context = (
                    '<p class="capture-context"><span class="system-label">Till projekt</span> '
                    f"<a href=\"/projects/{escape(project.id)}\">"
                    f"{escape(project.name)}</a></p>"
                )
            project_choice = (
                '<details class="capture-organization" open>'
                "<summary>Projektkoppling</summary>"
                "<label>"
                f"<input name=\"project_id\" type=\"checkbox\" value=\"{escape(project.id)}\" checked>"
                f"Koppla till {escape(project.name)}</label>"
                "</details>"
            )

        return f"""
    {context}
    <form class="capture-form" method="post" action="{action}">
      {hidden_document}
      <label for="content">Notering</label>
      <textarea id="content" name="content" autofocus required></textarea>
      {source_location}
      {project_choice}
      <button type="submit">Spara</button>
    </form>
"""

    def _render_capture_context(
        self, document: Document | None = None, project: Project | None = None
    ) -> str:
        target = "Fristående notering"
        detail = "Kan sparas utan dokument eller projekt."
        if document:
            target = "Dokument"
            detail = (
                f"<a href=\"/documents/{escape(document.id)}\">"
                f"{escape(document.title)}</a>"
            )
        elif project:
            target = "Projekt"
            detail = (
                f"<a href=\"/projects/{escape(project.id)}\">"
                f"{escape(project.name)}</a>"
            )
        return f"""
    <h2 class="context-title">Notering</h2>
    <div class="context-group">
      <p class="system-label">Till</p>
      <p>{target}</p>
      <p>{detail}</p>
    </div>
"""

    def _render_note_edit_context(self, note: KnowledgeObject) -> str:
        target = "Fristående notering"
        detail = "Ingen dokument- eller projektkoppling."
        if note.document_id:
            try:
                document = self.archive.get_document(note.document_id)
                target = "Dokument"
                detail = (
                    f"<a href=\"/documents/{escape(document.id)}\">"
                    f"{escape(document.title)}</a>"
                )
            except FileNotFoundError:
                target = "Dokument"
                detail = "Dokument saknas i arkivet."
        elif note.project_ids:
            try:
                project = self.archive.get_project(note.project_ids[0])
                target = "Projekt"
                detail = (
                    f"<a href=\"/projects/{escape(project.id)}\">"
                    f"{escape(project.name)}</a>"
                )
            except FileNotFoundError:
                target = "Projekt"
                detail = "Projekt saknas i arkivet."
        history_note = (
            f"{len(note.history)} tidigare versioner"
            if note.history
            else "Ingen tidigare version"
        )
        return f"""
    <h2 class="context-title">Notering</h2>
    <div class="context-group">
      <p class="system-label">Till</p>
      <p>{target}</p>
      <p>{detail}</p>
    </div>
    <div class="context-group">
      <p class="system-label">Historik</p>
      <p>{history_note}</p>
    </div>
"""

    def _render_document_context(
        self,
        document: Document,
        original_file: str,
        rendered_projects: str,
    ) -> str:
        return f"""
    <h2 class="context-title">Dokument</h2>
    <div class="context-group document-context__meta">
      <dl>
        <dt>Upphov</dt>
        <dd>{escape(document.author or "Okänt")}</dd>
        <dt>Utgivningsår</dt>
        <dd>{escape(document.year or "Okänt")}</dd>
        <dt>Originalfil</dt>
        <dd>{original_file}</dd>
        <dt>Projekt</dt>
        <dd>{rendered_projects}</dd>
      </dl>
    </div>
    {self._render_document_metadata_form(document)}
"""

    def _render_document_metadata_form(self, document: Document) -> str:
        sources = document.metadata_sources or {}
        metadata_source = ", ".join(
            f"{field}: {source}" for field, source in sorted(sources.items())
        )
        if not metadata_source:
            metadata_source = "Ingen sparad källinformation."
        return f"""
    <details class="metadata-editor">
      <summary>Redigera metadata</summary>
      <p class="metadata-provenance">Källor: {escape(metadata_source)}</p>
      <form method="post" action="/documents/{escape(document.id)}/metadata">
        <label for="document-title">Titel</label>
        <input id="document-title" name="title" type="text" value="{escape(document.title)}" required>
        <label for="document-author">Upphov</label>
        <input id="document-author" name="author" type="text" value="{escape(document.author)}">
        <label for="document-year">Utgivningsår</label>
        <input id="document-year" name="year" type="text" inputmode="numeric" pattern="\\d{{4}}" value="{escape(document.year)}">
        <button type="submit">Spara metadata</button>
      </form>
    </details>
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
        <label for="object_id">Kunskapsobjekt</label>
        <select id="object_id" name="object_id">
          {options}
        </select>
        <button type="submit">Koppla</button>
      </form>
    </section>
"""

    def _render_inbox_document(
        self, document: Document, projects: list[Project] | None = None
    ) -> str:
        projects = projects if projects is not None else self.archive.list_projects()
        project_options = "\n".join(
            (
                "<label>"
                f"<input name=\"project_id\" type=\"checkbox\" value=\"{escape(project.id)}\""
                f"{' checked' if project.id in document.project_ids else ''}>"
                f"{escape(project.name)}</label>"
            )
            for project in projects
        )
        if not project_options:
            project_options = "<p>Inga projekt finns ännu.</p>"
        original_filename = (
            f"<dd>{escape(document.original_filename)}</dd>"
            if document.original_filename
            else "<dd>Okänd</dd>"
        )
        author = escape(document.author or "Okänt")
        year = escape(document.year or "Okänt")
        status = self._format_inbox_status(document.inbox_status)
        projects_open = " open" if len(projects) <= 4 else ""
        project_hint = (
            "Valfritt. Välj bara ett sammanhang om det redan är tydligt."
            if projects
            else "Valfritt. Det finns inga projekt att välja ännu."
        )

        return f"""
      <article class="inbox-item">
        <div class="inbox-item__context">
          <p class="system-label">Dokument i inkorg</p>
          <h3><a href="/documents/{escape(document.id)}">{escape(document.title)}</a></h3>
          <dl class="compact-meta">
            <dt>Originalfil</dt>
            {original_filename}
            <dt>Upphov</dt>
            <dd>{author}</dd>
            <dt>År</dt>
            <dd>{year}</dd>
            <dt>Köläge</dt>
            <dd>{escape(status)}</dd>
          </dl>
        </div>
        <form method="post" action="/inbox/documents/{escape(document.id)}">
          <p class="decision-prompt">Granska dokumentet, koppla eventuellt ett projekt och välj nästa steg.</p>
          <details class="optional-projects"{projects_open}>
            <summary>Valfri projektkoppling</summary>
            <fieldset>
              <legend>Koppla till projekt</legend>
              <p class="metadata-provenance">{project_hint}</p>
              {project_options}
            </fieldset>
          </details>
          <div class="decision-actions">
            <button name="decision" type="submit" value="done">Spara</button>
            <button name="decision" type="submit" value="later">Senare</button>
            <button name="decision" type="submit" value="trashed">Kasta</button>
          </div>
        </form>
      </article>
"""

    def _render_ai_inbox_candidates(
        self,
        candidates: list[KnowledgeObject],
        documents_by_id: dict[str, Document] | None = None,
    ) -> str:
        grouped = self._group_ai_candidates_by_document(candidates, documents_by_id)
        if not grouped:
            return ""
        summary = (
            f"<p>{self._format_document_count(len(grouped))} har AI-förslag som väntar på granskning.</p>"
        )
        rendered_items = "\n".join(
            self._render_ai_inbox_document(document, pending_count)
            for document, pending_count in grouped
        )
        return f"{summary}\n{rendered_items}"

    def _group_ai_candidates_by_document(
        self,
        candidates: list[KnowledgeObject],
        documents_by_id: dict[str, Document] | None = None,
    ) -> list[tuple[Document, int]]:
        counts: dict[str, int] = {}
        for candidate in candidates:
            if not candidate.document_id:
                continue
            counts[candidate.document_id] = counts.get(candidate.document_id, 0) + 1
        documents = []
        for document_id, pending_count in counts.items():
            document = (
                documents_by_id.get(document_id)
                if documents_by_id is not None
                else self.archive.get_document(document_id)
            )
            if document is not None:
                documents.append((document, pending_count))
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
      <article class="inbox-item inbox-item--ai" data-ai-inbox-document-id="{escape(document.id)}">
        <div class="inbox-item__context">
          <p class="system-label">AI-granskning</p>
          <h3>{escape(document.title)}</h3>
          <p class="metadata-provenance">{candidate_text}</p>
        </div>
        <div class="inbox-item__decision">
          <p class="decision-prompt">AI har lämnat förslag som behöver redaktionellt beslut innan de blir del av arkivet.</p>
          <p><a href="{document_href}#ai-review">Granska AI-förslag</a></p>
          <p><a href="{document_href}">Öppna dokument</a></p>
        </div>
      </article>
"""

    def _render_ai_candidate_groups(self, candidates: list[KnowledgeObject]) -> str:
        groups = (
            ("Sammanfattning", "Summary"),
            ("Påståenden", "Claim"),
            ("Insikter", "Insight"),
            ("Frågor", "Question"),
            ("Projektförslag", "ProjectSuggestion"),
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
      <section class="ai-review-group" aria-labelledby="ai-{escape(semantic_type)}">
        <h3 id="ai-{escape(semantic_type)}">{escape(heading)}</h3>
        {"".join(self._render_ai_candidate(candidate) for candidate in items)}
      </section>
"""
            )
        return "\n".join(rendered_groups)

    def _format_inbox_status(self, inbox_status: str) -> str:
        return {
            "new": "Väntar på beslut",
            "later": "Markerad för senare",
        }.get(inbox_status, inbox_status)

    def _format_ai_type_label(self, semantic_type: str) -> str:
        return {
            "Summary": "Sammanfattning",
            "Claim": "Påstående",
            "Insight": "Insikt",
            "Question": "Fråga",
            "ProjectSuggestion": "Projektförslag",
        }.get(semantic_type, semantic_type)

    def _format_review_status(self, review_status: str) -> str:
        return {
            "accepted": "Accepterad",
            "rejected": "Avvisad",
            "later": "Senare",
            "handled": "Hanterad",
            "candidate": "Ogranskad",
        }.get(review_status, review_status)

    def _visible_ai_candidates_for_inbox(
        self,
        knowledge_objects: list[KnowledgeObject] | None = None,
        visibility: AiCandidateVisibilityContext | None = None,
    ) -> list[KnowledgeObject]:
        candidates = [
            item
            for item in (
                knowledge_objects
                if knowledge_objects is not None
                else self.archive.list_recent_knowledge_objects(limit=10_000)
            )
            if item.creator == "ai" and item.review_status in {"candidate", "later"}
        ]
        candidates.sort(key=lambda item: item.updated_at, reverse=True)
        return [
            candidate
            for candidate in candidates
            if self._ai_candidate_should_be_visible(candidate, visibility=visibility)
        ]

    def _visible_ai_candidates_for_document(
        self,
        document: Document,
        knowledge_objects: list[KnowledgeObject] | None = None,
        visibility: AiCandidateVisibilityContext | None = None,
    ) -> list[KnowledgeObject]:
        return [
            candidate
            for candidate in self._visible_ai_candidates_for_inbox(
                knowledge_objects, visibility
            )
            if candidate.document_id == document.id
        ]

    def _reviewed_ai_candidates_for_document(
        self, document: Document
    ) -> list[KnowledgeObject]:
        candidates = [
            candidate
            for candidate in self.archive.list_recent_knowledge_objects(limit=10_000)
            if candidate.document_id == document.id
            and candidate.ai_run_id
            and candidate.review_status in {"accepted", "rejected", "handled"}
        ]
        candidates.sort(key=lambda item: item.updated_at, reverse=True)
        return candidates

    def _ai_candidate_should_be_visible(
        self,
        candidate: KnowledgeObject,
        document: Document | None = None,
        visibility: AiCandidateVisibilityContext | None = None,
    ) -> bool:
        if candidate.semantic_type != "ProjectSuggestion":
            return True
        if not candidate.project_ids:
            return False
        if document is None and visibility is not None and candidate.document_id:
            document = visibility.documents.get(candidate.document_id)
        if document is None and candidate.document_id:
            document = self.archive.get_document(candidate.document_id)
        if document is None:
            return False
        if visibility is not None:
            if any(project_id not in visibility.project_ids for project_id in candidate.project_ids):
                return False
            return not any(
                project_id in document.project_ids for project_id in candidate.project_ids
            )
        for project_id in candidate.project_ids:
            try:
                self.archive.get_project(project_id)
            except FileNotFoundError:
                return False
        return not any(
            project_id in document.project_ids for project_id in candidate.project_ids
        )

    def _should_create_ai_candidate(
        self,
        candidate: object,
        document: Document,
        projects: tuple[tuple[str, str], ...],
    ) -> bool:
        if getattr(candidate, "capability", "") != "project_suggestion":
            return True
        return bool(self._project_ids_for_ai_candidate(candidate, document, projects))

    def _project_ids_for_ai_candidate(
        self,
        candidate: object,
        document: Document,
        projects: tuple[tuple[str, str], ...],
    ) -> tuple[str, ...]:
        if getattr(candidate, "capability", "") != "project_suggestion":
            return ()
        project_id = self._resolve_project_suggestion(candidate, projects)
        if not project_id or project_id in document.project_ids:
            return ()
        return (project_id,)

    def _resolve_project_suggestion(
        self, candidate: object, projects: tuple[tuple[str, str], ...]
    ) -> str:
        raw_project_id = str(getattr(candidate, "project_id", "")).strip()
        project_ids = {project_id for project_id, _name in projects}
        if raw_project_id in project_ids:
            return raw_project_id

        raw_project_name = (
            str(getattr(candidate, "project_name", "")).strip().casefold()
        )
        if not raw_project_name:
            return ""
        matches = [
            project_id
            for project_id, project_name in projects
            if project_name.casefold() == raw_project_name
        ]
        if len(matches) == 1:
            return matches[0]
        return ""

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
                f"<p class=\"metadata-provenance\">Dokument: <a href=\"/documents/{escape(document.id)}\">"
                f"{escape(document.title)}</a></p>"
            )
        confidence = (
            f"<p class=\"metadata-provenance\">Säkerhet: {escape(candidate.confidence)}</p>"
            if candidate.confidence
            else ""
        )
        provenance = (
            f"{escape(candidate.ai_provider)} / {escape(candidate.ai_model)} / "
            f"{escape(candidate.prompt_version)}"
        )
        return f"""
      <article class="ai-candidate" id="candidate-{escape(candidate.id)}" data-ai-review-candidate-id="{escape(candidate.id)}">
        <p class="ai-provenance"><span class="system-label">AI-FÖRSLAG</span> {provenance}</p>
        <h4>{escape(self._format_ai_type_label(candidate.semantic_type))}</h4>
        {document_link}
        <p class="ai-suggestion">{escape(candidate.original_content or candidate.content)}</p>
        {confidence}
        <form method="post" action="/documents/{escape(candidate.document_id)}/candidates/{escape(candidate.id)}">
          <label for="content-{escape(candidate.id)}">Din formulering</label>
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

    def _render_reviewed_ai_candidates(self, candidates: list[KnowledgeObject]) -> str:
        if not candidates:
            return "<p>Inga tidigare AI-granskningsbeslut.</p>"
        return "\n".join(self._render_reviewed_ai_candidate(candidate) for candidate in candidates)

    def _render_reviewed_ai_candidate(self, candidate: KnowledgeObject) -> str:
        if candidate.semantic_type == "ProjectSuggestion":
            return self._render_reviewed_project_suggestion(candidate)
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
        return f"""
      <article class="reviewed-ai-candidate" data-ai-reviewed-candidate-id="{escape(candidate.id)}">
        <h4>{escape(self._format_ai_type_label(candidate.semantic_type))} - {escape(self._format_review_status(candidate.review_status))}</h4>
        <p class="metadata-provenance">AI-original: {escape(candidate.original_content or candidate.content)}</p>
        <form method="post" action="/documents/{escape(candidate.document_id)}/candidates/{escape(candidate.id)}">
          <label for="reviewed-content-{escape(candidate.id)}">Formulering</label>
          <textarea id="reviewed-content-{escape(candidate.id)}" name="content">{escape(candidate.content)}</textarea>
          <label for="reviewed-reason-{escape(candidate.id)}">Avvisningsorsak</label>
          <select id="reviewed-reason-{escape(candidate.id)}" name="rejection_reason">
            {rejection_options}
          </select>
          <button name="decision" type="submit" value="accept">Markera accepterad</button>
          <button name="decision" type="submit" value="reject">Markera avvisad</button>
        </form>
      </article>
"""

    def _render_reviewed_project_suggestion(self, candidate: KnowledgeObject) -> str:
        project_name = "Okänt projekt"
        if candidate.project_ids:
            try:
                project_name = self.archive.get_project(candidate.project_ids[0]).name
            except FileNotFoundError:
                project_name = "Okänt projekt"
        return f"""
      <article class="reviewed-ai-candidate" data-ai-reviewed-candidate-id="{escape(candidate.id)}">
        <h4>Projektförslag - {escape(self._format_review_status(candidate.review_status))}</h4>
        <p>Föreslaget projekt: {escape(project_name)}</p>
        <p class="metadata-provenance">AI-original: {escape(candidate.original_content or candidate.content)}</p>
        <form method="post" action="/documents/{escape(candidate.document_id)}/candidates/{escape(candidate.id)}">
          <button name="decision" type="submit" value="link_project">Markera länkad</button>
          <button name="decision" type="submit" value="reject">Markera avvisad</button>
        </form>
      </article>
"""

    def _render_project_suggestion_candidate(self, candidate: KnowledgeObject) -> str:
        project_name = "Okänt projekt"
        project_id = candidate.project_ids[0] if candidate.project_ids else ""
        if project_id:
            project = self.archive.get_project(project_id)
            project_name = project.name
        confidence = (
            f"<p class=\"metadata-provenance\">Säkerhet: {escape(candidate.confidence)}</p>"
            if candidate.confidence
            else ""
        )
        provenance = (
            f"{escape(candidate.ai_provider)} / {escape(candidate.ai_model)} / "
            f"{escape(candidate.prompt_version)}"
        )
        return f"""
      <article class="ai-candidate" id="candidate-{escape(candidate.id)}" data-ai-review-candidate-id="{escape(candidate.id)}">
        <p class="ai-provenance"><span class="system-label">AI-FÖRSLAG</span> {provenance}</p>
        <h4>{escape(self._format_ai_type_label(candidate.semantic_type))}</h4>
        <p>Föreslaget projekt: {escape(project_name)}</p>
        <p class="ai-suggestion">{escape(candidate.original_content or candidate.content)}</p>
        {confidence}
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
        operation_status = self._render_ai_operation_status(runs)
        rendered_candidates = self._render_ai_candidate_groups(candidates)
        if not rendered_candidates:
            rendered_candidates = (
                '<p class="empty-state">Inga AI-förslag väntar på granskning för dokumentet.</p>'
            )
        reviewed_candidates = self._render_reviewed_ai_candidates(
            self._reviewed_ai_candidates_for_document(document)
        )
        rendered_runs = "\n".join(
            (
                f"<li>{escape(_ai_run_status_label(run.status))} - {escape(run.model)} - "
                f"{run.actual_input_tokens}/{run.actual_output_tokens} token - "
                f"{run.actual_cost:.6f} {escape(run.currency)}</li>"
            )
            for run in runs
        )
        if not rendered_runs:
            rendered_runs = "<li>Ingen AI-körning ännu.</li>"
        return f"""
    <section id="ai-review" aria-labelledby="document-ai">
      <h2 id="document-ai">AI</h2>
      {ai_action}
      <h3>Väntande kandidater</h3>
      {rendered_candidates}
      <h3>AI-körningar</h3>
      <ul>{rendered_runs}</ul>
      <h3>Tidigare granskningsbeslut</h3>
      {reviewed_candidates}
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
        return (
            f"<li><p>{escape(content)}</p>{source}"
            f"<p><a href=\"/knowledge/{escape(note_id)}/edit\">Redigera</a></p></li>"
        )

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
            raise AiProviderError("Dokumentets extraherade text saknas i arkivet.")
        text = text_path.read_text(encoding="utf-8").strip()
        if not text:
            raise AiProviderError("Dokumentets extraherade text är tom.")
        return text

    def _estimate_document_ai_cost(self, text: str) -> AiCost:
        input_tokens = estimate_input_tokens(text)
        return estimate_cost(
            input_tokens=input_tokens,
            output_tokens=self.ai_max_output_tokens,
            model=self.ai_model,
        )

    def _make_ai_provider(self) -> AiProvider:
        if self.ai_provider_override:
            return self.ai_provider_override
        if self.ai_provider_name == "mock":
            return MockAiProvider()
        if self.ai_provider_name == "openai":
            return OpenAiProvider(
                load_openai_api_key(self.secrets_path, self.encrypted_secrets_path)
            )
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

    def _ai_review_redirect_location(
        self, document_id: str, reviewed_candidate_id: str = ""
    ) -> str:
        document = self.archive.get_document(document_id)
        candidates = [
            candidate
            for candidate in self._sort_ai_candidates_for_review(
                self._visible_ai_candidates_for_document(document)
            )
            if candidate.id != reviewed_candidate_id
        ]
        if not candidates:
            return f"/documents/{document_id}#ai-review"
        return f"/documents/{document_id}#candidate-{candidates[0].id}"

    def _render_ai_statistics_totals(self, statistics: AiStatistics) -> str:
        reviews = statistics.candidate_reviews
        rows = {
            "Genomförda AI-körningar": str(statistics.completed_runs),
            "Total kostnad": self._format_statistics_cost(statistics.total_usage.cost),
            "Input-token": str(statistics.total_usage.input_tokens),
            "Output-token": str(statistics.total_usage.output_tokens),
            "AI-kandidater": str(reviews.total),
            "Accepterade kandidater": str(reviews.accepted),
            "Redigerade och accepterade kandidater": str(reviews.edited_accepted),
            "Avvisade kandidater": str(reviews.rejected),
            "Väntande kandidater": str(reviews.pending),
            "Uppskjutna kandidater": str(reviews.later),
            "Behandlade projektförslag": str(reviews.handled),
        }
        rendered_rows = "\n".join(
            f"<tr><th scope=\"row\">{escape(label)}</th><td>{escape(value)}</td></tr>"
            for label, value in rows.items()
        )
        return f"""
      <table>
        <tbody>
          {rendered_rows}
        </tbody>
      </table>
"""

    def _render_usage_summary_table(
        self, summaries: dict[str, UsageSummary], label: str
    ) -> str:
        if not summaries:
            return "<p>Ingen användning ännu.</p>"
        rows = "\n".join(
            f"""
          <tr>
            <th scope="row">{escape(key)}</th>
            <td>{summary.runs}</td>
            <td>{summary.input_tokens}</td>
            <td>{summary.output_tokens}</td>
            <td>{self._format_statistics_cost(summary.cost)}</td>
          </tr>
"""
            for key, summary in summaries.items()
        )
        return f"""
      <table>
        <thead>
          <tr>
            <th scope="col">{escape(label.capitalize())}</th>
            <th scope="col">Körningar</th>
            <th scope="col">Input-token</th>
            <th scope="col">Output-token</th>
            <th scope="col">Kostnad</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
"""

    def _render_candidate_review_table(
        self, summaries: dict[str, CandidateReviewSummary]
    ) -> str:
        if not summaries:
            return "<p>Inga AI-kandidater ännu.</p>"
        rows = "\n".join(
            f"""
          <tr>
            <th scope="row">{escape(candidate_type)}</th>
            <td>{summary.total}</td>
            <td>{summary.accepted}</td>
            <td>{summary.edited_accepted}</td>
            <td>{summary.rejected}</td>
            <td>{summary.pending}</td>
            <td>{summary.later}</td>
            <td>{summary.handled}</td>
          </tr>
"""
            for candidate_type, summary in summaries.items()
        )
        return f"""
      <table>
        <thead>
          <tr>
            <th scope="col">Typ</th>
            <th scope="col">Totalt</th>
            <th scope="col">Accepterade</th>
            <th scope="col">Redigerade + accepterade</th>
            <th scope="col">Avvisade</th>
            <th scope="col">Väntande</th>
            <th scope="col">Senare</th>
            <th scope="col">Behandlade</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
"""

    def _render_rejection_reasons(self, reasons: dict[str, int]) -> str:
        if not reasons:
            return "<p>Inga sparade avvisningsorsaker ännu.</p>"
        rows = "\n".join(
            f"""
          <tr>
            <th scope="row">{escape(reason)}</th>
            <td>{count}</td>
          </tr>
"""
            for reason, count in reasons.items()
        )
        return f"""
      <table>
        <thead>
          <tr>
            <th scope="col">Orsak</th>
            <th scope="col">Antal</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
"""

    def render_document(self, document_id: str) -> str:
        started = perf_counter()
        document = self._timed_render_step(
            "document",
            "get_document",
            lambda: self.archive.get_document(document_id),
        )
        knowledge_objects = self._timed_render_step(
            "document",
            "list_knowledge_objects",
            self.archive.list_knowledge_objects,
        )
        projects = self._timed_render_step(
            "document",
            "list_projects",
            self.archive.list_projects,
        )
        runs = self._timed_render_step(
            "document",
            "list_ai_runs_for_document",
            lambda: self.archive.list_ai_runs_for_document(document.id),
        )
        notes = [
            item
            for item in knowledge_objects
            if item.document_id == document.id and item.review_status == "accepted"
        ]
        notes.sort(key=lambda item: item.created_at, reverse=True)
        visibility = AiCandidateVisibilityContext(
            documents={document.id: document},
            project_ids={project.id for project in projects},
        )
        candidates = self._visible_ai_candidates_for_document(
            document, knowledge_objects, visibility
        )
        linked_projects = [project for project in projects if project.id in document.project_ids]
        rendered_projects = ", ".join(
            f"<a href=\"/projects/{escape(project.id)}\">{escape(project.name)}</a>"
            for project in linked_projects
        )
        if not rendered_projects:
            rendered_projects = "Inga projekt"
        original_file = (
            f"<a href=\"/documents/{escape(document.id)}/original\">"
            f"{escape(document.original_filename or 'original.pdf')}</a>"
            if document.has_original_file
            else "Ingen digital originalfil"
        )
        html = self._page(
            title=document.title,
            active_nav="documents",
            body=f"""
    <p><a href="/documents">Dokument</a></p>
    <h1>{escape(document.title)}</h1>
    {self._render_document_content_sections(notes)}
    {self._render_document_ai_panel(document, candidates, runs)}
    <section aria-labelledby="document-capture">
      <h2 id="document-capture">Ny notering</h2>
      {self._render_capture_form(document=document, show_context=False)}
    </section>
""",
            context=self._render_document_context(
                document=document,
                original_file=original_file,
                rendered_projects=rendered_projects,
            ),
        )
        self._log_render_total("document", started)
        return html
        self._log_render_total("document", started)
        return html

    def render_review_history(self, document_id: str) -> str:
        document = self.archive.get_document(document_id)
        reviewed_candidates = self._render_reviewed_ai_candidates(
            self._reviewed_ai_candidates_for_document(document)
        )
        return self._page(
            title="Tidigare AI-granskning",
            active_nav="documents",
            body=f"""
    <p><a href="/documents/{escape(document.id)}">{escape(document.title)}</a></p>
    <h1>Tidigare AI-granskning</h1>
    {reviewed_candidates}
""",
        )

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
        operation_status = self._render_ai_operation_status(runs)
        rendered_candidates = self._render_ai_candidate_groups(candidates)
        if not rendered_candidates:
            rendered_candidates = (
                '<p class="empty-state">Inga AI-förslag väntar på granskning för dokumentet.</p>'
            )
        rendered_runs = "\n".join(
            (
                f"<li>{escape(_ai_run_status_label(run.status))} - {escape(run.model)} - "
                f"{run.actual_input_tokens}/{run.actual_output_tokens} token - "
                f"{run.actual_cost:.6f} {escape(run.currency)}</li>"
            )
            for run in runs
        )
        if not rendered_runs:
            rendered_runs = "<li>Ingen AI-körning ännu.</li>"
        return f"""
    <section id="ai-review" aria-labelledby="document-ai">
      <h2 id="document-ai">AI-granskning</h2>
      <section class="ai-operation" aria-labelledby="ai-operation">
        <h3 id="ai-operation">AI-operation</h3>
        {ai_action}
        {operation_status}
        <details>
          <summary>Tidigare körningar</summary>
          <ul>{rendered_runs}</ul>
        </details>
      </section>
      <h3>Förslag att granska</h3>
      {rendered_candidates}
      <p><a href="/documents/{escape(document.id)}/review-history">Tidigare AI-granskning</a></p>
    </section>
"""

    def _render_ai_operation_status(self, runs: list[AiRunRecord]) -> str:
        for run in runs:
            if run.status == "planned":
                return '<p class="system-note">AI-analys väntar på bakgrundsarbete.</p>'
            if run.status == "running":
                return '<p class="system-note">AI-analys pågår.</p>'
            if run.status == "failed":
                error = escape(run.error or "AI-körningen misslyckades.")
                return f'<p class="system-note">AI-analys misslyckades: {error}</p>'
        return ""

    def _render_document_content_sections(self, notes: list[KnowledgeObject]) -> str:
        groups = (
            ("Sammanfattning", "Summary"),
            ("Påståenden", "Claim"),
            ("Insikter", "Insight"),
            ("Frågor", "Question"),
        )
        rendered_sections: list[str] = []
        grouped_ids: set[str] = set()
        for heading, semantic_type in groups:
            items = [note for note in notes if note.semantic_type == semantic_type]
            grouped_ids.update(note.id for note in items)
            rendered_sections.append(
                self._render_document_note_section(heading, semantic_type, items)
            )
        captures = [note for note in notes if note.id not in grouped_ids]
        rendered_sections.append(
            self._render_document_note_section("Noteringar", "captures", captures)
        )
        return "\n".join(rendered_sections)

    def _render_document_note_section(
        self,
        heading: str,
        section_id: str,
        notes: list[KnowledgeObject],
    ) -> str:
        return f"""
    <section aria-labelledby="document-{escape(section_id)}">
      <h2 id="document-{escape(section_id)}">{escape(heading)}</h2>
      <ul>
        {self._render_notes(notes, "Inget innehåll ännu.")}
      </ul>
    </section>
"""

    def _render_project_suggestion_candidate(self, candidate: KnowledgeObject) -> str:
        project_name = "Okänt projekt"
        project_id = candidate.project_ids[0] if candidate.project_ids else ""
        if project_id:
            project = self.archive.get_project(project_id)
            project_name = project.name
        confidence = (
            f"<p class=\"metadata-provenance\">Säkerhet: {escape(candidate.confidence)}</p>"
            if candidate.confidence
            else ""
        )
        provenance = (
            f"{escape(candidate.ai_provider)} / {escape(candidate.ai_model)} / "
            f"{escape(candidate.prompt_version)}"
        )
        return f"""
      <article class="ai-candidate" id="candidate-{escape(candidate.id)}" data-ai-review-candidate-id="{escape(candidate.id)}">
        <p class="ai-provenance"><span class="system-label">AI-FÖRSLAG</span> {provenance}</p>
        <h4>{escape(self._format_ai_type_label(candidate.semantic_type))}</h4>
        <p>Föreslaget projekt: {escape(project_name)}</p>
        <p class="ai-suggestion">{escape(candidate.original_content or candidate.content)}</p>
        {confidence}
        <form method="post" action="/documents/{escape(candidate.document_id)}/candidates/{escape(candidate.id)}">
          <button name="decision" type="submit" value="link_project">Koppla till projekt</button>
          <button name="decision" type="submit" value="reject">Avvisa</button>
        </form>
      </article>
"""

    def _format_statistics_cost(self, cost: float) -> str:
        return f"{cost:.6f} USD"

    def _log(self, message: str) -> None:
        if self.log:
            self.log(message)

    def _timed_render_step(self, view: str, step: str, fn: Callable[[], object]):
        started = perf_counter()
        result = fn()
        elapsed = perf_counter() - started
        if elapsed >= self.render_step_threshold_seconds:
            self._log(
                f"render step view={view} step={step} duration_ms={elapsed * 1000:.1f}"
            )
        return result

    def _log_render_total(self, view: str, started: float) -> None:
        elapsed = perf_counter() - started
        self._log(f"render total view={view} duration_ms={elapsed * 1000:.1f}")

    def _nav_link(self, key: str, href: str, label: str, mark: str, active_nav: str) -> str:
        active_class = " is-active" if active_nav == key else ""
        current = ' aria-current="page"' if active_nav == key else ""
        return (
            f'<a class="global-nav__link{active_class}" href="{href}"{current}>'
            f'<span class="global-nav__mark" aria-hidden="true">{mark}</span>'
            f"<span>{label}</span>"
            "</a>"
        )

    def _design_css(self) -> str:
        return """
    @font-face {
      font-family: "Monomakh";
      src: url("/static/fonts/Monomakh-Regular.ttf") format("truetype");
      font-style: normal;
      font-weight: 400;
      font-display: swap;
    }

    :root {
      --color-ivory: #f7f1e4;
      --color-ivory-deep: #eee5d6;
      --color-surface-subtle: #fbf7ef;
      --color-ebony: #15130f;
      --color-ebony-soft: #403b34;
      --color-muted: #716a60;
      --color-border: rgba(21, 19, 15, 0.26);
      --color-border-strong: rgba(21, 19, 15, 0.72);
      --color-cinnabar: #9f1d10;
      --color-focus: #15130f;
      --font-system: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --font-reading: Georgia, "Times New Roman", serif;
      --font-inscription: "Courier New", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      --font-devis: "Monomakh", var(--font-inscription);
      --step--1: 0.82rem;
      --step-0: 1rem;
      --step-1: 1.18rem;
      --step-2: 1.55rem;
      --step-3: 2rem;
      --space-1: 0.25rem;
      --space-2: 0.5rem;
      --space-3: 0.75rem;
      --space-4: 1rem;
      --space-5: 1.5rem;
      --space-6: 2rem;
      --space-7: 3rem;
      --line-thin: 1px solid var(--color-border);
      --line-strong: 1px solid var(--color-border-strong);
      --measure-reading: 72ch;
      --shell-context: minmax(13rem, 18rem);
    }

    * {
      box-sizing: border-box;
    }

    html {
      min-width: 0;
      background: var(--color-ivory);
    }

    body {
      color: var(--color-ebony);
      background: var(--color-ivory);
      font-family: var(--font-system);
      font-size: 16px;
      line-height: 1.5;
      margin: 0;
      min-width: 0;
      text-rendering: optimizeLegibility;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      border: 3px solid var(--color-ebony);
      z-index: 10;
    }

    a {
      color: inherit;
      text-decoration-color: var(--color-cinnabar);
      text-decoration-thickness: 1px;
      text-underline-offset: 0.2em;
    }

    a:hover {
      color: var(--color-cinnabar);
    }

    a:focus-visible,
    button:focus-visible,
    input:focus-visible,
    select:focus-visible,
    textarea:focus-visible {
      outline: 2px solid var(--color-focus);
      outline-offset: 3px;
    }

    .app-shell {
      min-height: 100vh;
      padding: 3px;
    }

    .identity-bar {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: var(--space-5);
      align-items: center;
      border-bottom: var(--line-strong);
      padding: var(--space-4) clamp(var(--space-4), 2.5vw, var(--space-7));
    }

    .identity-lockup {
      display: inline-grid;
      grid-template-columns: auto minmax(0, auto);
      gap: var(--space-4);
      align-items: center;
      min-width: 0;
      text-decoration: none;
    }

    .identity-mark {
      width: clamp(2.6rem, 5vw, 4.25rem);
      height: clamp(2.6rem, 5vw, 4.25rem);
      color: var(--color-cinnabar);
      flex: 0 0 auto;
    }

    .identity-text {
      min-width: 0;
      border-left: var(--line-thin);
      padding-left: var(--space-4);
    }

    .identity-title {
      display: block;
      font-family: var(--font-system);
      font-size: clamp(1.35rem, 3vw, 2.15rem);
      font-weight: 650;
      letter-spacing: 0.12em;
      line-height: 1.05;
      overflow-wrap: anywhere;
    }

    .identity-subtitle,
    .system-label,
    label,
    legend,
    th,
    dt {
      font-family: var(--font-inscription);
      font-size: var(--step--1);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .identity-subtitle {
      color: var(--color-cinnabar);
      display: block;
      font-family: var(--font-devis);
      font-size: 0.95rem;
      font-weight: 400;
      letter-spacing: 0.01em;
      line-height: 1.2;
      margin-top: var(--space-2);
      text-transform: none;
    }

    .identity-actions {
      display: flex;
      gap: var(--space-3);
      justify-content: flex-end;
    }

    .identity-action {
      align-items: center;
      border: var(--line-strong);
      color: var(--color-cinnabar);
      display: inline-flex;
      font-family: var(--font-inscription);
      min-height: 2.75rem;
      padding: 0 var(--space-4);
      text-decoration: none;
      text-transform: uppercase;
    }

    .identity-action.is-active {
      background: var(--color-cinnabar);
      color: var(--color-ivory);
    }

    .global-nav {
      border-bottom: var(--line-strong);
      display: flex;
      min-width: 0;
      overflow-x: auto;
      padding: 0 clamp(var(--space-4), 2.5vw, var(--space-7));
    }

    .global-nav__link {
      align-items: center;
      border-right: var(--line-thin);
      display: inline-flex;
      flex: 0 0 auto;
      gap: var(--space-3);
      min-height: 3.15rem;
      padding: 0 var(--space-5);
      position: relative;
      text-decoration: none;
      text-transform: uppercase;
      font-family: var(--font-inscription);
      font-size: var(--step--1);
    }

    .global-nav__link:first-child {
      border-left: var(--line-thin);
    }

    .global-nav__link.is-active {
      color: var(--color-cinnabar);
      font-weight: 700;
    }

    .global-nav__link.is-active::after {
      content: "";
      position: absolute;
      left: var(--space-4);
      right: var(--space-4);
      bottom: -1px;
      border-bottom: 2px solid var(--color-cinnabar);
    }

    .global-nav__mark {
      color: currentColor;
      font-size: 1.2em;
      line-height: 1;
    }

    .page-workspace {
      display: grid;
      grid-template-columns: minmax(0, 1fr);
      margin: 0 auto;
      max-width: 88rem;
      min-width: 0;
    }

    .page-workspace.has-context {
      grid-template-columns: var(--shell-context) minmax(0, 1fr);
    }

    .page-context {
      border-right: var(--line-strong);
      padding: var(--space-5);
    }

    .page-context > :first-child,
    main > :first-child {
      margin-top: 0;
    }

    .context-title {
      border-top: 0;
      color: var(--color-cinnabar);
      margin-bottom: var(--space-5);
      padding-top: 0;
    }

    .context-group {
      border-top: var(--line-thin);
      margin-bottom: var(--space-5);
      padding-top: var(--space-4);
    }

    .context-group > :last-child {
      margin-bottom: 0;
    }

    .context-actions {
      display: grid;
      gap: var(--space-3);
    }

    main {
      min-width: 0;
      padding: clamp(var(--space-4), 3vw, var(--space-7));
    }

    main > * {
      max-width: var(--measure-reading);
    }

    main > h1:first-child,
    main > p:first-child + h1 {
      margin-top: 0;
    }

    h1,
    h2,
    h3 {
      color: var(--color-ebony);
      line-height: 1.16;
      margin: var(--space-6) 0 var(--space-3);
      overflow-wrap: anywhere;
    }

    h1 {
      font-size: var(--step-2);
      font-weight: 580;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }

    h2 {
      border-top: var(--line-thin);
      font-family: var(--font-inscription);
      font-size: var(--step-1);
      font-weight: 700;
      letter-spacing: 0.04em;
      padding-top: var(--space-4);
      text-transform: uppercase;
    }

    h3 {
      font-size: var(--step-1);
      font-weight: 650;
    }

    h4 {
      font-size: var(--step-0);
      font-weight: 650;
      line-height: 1.2;
      margin: var(--space-4) 0 var(--space-3);
      overflow-wrap: anywhere;
    }

    p,
    li,
    dd {
      overflow-wrap: anywhere;
    }

    p {
      margin: 0 0 var(--space-4);
    }

    section,
    article,
    form,
    dl,
    table,
    ul {
      margin-bottom: var(--space-5);
    }

    article {
      border-top: var(--line-thin);
      padding: var(--space-4) 0;
    }

    ul {
      list-style: none;
      padding-left: 0;
    }

    li {
      border-top: var(--line-thin);
      padding: var(--space-3) 0;
    }

    dl {
      display: grid;
      gap: var(--space-2) var(--space-4);
      grid-template-columns: max-content minmax(0, 1fr);
    }

    dt {
      color: var(--color-cinnabar);
    }

    dd {
      margin: 0;
    }

    form {
      border-top: var(--line-thin);
      padding-top: var(--space-4);
    }

    .filter-form,
    .metadata-editor form {
      border-top: 0;
      padding-top: 0;
    }

    .filter-field {
      margin-bottom: var(--space-4);
    }

    label,
    legend {
      color: var(--color-ebony-soft);
      display: block;
      margin-bottom: var(--space-2);
    }

    fieldset {
      border: var(--line-thin);
      margin: 0 0 var(--space-4);
      padding: var(--space-4);
    }

    details {
      border-top: var(--line-thin);
      margin-bottom: var(--space-4);
      padding-top: var(--space-3);
    }

    summary {
      cursor: pointer;
      font-family: var(--font-inscription);
      font-size: var(--step--1);
      min-height: 2.75rem;
      padding: var(--space-2) 0;
      text-transform: uppercase;
    }

    input,
    select,
    textarea,
    button {
      font: inherit;
    }

    input,
    select,
    textarea {
      background: var(--color-surface-subtle);
      border: var(--line-strong);
      color: var(--color-ebony);
      display: block;
      margin-bottom: var(--space-4);
      min-height: 2.75rem;
      padding: 0.62rem 0.7rem;
      width: 100%;
    }

    textarea {
      font-family: var(--font-reading);
      min-height: 10rem;
      resize: vertical;
    }

    input[type="checkbox"] {
      accent-color: var(--color-cinnabar);
      display: inline-block;
      min-height: auto;
      margin: 0 var(--space-2) 0 0;
      width: auto;
    }

    button {
      background: transparent;
      border: var(--line-strong);
      color: var(--color-ebony);
      cursor: pointer;
      font-family: var(--font-inscription);
      font-size: var(--step--1);
      min-height: 2.75rem;
      margin: var(--space-2) var(--space-2) var(--space-2) 0;
      padding: 0.55rem 0.85rem;
      text-transform: uppercase;
    }

    button:hover {
      border-color: var(--color-cinnabar);
      color: var(--color-cinnabar);
    }

    button[type="submit"]:first-of-type,
    button[name="confirm_ai"],
    button[value="yes"] {
      border-color: var(--color-cinnabar);
      color: var(--color-cinnabar);
    }

    table {
      border-collapse: collapse;
      width: 100%;
    }

    th,
    td {
      border-top: var(--line-thin);
      padding: var(--space-3);
      text-align: left;
      vertical-align: top;
    }

    .queue-summary {
      border-bottom: var(--line-strong);
      margin-bottom: var(--space-6);
      padding-bottom: var(--space-4);
    }

    .queue-summary h2 {
      border-top: 0;
      padding-top: 0;
    }

    .queue-summary__number,
    .queue-count {
      color: var(--color-cinnabar);
      font-family: var(--font-inscription);
      font-size: var(--step-1);
      font-weight: 700;
    }

    .empty-state {
      color: var(--color-muted);
    }

    .inbox-item {
      display: grid;
      gap: var(--space-5);
      grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
    }

    .inbox-item h3 {
      margin-top: 0;
    }

    .inbox-item a {
      overflow-wrap: anywhere;
      word-break: break-word;
    }

    .inbox-item > form,
    .inbox-item__context,
    .inbox-item__decision {
      border-top: 0;
      margin-bottom: 0;
      min-width: 0;
      padding-top: 0;
    }

    .compact-meta {
      font-size: var(--step--1);
      margin-bottom: 0;
    }

    .decision-prompt {
      font-family: var(--font-reading);
      font-size: var(--step-1);
      line-height: 1.45;
    }

    .optional-projects fieldset {
      border: 0;
      margin-bottom: 0;
      padding: var(--space-3) 0 0;
    }

    .optional-projects label {
      font-family: var(--font-system);
      font-size: var(--step-0);
      letter-spacing: 0;
      text-transform: none;
    }

    .decision-actions {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: var(--space-2);
    }

    .ai-operation {
      border-top: var(--line-thin);
      padding-top: var(--space-4);
    }

    .ai-review-group {
      margin-bottom: var(--space-6);
    }

    .ai-candidate {
      border-top: var(--line-strong);
    }

    .ai-provenance {
      color: var(--color-muted);
      font-family: var(--font-inscription);
      font-size: var(--step--1);
    }

    .ai-provenance .system-label {
      color: var(--color-cinnabar);
      margin-right: var(--space-2);
    }

    .ai-suggestion {
      font-family: var(--font-reading);
      font-size: var(--step-0);
      line-height: 1.5;
    }

    .project-list__item {
      display: grid;
      gap: var(--space-2);
      padding: var(--space-4) 0;
    }

    .project-list__title {
      font-size: var(--step-1);
      font-weight: 650;
      line-height: 1.25;
      overflow-wrap: anywhere;
      word-break: break-word;
    }

    .project-list__metadata {
      color: var(--color-muted);
      font-family: var(--font-inscription);
      font-size: var(--step--1);
    }

    .capture-context {
      color: var(--color-muted);
    }

    .capture-context a,
    .page-context a {
      overflow-wrap: anywhere;
      word-break: break-word;
    }

    .capture-context .system-label {
      color: var(--color-cinnabar);
      margin-right: var(--space-2);
    }

    .capture-form textarea {
      font-size: var(--step-1);
      line-height: 1.55;
      min-height: clamp(14rem, 38vh, 26rem);
    }

    #project-capture + .capture-context + .capture-form textarea {
      min-height: clamp(10rem, 24vh, 16rem);
    }

    .capture-form details {
      max-width: var(--measure-reading);
    }

    .capture-organization label {
      font-family: var(--font-system);
      font-size: var(--step-0);
      letter-spacing: 0;
      text-transform: none;
    }

    .documents-heading {
      align-items: baseline;
      display: flex;
      gap: var(--space-4);
      justify-content: space-between;
      max-width: none;
    }

    .document-list {
      max-width: none;
    }

    .document-list__item {
      display: grid;
      gap: var(--space-2);
      grid-template-columns: minmax(0, 1fr) auto;
      padding: var(--space-4) 0;
    }

    .document-list__title {
      font-size: var(--step-1);
      font-weight: 650;
      line-height: 1.25;
    }

    .document-list__metadata,
    .document-list__projects {
      color: var(--color-muted);
      font-family: var(--font-inscription);
      font-size: var(--step--1);
    }

    .document-list__projects {
      grid-column: 1 / -1;
    }

    .document-list__status {
      align-items: center;
      display: inline-flex;
      font-family: var(--font-inscription);
      font-size: var(--step--1);
      gap: var(--space-2);
      justify-self: end;
      white-space: nowrap;
    }

    .status-mark {
      border: 1px solid currentColor;
      border-radius: 50%;
      display: inline-block;
      height: 0.65rem;
      width: 0.65rem;
    }

    .status-mark.is-complete {
      background: var(--color-cinnabar);
      border-color: var(--color-cinnabar);
      color: var(--color-cinnabar);
    }

    .document-context__meta,
    .document-context__meta dl {
      margin-bottom: var(--space-4);
    }

    .metadata-provenance {
      color: var(--color-muted);
      font-family: var(--font-inscription);
      font-size: var(--step--1);
    }

    .metadata-editor {
      border-top: var(--line-thin);
      margin-top: var(--space-5);
      padding-top: var(--space-4);
    }

    .metadata-editor summary {
      cursor: pointer;
      font-family: var(--font-inscription);
      font-size: var(--step--1);
      text-transform: uppercase;
    }

    .knowledge-section ul {
      margin-top: var(--space-3);
    }

    .knowledge-section li p:first-child {
      font-family: var(--font-reading);
      font-size: var(--step-1);
      line-height: 1.55;
    }

    small,
    .document-list__metadata,
    .document-list__projects {
      color: var(--color-muted);
    }

    @media (max-width: 54rem) {
      body::before {
        border-width: 2px;
      }

      .identity-bar {
        grid-template-columns: minmax(0, 1fr);
        gap: var(--space-3);
      }

      .identity-actions {
        justify-content: flex-start;
      }

      .identity-title {
        font-size: 1.35rem;
      }

      .global-nav {
        padding: 0;
      }

      .global-nav__link {
        flex: 1 0 auto;
        justify-content: center;
        min-width: 7rem;
        padding: 0 var(--space-3);
      }

      .page-workspace.has-context {
        grid-template-columns: minmax(0, 1fr);
      }

      .page-context {
        border-right: 0;
        border-bottom: var(--line-strong);
      }

      main {
        padding-bottom: var(--space-7);
      }

      h1 {
        font-size: 1.35rem;
      }

      dl {
        grid-template-columns: minmax(0, 1fr);
      }

      .document-list__item {
        grid-template-columns: minmax(0, 1fr);
      }

      .inbox-item {
        grid-template-columns: minmax(0, 1fr);
      }

      .document-list__status {
        justify-self: start;
      }
    }

    @media (max-width: 28rem) {
      .identity-lockup {
        grid-template-columns: auto minmax(0, 1fr);
        gap: var(--space-3);
      }

      .identity-subtitle {
        display: none;
      }

      .identity-title {
        font-size: 1.05rem;
        letter-spacing: 0.08em;
      }

      .identity-action {
        width: 100%;
        justify-content: center;
      }

      .global-nav__link {
        min-width: 6.2rem;
        flex-direction: column;
        gap: var(--space-1);
        min-height: 3.9rem;
      }

      main {
        padding-left: var(--space-4);
        padding-right: var(--space-4);
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        scroll-behavior: auto !important;
      }
    }
"""

    def _identity_mark(self) -> str:
        return """
          <svg class="identity-mark" viewBox="0 0 64 64" focusable="false" aria-hidden="true">
            <circle cx="32" cy="32" r="27" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M32 5 L58 58 H6 Z" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <path d="M32 5 V58 M12 58 H52" fill="none" stroke="currentColor" stroke-width="1.5"/>
            <circle cx="32" cy="32" r="7" fill="none" stroke="currentColor" stroke-width="1.5"/>
          </svg>
"""

    def _page(
        self,
        title: str,
        body: str,
        active_nav: str = "",
        context: str = "",
    ) -> str:
        context_region = (
            f'<aside class="page-context" aria-label="Kontext">{context}</aside>'
            if context
            else ""
        )
        workspace_class = "page-workspace has-context" if context else "page-workspace"
        capture_active = " is-active" if active_nav == "capture" else ""
        capture_current = ' aria-current="page"' if active_nav == "capture" else ""
        primary_nav = "\n      ".join(
            (
                self._nav_link("inbox", "/inbox", "Inkorg", "◇", active_nav),
                self._nav_link("documents", "/documents", "Dokument", "□", active_nav),
                self._nav_link("projects", "/projects", "Projekt", "△", active_nav),
            )
        )
        return f"""<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
{self._design_css()}
  </style>
</head>
<body>
  <div class="app-shell">
    <header class="identity-bar">
      <a class="identity-lockup" href="/inbox" aria-label="Dokumentverkstad inkorg">
{self._identity_mark()}
        <span class="identity-text">
          <span class="identity-title">DOKUMENTVERKSTAD</span>
          <span class="identity-subtitle">личный архивъ знаний ✚</span>
        </span>
      </a>
      <div class="identity-actions" aria-label="Primära handlingar">
        <a class="identity-action{capture_active}" href="/capture"{capture_current}>+ Notering</a>
      </div>
    </header>
    <nav class="global-nav" aria-label="Huvudnavigation">
      {primary_nav}
    </nav>
    <div class="{workspace_class}">
      {context_region}
      <main>
{body}
      </main>
    </div>
  </div>
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
            self._timed_request(self._handle_GET)

        def do_POST(self) -> None:
            self._timed_request(self._handle_POST)

        def _handle_GET(self) -> None:
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
                params = parse_qs(parsed.query)
                self._send_html(
                    app.render_documents(
                        query=params.get("q", [""])[0],
                        sort=params.get("sort", ["year"])[0],
                        ai_status=params.get("ai_status", [""])[0],
                        project_id=params.get("project_id", [""])[0],
                    )
                )
                return
            if parsed.path == "/documents/new":
                self._send_html(app.render_new_document())
                return
            if parsed.path == "/projects":
                self._send_html(app.render_projects())
                return
            if parsed.path == "/upload":
                self._send_html(app.render_upload())
                return
            if parsed.path == "/trash":
                self._send_html(app.render_trash())
                return
            if parsed.path == "/admin":
                self._send_html(app.render_admin())
                return
            if parsed.path == "/static/fonts/Monomakh-Regular.ttf":
                self._send_static_asset(
                    Path(__file__).with_name("static") / "fonts" / "Monomakh-Regular.ttf",
                    "font/ttf",
                )
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
                if document_path.endswith("/review-history"):
                    document_id = document_path.removesuffix("/review-history")
                    self._send_html(app.render_review_history(document_id))
                    return
                document_id = document_path
                self._send_html(app.render_document(document_id))
                return
            if parsed.path.startswith("/knowledge/") and parsed.path.endswith("/edit"):
                object_id = unquote(parsed.path.removeprefix("/knowledge/")).removesuffix("/edit")
                self._send_html(app.render_note_edit(object_id))
                return
            if parsed.path.startswith("/projects/"):
                project_id = unquote(parsed.path.removeprefix("/projects/"))
                self._send_html(app.render_project(project_id))
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def _handle_POST(self) -> None:
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length", "0"))
            if parsed.path == "/upload" and length > app.upload_max_bytes:
                self.send_error(
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    "Den uppladdade filen är för stor.",
                )
                return
            body = self.rfile.read(length)

            if parsed.path == "/upload":
                try:
                    app.enqueue_uploaded_pdf(
                        body,
                        self.headers.get("Content-Type", ""),
                    )
                except ValueError as error:
                    self._send_html(app.render_upload(error=str(error)))
                    return
                except Exception:
                    self._send_html(
                        app.render_upload(
                            error="PDF-filen kunde inte importeras. Kontrollera att filen är en läsbar PDF."
                        )
                    )
                    return
                message = "PDF-filen har lagts till i importkön."
                self._send_html(app.render_upload(message=message))
                return

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
                    app._ai_review_redirect_location(candidate.document_id, object_id)
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
                if existing_candidate.document_id != document_id:
                    self.send_error(HTTPStatus.BAD_REQUEST, "Candidate belongs to another document.")
                    return
                try:
                    candidate = app.review_ai_candidate_from_form(object_id, body)
                except ValueError as error:
                    self.send_error(HTTPStatus.BAD_REQUEST, str(error))
                    return
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header(
                    "Location",
                    app._ai_review_redirect_location(document_id, object_id),
                )
                self.end_headers()
                return

            if parsed.path.startswith("/documents/") and parsed.path.endswith("/metadata"):
                document_path = unquote(parsed.path.removeprefix("/documents/"))
                document_id = document_path.removesuffix("/metadata")
                try:
                    app.update_document_from_form(document_id, body)
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
                    app.enqueue_document_ai_analysis_from_form(document_id, body)
                except AiProviderError as error:
                    document = app.archive.get_document(document_id)
                    self._send_html(app.render_ai_message(document, str(error)))
                    return
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header("Location", f"/documents/{document_id}#ai-review")
                self.end_headers()
                return

            if parsed.path.startswith("/knowledge/"):
                object_id = unquote(parsed.path.removeprefix("/knowledge/"))
                try:
                    note = app.update_note_from_form(object_id, body)
                except ValueError as error:
                    self.send_error(HTTPStatus.BAD_REQUEST, str(error))
                    return
                self.send_response(HTTPStatus.SEE_OTHER)
                self.send_header(
                    "Location",
                    f"/documents/{note.document_id}" if note.document_id else "/capture",
                )
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

            if parsed.path.startswith("/trash/documents/") and parsed.path.endswith("/delete"):
                document_path = unquote(parsed.path.removeprefix("/trash/documents/"))
                document_id = document_path.removesuffix("/delete")
                try:
                    app.delete_trashed_document_from_form(document_id, body)
                except ValueError as error:
                    self.send_error(HTTPStatus.BAD_REQUEST, str(error))
                    return
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

        def send_response(
            self, code: int, message: str | None = None
        ) -> None:
            self._response_status = code
            super().send_response(code, message)

        def _timed_request(self, handler: Callable[[], None]) -> None:
            started = perf_counter()
            self._response_status = 0
            try:
                handler()
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError):
                parsed = urlparse(self.path)
                app._log(
                    "client disconnected "
                    f"method={self.command} "
                    f"path={parsed.path} "
                    f"status={self._response_status or 'unknown'}"
                )
            finally:
                elapsed = perf_counter() - started
                if elapsed >= app.slow_request_threshold_seconds:
                    parsed = urlparse(self.path)
                    app._log(
                        "slow request "
                        f"method={self.command} "
                        f"path={parsed.path} "
                        f"status={self._response_status or 'unknown'} "
                        f"duration_ms={elapsed * 1000:.1f}"
                    )

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

        def _send_static_asset(self, path: Path, content_type: str) -> None:
            if not path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            content = path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "public, max-age=31536000, immutable")
            self.end_headers()
            self.wfile.write(content)

    return Handler


def _multipart_pdf_upload(body: bytes, content_type: str) -> tuple[str, bytes]:
    boundary = _multipart_boundary(content_type)
    if not boundary:
        raise ValueError("Upload-formuläret saknar multipart-boundary.")
    marker = b"--" + boundary
    for raw_part in body.split(marker):
        part = raw_part.lstrip(b"\r\n")
        if not part or part.startswith(b"--"):
            continue
        headers, separator, content = part.partition(b"\r\n\r\n")
        if not separator:
            continue
        header_text = _decode_header_bytes(headers)
        if 'name="pdf"' not in header_text:
            continue
        filename = _content_disposition_filename(header_text)
        if not filename:
            raise ValueError("Ingen PDF-fil valdes.")
        if content.endswith(b"\r\n"):
            content = content[:-2]
        if not content:
            raise ValueError("Den uppladdade filen är tom.")
        return filename, content
    raise ValueError("Upload-formuläret saknade en PDF-fil.")


def _multipart_boundary(content_type: str) -> bytes:
    for part in content_type.split(";"):
        clean = part.strip()
        if clean.startswith("boundary="):
            boundary = clean.removeprefix("boundary=").strip('"')
            return boundary.encode("ascii", errors="ignore")
    return b""


def _content_disposition_filename(headers: str) -> str:
    for line in headers.splitlines():
        if not line.lower().startswith("content-disposition:"):
            continue
        for part in line.split(";"):
            clean = part.strip()
            if clean.startswith("filename="):
                return clean.removeprefix("filename=").strip('"')
    return ""


def _decode_header_bytes(headers: bytes) -> str:
    try:
        return headers.decode("utf-8")
    except UnicodeDecodeError:
        return headers.decode("latin-1", errors="replace")


def _safe_upload_filename(filename: str) -> str:
    normalized = filename.replace("\\", "/").strip()
    if normalized.startswith("/") or ":" in normalized:
        raise ValueError("Filnamnet är inte säkert att använda.")
    name = Path(normalized).name
    if not name or name in {".", ".."}:
        raise ValueError("Filnamnet är inte säkert att använda.")
    if Path(name).suffix.casefold() != ".pdf":
        raise ValueError("Endast PDF-filer kan laddas upp.")
    return name


def _ensure_uploaded_pdf_content(content: bytes) -> None:
    if not content.startswith(b"%PDF-"):
        raise ValueError("Filen är inte en PDF.")


def _unique_queue_path(path: Path) -> Path:
    if not path.exists():
        return path
    candidate = path
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}-{uuid4().hex[:8]}{path.suffix}")
    return candidate


def _safe_ai_error_message(error: Exception) -> str:
    if isinstance(error, AiProviderError):
        return str(error) or "AI-körningen misslyckades."
    return f"AI-körningen misslyckades: {error.__class__.__name__}."


def _ai_run_status_label(status: str) -> str:
    labels = {
        "planned": "väntar",
        "running": "pågår",
        "completed": "klar",
        "failed": "misslyckad",
    }
    return labels.get(status, status)


def unlock_configured_secrets(config: AppConfig, password: str | None = None) -> None:
    if not encrypted_secrets_exists(config.encrypted_secrets_path):
        return
    entered_password = (
        password
        if password is not None
        else getpass("Adminlösenord för Dokumentverkstad secrets: ")
    )
    unlock_encrypted_secrets(config.encrypted_secrets_path, entered_password)


def main(
    config_path: str | None = None,
    password: str | None = None,
    start_worker: bool = True,
) -> None:
    from .worker import BackgroundWorker

    config = load_config(config_path)
    ensure_app_directories(config)
    try:
        unlock_configured_secrets(config, password=password)
    except SecretsError as error:
        raise SystemExit(str(error)) from error
    app = CaptureApp(
        Archive(config.archive_root),
        config=config,
        log=runtime_log_sink(config.runtime_root),
    )
    server = ThreadingHTTPServer((config.host, config.port), make_handler(app))
    worker = None
    if start_worker:
        worker = BackgroundWorker(
            Archive(config.archive_root),
            config,
            run_next_ai_job=app.run_next_planned_ai_analysis,
            recover_ai_jobs=app.recover_interrupted_ai_runs,
            log=app._log,
        )
        worker.start()
    print(f"Dokumentverkstad körs på http://{config.host}:{config.port}/")
    try:
        server.serve_forever()
    finally:
        if worker is not None:
            worker.stop()
        if hasattr(server, "server_close"):
            server.server_close()
