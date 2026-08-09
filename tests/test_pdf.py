from __future__ import annotations

from pathlib import Path
import unittest
import zlib

from dokumentverkstad.pdf import extract_pdf
from helpers import workspace_tempdir


class PdfTests(unittest.TestCase):
    def test_extracts_text_from_compressed_text_array_pdf(self) -> None:
        with workspace_tempdir() as tmp:
            pdf_path = Path(tmp) / "realistic-text-array.pdf"
            _write_pdf_with_compressed_text_array(pdf_path)

            extraction = extract_pdf(pdf_path)

            self.assertEqual(extraction.title, "Realistic Text Array")
            self.assertEqual(extraction.author, "Dokumentverkstad Test")
            self.assertIn("Detta är maskinläsbar text.", extraction.text)


def _write_pdf_with_compressed_text_array(path: Path) -> None:
    content = (
        "BT\n"
        "/F1 12 Tf\n"
        "72 720 Td\n"
        "[(Detta ) -20 (är ) -20 (maskinläsbar ) -20 (text.)] TJ\n"
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
        b"<< /Title (Realistic Text Array) /Author (Dokumentverkstad Test) >>",
    ]
    _write_pdf(path, objects, info_object=6)


def _write_pdf(path: Path, objects: list[bytes], info_object: int) -> None:
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
    path.write_bytes(bytes(data))


if __name__ == "__main__":
    unittest.main()
