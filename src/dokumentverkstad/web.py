from __future__ import annotations

from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from .archive import Archive
from .config import load_config


class CaptureApp:
    def __init__(self, archive: Archive):
        self.archive = archive
        self.archive.initialize()

    def render_capture(self) -> str:
        notes = self.archive.list_recent_knowledge_objects()
        rendered_notes = "\n".join(
            f"<li><p>{escape(note.content)}</p></li>" for note in notes
        )
        if not rendered_notes:
            rendered_notes = "<li><p>Inga noteringar ännu.</p></li>"

        return f"""<!doctype html>
<html lang="sv">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Capture</title>
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
    <h1>Capture</h1>
    <form method="post" action="/capture">
      <label for="content">Ny notering</label>
      <textarea id="content" name="content" autofocus required></textarea>
      <button type="submit">Spara</button>
    </form>
    <section aria-labelledby="recent-notes">
      <h2 id="recent-notes">Senaste noteringar</h2>
      <ul>
        {rendered_notes}
      </ul>
    </section>
  </main>
</body>
</html>
"""

    def create_note_from_form(self, body: bytes) -> None:
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        content = form.get("content", [""])[0]
        self.archive.create_knowledge_object(content)


def make_handler(app: CaptureApp) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path in ("/", "/capture"):
                self._send_html(app.render_capture())
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            if self.path != "/capture":
                self.send_error(HTTPStatus.NOT_FOUND)
                return

            length = int(self.headers.get("Content-Length", "0"))
            app.create_note_from_form(self.rfile.read(length))
            self.send_response(HTTPStatus.SEE_OTHER)
            self.send_header("Location", "/capture")
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
