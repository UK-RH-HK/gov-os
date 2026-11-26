"""How a text names a path: written out (from the repository's root) or, in a document, as a Markdown link resolved
from the document's folder (L4, SL-11). A path code builds at run time is not found: the selected tests catch it."""

from __future__ import annotations

import posixpath
import re

_TOKEN = re.compile(r"[\w.\-/~@+]+")
_PLAIN = re.compile(r"[\w.\-/~@+]+\Z")
_LINK = re.compile(r"\]\(\s*<?([^()<>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)|^\s{0,3}\[[^\]]+\]:\s*<?([^<>\s]+)>?", re.MULTILINE)
_URL = re.compile(r"[a-z][a-z0-9+.\-]*:|//|#", re.IGNORECASE)


def links(text: str):
    """``(start, end, target)`` of each relative or rooted Markdown link, its anchor and query taken off."""
    for found in _LINK.finditer(text):
        group = 1 if found.group(1) is not None else 2
        raw = found.group(group)
        if _URL.match(raw):
            continue
        yield found.start(group), found.end(group), re.split(r"[#?]", raw)[0]


def resolve(source: str, target: str) -> str | None:
    """The repository path the link ``target`` of the document ``source`` names; None when it leaves the repository."""
    joined = target[1:] if target.startswith("/") else posixpath.join(posixpath.dirname(source), target)
    path = posixpath.normpath(joined)
    return None if path in (".", "..") or path.startswith("../") else path


def item_of(path: str, targets: dict[str, bool]) -> str | None:
    """The target ``path`` is, or lies inside when that target is a folder."""
    parts = path.split("/")
    for depth in range(len(parts), 0, -1):
        head = "/".join(parts[:depth])
        if head in targets and (depth == len(parts) or targets[head]):
            return head
    return None


def mentions(text: str, source: str, targets: dict[str, bool], *, document: bool, exists) -> list[tuple[str, str]]:
    """``(mentioned path, target)`` for each time ``text``, the file ``source``, names a path of ``targets`` (a path to
    whether it is a folder). ``exists`` says whether a repository path is there, for a link written from the root. A
    one-word folder is named only with a slash after it."""
    found = []
    if document:
        spans = []
        for start, end, raw in links(text):
            path = resolve(source, raw)
            if path is not None and not exists(path) and exists(raw.strip("/")):
                path = raw.strip("/")
            item = item_of(path, targets) if path else None
            if item is not None:
                found.append((path, item))
            spans.append((start, end))
        for start, end in reversed(spans):  # a link is judged as a link alone
            text = text[:start] + " " + text[end:]
    for token in _TOKEN.findall(text):
        rooted = token.removeprefix("./").lstrip("/").rstrip(".")
        path = rooted.rstrip("/")
        item = item_of(path, targets) if path else None
        if item is None or (targets[item] and "/" not in rooted and "." not in item):
            continue
        found.append((path, item))
    for item in targets:  # a path with a blank or another mark no token holds
        if not _PLAIN.match(item) and re.search(rf"(?<![\w.\-]){re.escape(item)}(?![\w\-])", text):
            found.append((item, item))
    return found
