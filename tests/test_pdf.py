from __future__ import annotations

from pathlib import Path
import unittest

from dokumentverkstad.pdf import _extract_with_stdlib, extract_pdf
from helpers import workspace_tempdir, write_realistic_text_array_pdf


class PdfTests(unittest.TestCase):
    def test_extracts_text_from_compressed_text_array_pdf(self) -> None:
        with workspace_tempdir() as tmp:
            pdf_path = Path(tmp) / "realistic-text-array.pdf"
            write_realistic_text_array_pdf(pdf_path)

            extraction = extract_pdf(pdf_path)

            self.assertEqual(extraction.title, "Realistic Text Array")
            self.assertEqual(extraction.author, "Dokumentverkstad Test")
            self.assertIn("Detta är maskinläsbar text.", extraction.text)

    def test_extracts_text_from_larger_pdf_with_binary_stream(self) -> None:
        with workspace_tempdir() as tmp:
            pdf_path = Path(tmp) / "larger-realistic.pdf"
            write_realistic_text_array_pdf(
                pdf_path,
                title="Larger PDF",
                text="Större maskinläsbar PDF.",
                binary_padding_size=2_200_000,
            )

            extraction = extract_pdf(pdf_path)

            self.assertGreater(pdf_path.stat().st_size, 2_000_000)
            self.assertEqual(extraction.title, "Larger PDF")
            self.assertIn("Större maskinläsbar PDF.", extraction.text)

    def test_stdlib_fallback_does_not_parse_escaped_9_as_octal(self) -> None:
        with workspace_tempdir() as tmp:
            pdf_path = Path(tmp) / "escaped-9.pdf"
            _write_raw_text_pdf(pdf_path, r"Version \9")

            extraction = _extract_with_stdlib(pdf_path)

            self.assertIn("Version 9", extraction.text)

    def test_stdlib_fallback_does_not_parse_escaped_superscript_as_octal(self) -> None:
        with workspace_tempdir() as tmp:
            pdf_path = Path(tmp) / "escaped-superscript.pdf"
            _write_raw_text_pdf(pdf_path, r"Not \²")

            extraction = _extract_with_stdlib(pdf_path)

            self.assertIn("Not ²", extraction.text)


def _write_raw_text_pdf(path: Path, raw_pdf_string: str) -> None:
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
BT /F1 12 Tf 72 720 Td ({raw_pdf_string}) Tj ET
endstream
endobj
trailer
<< /Root 1 0 R >>
%%EOF
"""
    path.write_bytes(pdf.encode("latin-1"))


if __name__ == "__main__":
    unittest.main()
