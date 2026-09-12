"""Hierarchical chunking: document -> section -> child."""
from __future__ import annotations

import re
from dataclasses import dataclass

HEADING_RX = re.compile(r"^(#{1,6})\s+(.*)$", re.M)


@dataclass
class Chunk:
    level: str  # document | section | child
    section: str
    text: str
    ordinal: int
    parent_ordinal: int | None = None


def _split_long(text: str, max_chars: int, overlap: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    out = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        # prefer to cut at a newline
        cut = text.rfind("\n", start + max_chars // 2, end) if end < len(text) else end
        if cut <= start:
            cut = end
        out.append(text[start:cut].strip())
        if cut >= len(text):
            break
        start = max(cut - overlap, start + 1)
    return [o for o in out if o]


def chunk_markdown(title: str, body: str, max_chars: int = 1200, overlap: int = 120) -> list[Chunk]:
    chunks: list[Chunk] = []
    doc_text = title.strip()
    first_para = body.strip().split("\n\n")[0] if body.strip() else ""
    if first_para and not first_para.startswith("#"):
        doc_text += "\n" + first_para[:400]
    chunks.append(Chunk("document", title, doc_text, 0))
    sections: list[tuple[str, str]] = []
    pos = 0
    last_title = title
    for m in HEADING_RX.finditer(body):
        seg = body[pos : m.start()].strip()
        if seg:
            sections.append((last_title, seg))
        last_title = m.group(2).strip()
        pos = m.end()
    tail = body[pos:].strip()
    if tail:
        sections.append((last_title, tail))
    if not sections and body.strip():
        sections.append((title, body.strip()))
    ordinal = 1
    for sec_title, sec_text in sections:
        sec_ord = ordinal
        chunks.append(Chunk("section", sec_title, f"{sec_title}\n{sec_text[:max_chars]}", sec_ord, 0))
        ordinal += 1
        pieces = _split_long(sec_text, max_chars, overlap)
        if len(pieces) > 1:
            for piece in pieces:
                chunks.append(Chunk("child", sec_title, piece, ordinal, sec_ord))
                ordinal += 1
    return chunks


def chunk_record_fields(title: str, fields: dict[str, str], body: str, max_chars: int, overlap: int) -> list[Chunk]:
    """YAML record: document chunk from title/summary, a section per long text field, plus body sections."""
    chunks = chunk_markdown(title, body, max_chars, overlap)
    ordinal = max(c.ordinal for c in chunks) + 1
    for name, text in fields.items():
        if not text or len(text) < 40:
            continue
        sec_ord = ordinal
        chunks.append(Chunk("section", name, f"{name}\n{text[:max_chars]}", sec_ord, 0))
        ordinal += 1
        pieces = _split_long(text, max_chars, overlap)
        if len(pieces) > 1:
            for piece in pieces:
                chunks.append(Chunk("child", name, piece, ordinal, sec_ord))
                ordinal += 1
    return chunks


def chunk_plain(title: str, text: str, max_chars: int, overlap: int) -> list[Chunk]:
    chunks = [Chunk("document", title, title + "\n" + text[:300], 0)]
    paras = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    buf, ordinal = "", 1
    for p in paras:
        if len(buf) + len(p) > max_chars and buf:
            chunks.append(Chunk("section", f"part {ordinal}", buf.strip(), ordinal, 0))
            ordinal += 1
            buf = ""
        buf += p + "\n\n"
    if buf.strip():
        chunks.append(Chunk("section", f"part {ordinal}", buf.strip(), ordinal, 0))
    return chunks
