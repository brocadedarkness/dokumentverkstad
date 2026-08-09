from __future__ import annotations

from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from .archive import Archive
from .config import load_config
from .document import Document
from .project import Project


class CaptureApp:
    def __init__(self, archive: Archive):
        self.archive = archive
        self.archive.initialize()

    def render_capture(
        self, document: Document | None = None, project: Project | None = None
    ) -> str:
        notes = (
            self.archive.list_knowledge_objects_for_document(document.id)
            if document
            else self.archive.list_knowledge_objects_for_project(project.id)
            if project
            else self.archive.list_recent_knowledge_objects()
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
        return self._page(
            title=document.title,
            body=f"""
    <p><a href="/documents">Documents</a></p>
    <h1>{escape(document.title)}</h1>
    <dl>
      <dt>Originalfil</dt>
      <dd>Ingen digital originalfil</dd>
    </dl>
    <section aria-labelledby="document-capture">
      <h2 id="document-capture">Capture</h2>
      {self._render_capture_form(document=document)}
    </section>
    <section aria-labelledby="document-notes">
      <h2 id="document-notes">Kopplade noteringar</h2>
      <ul>
        {self._render_notes(notes, "Inga kopplade noteringar ännu.")}
      </ul>
    </section>
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
            if project.id not in note.project_ids
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
        self, document: Document | None = None, project: Project | None = None
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
            if parsed.path in ("/", "/capture"):
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
            if parsed.path.startswith("/documents/"):
                document_id = unquote(parsed.path.removeprefix("/documents/"))
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

    return Handler


def main() -> None:
    config = load_config()
    config.runtime_root.mkdir(parents=True, exist_ok=True)
    app = CaptureApp(Archive(config.archive_root))
    server = ThreadingHTTPServer((config.host, config.port), make_handler(app))
    print(f"Dokumentverkstad Capture körs på http://{config.host}:{config.port}/")
    server.serve_forever()
