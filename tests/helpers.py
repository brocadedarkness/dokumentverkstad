from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import shutil
from uuid import uuid4
import zlib


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


def write_realistic_text_array_pdf(
    path: str | Path,
    title: str = "Realistic Text Array",
    author: str = "Dokumentverkstad Test",
    text: str = "Detta är maskinläsbar text.",
    binary_padding_size: int = 0,
) -> None:
    safe_title = _pdf_escape(title)
    safe_author = _pdf_escape(author)
    words = text.split(" ")
    text_array = " ".join(f"({_pdf_escape(word)} ) -20" for word in words)
    content = (
        "BT\n"
        "/F1 12 Tf\n"
        "72 720 Td\n"
        f"[{text_array}] TJ\n"
        "ET\n"
    ).encode("latin-1")
    compressed = zlib.compress(content)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 5 0 R >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>",
        (
            b"<< /Length "
            + str(len(compressed)).encode("ascii")
            + b" /Filter /FlateDecode >>\nstream\n"
            + compressed
            + b"\nendstream"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Title ({safe_title}) /Author ({safe_author}) >>".encode("latin-1"),
    ]
    if binary_padding_size:
        objects.append(_binary_stream(binary_padding_size))
    _write_pdf(path, objects, info_object=6)


def _binary_stream(size: int) -> bytes:
    payload = bytes((index * 37) % 251 for index in range(size))
    return (
        b"<< /Length "
        + str(len(payload)).encode("ascii")
        + b" >>\nstream\n"
        + payload
        + b"\nendstream"
    )


def _write_pdf(path: str | Path, objects: list[bytes], info_object: int) -> None:
    data = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(len(data))
        data.extend(f"{index} 0 obj\n".encode("ascii"))
        data.extend(body)
        data.extend(b"\nendobj\n")

    xref_offset = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    data.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    data.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} "
            f"/Root 1 0 R /Info {info_object} 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    Path(path).write_bytes(bytes(data))
