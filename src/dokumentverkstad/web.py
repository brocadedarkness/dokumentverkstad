from __future__ import annotations

from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

from .archive import Archive
from .config import load_config
from .document import Document


class CaptureApp:
    def __init__(self, archive: Archive):
        self.archive = archive
        self.archive.initialize()

    def render_capture(self, document: Document | None = None) -> str:
        notes = (
            self.archive.list_knowledge_objects_for_document(document.id)
            if document
            else self.archive.list_recent_knowledge_objects()
        )
        return self._page(
            title="Capture",
            body=f"""
    <h1>Capture</h1>
    {self._render_capture_form(document)}
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
      {self._render_capture_form(document)}
    </section>
    <section aria-labelledby="document-notes">
      <h2 id="document-notes">Kopplade noteringar</h2>
      <ul>
        {self._render_notes(notes, "Inga kopplade noteringar ännu.")}
      </ul>
    </section>
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

    def create_note_from_form(self, body: bytes) -> None:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        content = form.get("content", [""])[0]
        document_id = form.get("document_id", [""])[0]
        source_location = form.get("source_location", [""])[0]
        self.archive.create_knowledge_object(
            content,
            document_id=document_id,
            source_location=source_location,
        )

    def _render_capture_form(self, document: Document | None = None) -> str:
        action = "/capture"
        context = ""
        source_location = ""
        hidden_document = ""
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

        return f"""
    {context}
    <form method="post" action="{action}">
      {hidden_document}
      <label for="content">Ny notering</label>
      <textarea id="content" name="content" autofocus required></textarea>
      {source_location}
      <button type="submit">Spara</button>
    </form>
"""

    def _render_notes(self, notes: list[object], empty_text: str) -> str:
        rendered_notes = "\n".join(
            self._render_note(note.content, note.source_location) for note in notes
        )
        if not rendered_notes:
            return f"<li><p>{escape(empty_text)}</p></li>"
        return rendered_notes

    def _render_note(self, content: str, source_location: str = "") -> str:
        source = ""
        if source_location:
            source = f"<small>Källa: {escape(source_location)}</small>"
        return f"<li><p>{escape(content)}</p>{source}</li>"

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
    input {{
      box-sizing: border-box;
      width: 100%;
      font: inherit;
      padding: 0.55rem;
      border: 1px solid #555;
      margin-bottom: 0.75rem;
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
                document = app.archive.get_document(document_id) if document_id else None
                self._send_html(app.render_capture(document))
                return
            if parsed.path == "/documents":
                self._send_html(app.render_documents())
                return
            if parsed.path.startswith("/documents/"):
                document_id = unquote(parsed.path.removeprefix("/documents/"))
                self._send_html(app.render_document(document_id))
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

            if parsed.path != "/capture":
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            app.create_note_from_form(body)
            params = parse_qs(parsed.query)
            document_id = params.get("document_id", [""])[0]
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header(
                "Location", f"/documents/{document_id}" if document_id else "/capture"
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
