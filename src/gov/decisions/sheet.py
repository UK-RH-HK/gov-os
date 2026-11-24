"""The answer sheet: its writer, its parser and the batch hash (W2-211 PG-3; the spec's "The answer sheet").

The sheet is a fixed block (``GOV-ANSWERS 1``, ``batch:``, ``hash:``, ``answered:``, ``count:``, one line per card, ``END``).
``write_sheet`` and ``template/governance/kernel/templates/decisions-sheet.js`` write it byte for byte alike. ``parse_sheet``
reads the first complete block of a text the chat may have wrapped (a code fence, quote marks, CRLF, text around it).
``batch_hash`` is the one function that writes the batch's hash into the manifest and checks it on a sheet.
"""

from __future__ import annotations

import hashlib
import json
import re

NOTE_MAX = 400
FIRST = "GOV-ANSWERS 1"
# every character Python's ``str.splitlines`` and JavaScript's line terminators treat as a line break
_BREAKS = re.compile("\r\n|[\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029]")
_QUOTES = "\"'`“”‘’«»"
_CARD = re.compile(r"^(DP-\d+): ([a-f]|skip)(?: \| note: (.*))?$", re.DOTALL)


class SheetError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def batch_hash(batch: str, cards: list[dict]) -> str:
    """The SHA-256 (hex) of the batch id and its cards in page order, as JSON with sorted keys, no spaces, in UTF-8."""
    canonical = json.dumps({"batch": batch, "cards": cards}, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def strip_prefix(text: str) -> str:
    return text[7:] if text.startswith("sha256:") else text


def write_sheet(batch: str, hash_: str, answered: str, picks: list) -> str:
    """The sheet's text for ``picks``, a list of ``(id, letter or "skip", note or None)``, ending in one newline."""
    lines = [FIRST, f"batch: {batch}", f"hash: {hash_}", f"answered: {answered}", f"count: {len(picks)}"]
    for pick_id, letter, note in picks:
        line = f"{pick_id}: {letter}"
        if note:
            line += " | note: " + _BREAKS.sub(" ", note)
        lines.append(line)
    lines.append("END")
    return "\n".join(lines) + "\n"


def _clean(line: str) -> str:
    """A line without the chat's quote marks and spaces before it, and the spaces after it."""
    return line.lstrip(" \t>" + _QUOTES).rstrip()


def parse_sheet(text: str) -> dict:
    """``{batch, hash, answered, count, lines: [{id, letter, note}], text}`` of the first complete block;
    ``SheetError`` with the reason when there is none."""
    rows = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    starts = [i for i, row in enumerate(rows) if _clean(row).rstrip(_QUOTES + " ") == FIRST]
    if not starts:
        raise SheetError(f"no block opens with {FIRST}")
    first_reason = None
    for start in starts:
        try:
            return _block(rows, start)
        except SheetError as error:
            first_reason = first_reason or error.message
    raise SheetError(first_reason or "no complete block")


def _block(rows: list[str], start: int) -> dict:
    # a chat that wrapped each line in quote marks closed them after ``batch:``'s value too
    closer = ""
    probe = rows[start + 1].rstrip() if start + 1 < len(rows) else ""
    if probe and probe[-1] in _QUOTES and _clean(probe).startswith("batch:") and _QUOTES.count(probe[-1]) and \
            any(c in _QUOTES for c in rows[start][:rows[start].find(FIRST)]):
        closer = probe[-1]

    def get(at: int) -> str:
        row = _clean(rows[at]) if at < len(rows) else ""
        return row[:-1].rstrip() if closer and row.endswith(closer) else row

    head = {}
    for offset, key in enumerate(("batch", "hash", "answered", "count"), 1):
        row = get(start + offset)
        if not row.startswith(f"{key}:"):
            raise SheetError(f"{key}: is missing or out of order")
        head[key] = row.split(":", 1)[1].strip()
    if not re.fullmatch(r"\d+", head["count"]):
        raise SheetError(f"count: {head['count']!r} is not a number")
    lines, at = [], start + 5
    while at < len(rows):
        raw = rows[at].lstrip(" \t>" + _QUOTES)
        if get(at) == "END" or re.fullmatch(r"END[\s`" + _QUOTES + r"]*", raw):
            break
        lines.append(raw.rstrip())
        at += 1
    else:
        raise SheetError("no END line")
    if len(lines) != int(head["count"]):
        raise SheetError(f"count: {head['count']} but {len(lines)} lines")
    parsed, seen = [], set()
    for row in lines:
        if closer and row.endswith(closer) and "| note: " not in row:
            row = row[:-1].rstrip()
        found = _CARD.match(row)
        if not found:
            raise SheetError(f"line {row[:60]!r} is not `DP-n: <letter or skip>`")
        pick_id, letter, note = found.groups()
        if pick_id in seen:
            raise SheetError(f"{pick_id} twice")
        seen.add(pick_id)
        if note is not None and len(note) > NOTE_MAX:
            raise SheetError(f"the note of {pick_id} is {len(note)} characters, over {NOTE_MAX}")
        parsed.append({"id": pick_id, "letter": letter, "note": note if note else None})
    block = [FIRST, f"batch: {head['batch']}", f"hash: {head['hash']}", f"answered: {head['answered']}",
             f"count: {head['count']}", *lines, "END"]
    return {**head, "count": int(head["count"]), "lines": parsed, "text": "\n".join(block) + "\n"}
