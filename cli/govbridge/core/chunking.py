"""Line-aligned chunking (ARCHITECTURE.md section 2, section 4.3; ``MEMORY_POLICY.chunking`` 1200/120). A chunk
never splits a line, so a chunk's byte range always lands on whole source lines. Overlap is expressed in characters
and realised by stepping back whole lines, never a partial line.

``CHUNKER_VERSION`` is part of the chunk identity (``chunk_id = sha256(blob_id || chunker_version || start_line ||
end_line)``) and part of the build manifest's pins (ARCHITECTURE.md section 8.1); changing the algorithm below must
bump it so a stale chunk table is never silently reused (ARCHITECTURE.md section 3).
"""
from __future__ import annotations

import dataclasses
import hashlib

CHUNKER_VERSION = "govbridge-chunker/1"
DEFAULT_MAX_CHARS = 1200
DEFAULT_OVERLAP_CHARS = 120


@dataclasses.dataclass(frozen=True)
class Chunk:
    start_line: int  # 1-indexed, inclusive
    end_line: int  # 1-indexed, inclusive
    text: str


def chunk_text(text: str, max_chars: int = DEFAULT_MAX_CHARS,
                overlap_chars: int = DEFAULT_OVERLAP_CHARS) -> list[Chunk]:
    """Split ``text`` into line-aligned chunks of at most ``max_chars`` characters (a single line longer than
    ``max_chars`` is still emitted whole -- a chunk is never smaller than one line), with ``overlap_chars`` of
    trailing context carried into the next chunk. Deterministic and pure."""
    if text == "":
        return []
    lines = text.splitlines(keepends=True)
    n = len(lines)
    chunks: list[Chunk] = []
    i = 0
    while i < n:
        chars = 0
        j = i
        while j < n and (j == i or chars + len(lines[j]) <= max_chars):
            chars += len(lines[j])
            j += 1
        chunks.append(Chunk(start_line=i + 1, end_line=j, text="".join(lines[i:j])))
        if j >= n:
            break
        # step back from j to build overlap_chars of trailing context, in whole lines
        back_chars = 0
        k = j
        while k > i and back_chars < overlap_chars:
            k -= 1
            back_chars += len(lines[k])
        i = k if k > i else j  # guarantee forward progress even if a single line exceeds overlap_chars
    return chunks


def chunk_id(blob_id: str, start_line: int, end_line: int, chunker_version: str = CHUNKER_VERSION) -> str:
    h = hashlib.sha256()
    h.update(blob_id.encode())
    h.update(b"\0")
    h.update(chunker_version.encode())
    h.update(b"\0")
    h.update(str(start_line).encode())
    h.update(b"\0")
    h.update(str(end_line).encode())
    return h.hexdigest()[:24]


def text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
