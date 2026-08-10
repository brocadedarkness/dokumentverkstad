from __future__ import annotations

from pathlib import Path
import unittest

from dokumentverkstad.pdf import extract_pdf
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


if __name__ == "__main__":
    unittest.main()
