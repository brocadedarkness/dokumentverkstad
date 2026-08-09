from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import shutil
from uuid import uuid4


@contextmanager
def workspace_tempdir():
    root = Path("test_tmp")
    root.mkdir(exist_ok=True)
    path = root / f"case_{uuid4().hex}"
    path.mkdir()
    try:
        yield str(path)
    finally:
        shutil.rmtree(path, ignore_errors=True)


def write_minimal_pdf(
    path: str | Path,
    title: str = "PDF Title",
    author: str = "PDF Author",
    text: str = "Machine readable text",
) -> None:
    safe_title = _pdf_escape(title)
    safe_author = _pdf_escape(author)
    safe_text = _pdf_escape(text)
    pdf = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 72 720 Td ({safe_text}) Tj ET
endstream
endobj
5 0 obj
<< /Title ({safe_title}) /Author ({safe_author}) >>
endobj
trailer
<< /Root 1 0 R /Info 5 0 R >>
%%EOF
"""
    Path(path).write_bytes(pdf.encode("latin-1"))


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
