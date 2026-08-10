from __future__ import annotations

from dataclasses import dataclass
import re
import zlib
from pathlib import Path
from typing import Iterator


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
    for stream, prefix in _iter_streams(data):
        if b"/FlateDecode" in prefix:
            try:
                stream = zlib.decompress(stream)
            except zlib.error:
                continue
        parts.extend(_strings_from_content(stream.decode("latin-1", errors="ignore")))

    if not parts and len(decoded) <= 2_000_000:
        parts.extend(_strings_from_content(decoded))

    return "\n".join(part for part in parts if part).strip()


def _iter_streams(data: bytes) -> Iterator[tuple[bytes, bytes]]:
    position = 0
    while True:
        stream_marker = data.find(b"stream", position)
        if stream_marker == -1:
            return

        start = stream_marker + len(b"stream")
        if data[start : start + 2] == b"\r\n":
            start += 2
        elif data[start : start + 1] in (b"\n", b"\r"):
            start += 1

        end = data.find(b"endstream", start)
        if end == -1:
            return

        stream = data[start:end].rstrip(b"\r\n")
        prefix = data[max(0, stream_marker - 300) : stream_marker]
        yield stream, prefix
        position = end + len(b"endstream")


def _strings_from_content(content: str) -> list[str]:
    strings = [
        _decode_pdf_string(match.group(1))
        for match in re.finditer(r"\(((?:\\.|[^\\)])*)\)\s*Tj", content, re.DOTALL)
    ]
    position = 0
    while True:
        operator_index = content.find("TJ", position)
        if operator_index == -1:
            break
        array_start = content.rfind("[", 0, operator_index)
        if array_start != -1:
            array_content = content[array_start:operator_index]
            strings.append(
                "".join(
                    _decode_pdf_string(match.group(1))
                    for match in re.finditer(
                        r"\(((?:\\.|[^\\)])*)\)", array_content, re.DOTALL
                    )
                )
            )
        position = operator_index + 2
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
