from __future__ import annotations

from dataclasses import dataclass
import re
import zlib
from pathlib import Path


@dataclass(frozen=True)
class PdfExtraction:
    title: str
    author: str
    text: str


def extract_pdf(path: str | Path) -> PdfExtraction:
    data = Path(path).read_bytes()
    decoded = data.decode("latin-1", errors="ignore")
    return PdfExtraction(
        title=_metadata_value(decoded, "Title"),
        author=_metadata_value(decoded, "Author"),
        text=_extract_text(data, decoded),
    )


def _metadata_value(decoded: str, name: str) -> str:
    match = re.search(rf"/{name}\s*\((.*?)\)", decoded, re.DOTALL)
    if not match:
        return ""
    return _decode_pdf_string(match.group(1)).strip()


def _extract_text(data: bytes, decoded: str) -> str:
    parts: list[str] = []
    for match in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.DOTALL):
        stream = match.group(1)
        prefix = data[max(0, match.start() - 300) : match.start()]
        if b"/FlateDecode" in prefix:
            try:
                stream = zlib.decompress(stream)
            except zlib.error:
                continue
        parts.extend(_strings_from_content(stream.decode("latin-1", errors="ignore")))

    if not parts:
        parts.extend(_strings_from_content(decoded))

    return "\n".join(part for part in parts if part).strip()


def _strings_from_content(content: str) -> list[str]:
    strings = [
        _decode_pdf_string(match.group(1))
        for match in re.finditer(r"\(((?:\\.|[^\\)])*)\)\s*Tj", content, re.DOTALL)
    ]
    for array_match in re.finditer(r"\[(.*?)\]\s*TJ", content, re.DOTALL):
        strings.append(
            "".join(
                _decode_pdf_string(match.group(1))
                for match in re.finditer(r"\((?:\\.|[^\\)])*\)", array_match.group(1), re.DOTALL)
            )
        )
    return strings


def _decode_pdf_string(value: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(value):
        char = value[index]
        if char != "\\":
            result.append(char)
            index += 1
            continue

        index += 1
        if index >= len(value):
            break

        escaped = value[index]
        if escaped in "nrtbf":
            result.append({"n": "\n", "r": "\r", "t": "\t", "b": "\b", "f": "\f"}[escaped])
            index += 1
        elif escaped in "()\\":
            result.append(escaped)
            index += 1
        elif escaped in "\r\n":
            while index < len(value) and value[index] in "\r\n":
                index += 1
        elif escaped.isdigit():
            octal = escaped
            index += 1
            while index < len(value) and len(octal) < 3 and value[index].isdigit():
                octal += value[index]
                index += 1
            result.append(chr(int(octal, 8)))
        else:
            result.append(escaped)
            index += 1
    return "".join(result)
