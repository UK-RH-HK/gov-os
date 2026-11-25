"""A decision package as a card: its fields, limits, page-readiness and content hash (W2-211 PG-1; the spec's "The record").

``page_ready(package, root)`` is computed by code, like a ticket's READY: it lists, for a package that cannot be put on
a page, each field that is missing, too long or false, as ``(field, why)``; it never fills a field itself. ``card`` is the
part of a package a batch hash covers; ``content_hash`` is the SHA-256 of the package file's text (a package changed after
publication has another one).
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path

from gov.util import frontmatter

PACKAGES_DIR = "docs/decisions/packages"
LIMITS = {"title": 120, "question": 300, "found": 900, "label": 80, "cost": 240, "consequence": 240, "reason": 400,
          "blocks": 200, "meanwhile": 200}
SOURCES_MAX = 12
OPTIONS_MIN, OPTIONS_MAX = 2, 6
RUBRIC = re.compile(r"^(P1\.(?:[1-9]|10)|P2\.brought)$")
CONFIDENCE = ("low", "medium", "high")
CARD_FIELDS = ("id", "question", "found", "options", "recommendation", "sources", "blocks", "deadline", "constrains",
               "meanwhile", "file_only")
_DEC = re.compile(r"^DEC-\d+$")
_HEX = re.compile(r"^[0-9a-f]{7,40}$")


def read(path: Path) -> tuple[dict, str]:
    """``(frontmatter, text)`` of a package file; ``ValueError`` when it has no readable frontmatter."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        front = frontmatter.parse(text)
    except frontmatter.FrontmatterError as error:
        raise ValueError(f"{path} frontmatter is not readable ({error.kind})") from None
    if front is None:
        raise ValueError(f"{path} has no frontmatter")
    return front, text


def load_all(root: Path, folder: str = PACKAGES_DIR) -> dict[str, dict]:
    """Every package of the folder by id: ``{id: {front, text, path}}`` (a file that cannot be read is left out)."""
    found: dict[str, dict] = {}
    base = Path(root) / folder
    for path in sorted(base.glob("*.md")) if base.is_dir() else []:
        try:
            front, text = read(path)
        except (OSError, ValueError):
            continue
        if isinstance(front.get("id"), str):
            found[front["id"]] = {"front": front, "text": text, "path": path}
    return found


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def card(front: dict) -> dict:
    """The part of a package the batch hash covers (and the page shows)."""
    out = {name: front.get(name) for name in CARD_FIELDS}
    out["file_only"] = bool(front.get("file_only"))
    options = front.get("options")
    out["options"] = [{k: o.get(k) for k in ("key", "label", "cost", "consequence")} if isinstance(o, dict) else o
                      for o in options] if isinstance(options, list) else options
    return out


def _text(value) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _limit(field: str, value, name: str, problems: list) -> None:
    if len(value) > LIMITS[name]:
        problems.append((field, f"too long ({len(value)} of {LIMITS[name]})"))


def _source_exists(root: Path, source: str, register_ids: set) -> bool:
    if _DEC.match(source):
        return source in register_ids
    path = Path(source)
    if not path.is_absolute() and ".." not in path.parts and (Path(root) / path).exists():
        return True
    if _HEX.match(source):
        done = subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{source}^{{commit}}"],
                              capture_output=True, stdin=subprocess.DEVNULL)
        return done.returncode == 0
    return False


def register_ids(root: Path, register: str) -> set:
    path = Path(root) / register
    try:
        return set(re.findall(r"^###[ \t]+(DEC-\d+)[ \t]", path.read_text(encoding="utf-8"), re.MULTILINE))
    except (OSError, UnicodeDecodeError):
        return set()


def page_ready(front: dict, root: Path, register: str = "docs/DECISION_REGISTER.md") -> list[tuple[str, str]]:
    """The ``(field, why)`` pairs that keep a package off a page; empty when it is page-ready."""
    problems: list[tuple[str, str]] = []
    if (title := _text(front.get("title"))) is not None:
        _limit("title", title, "title", problems)
    for name in ("question", "found"):
        value = _text(front.get(name))
        if value is None:
            problems.append((name, "missing"))
        else:
            _limit(name, value, name, problems)
    options = front.get("options")
    if not isinstance(options, list) or not (OPTIONS_MIN <= len(options) <= OPTIONS_MAX):
        problems.append(("options", f"{OPTIONS_MIN} to {OPTIONS_MAX} are needed, "
                         f"there are {len(options) if isinstance(options, list) else 'none'}"))
    else:
        for at, option in enumerate(options):
            want = "abcdef"[at]
            if not isinstance(option, dict) or option.get("key") != want:
                problems.append(("options", f"item {at + 1} is not an entry with key {want}"))
                continue
            for name in ("label", "cost", "consequence"):
                value = _text(option.get(name))
                if value is None:
                    problems.append(("options", f"option {want} has no {name}"))
                else:
                    _limit("options", value, name, problems)
    keys = [o.get("key") for o in options if isinstance(o, dict)] if isinstance(options, list) else []
    rec = front.get("recommendation")
    if not isinstance(rec, dict):
        problems.append(("recommendation", "missing"))
    else:
        if rec.get("option") not in keys:
            problems.append(("recommendation", f"names no option of the card ({rec.get('option')!r})"))
        reason = _text(rec.get("reason"))
        if reason is None:
            problems.append(("recommendation", "has no reason"))
        else:
            _limit("recommendation", reason, "reason", problems)
        if rec.get("confidence") not in CONFIDENCE:
            problems.append(("recommendation", "has no confidence of low, medium or high"))
    sources = front.get("sources")
    if not isinstance(sources, list) or not sources:
        problems.append(("sources", "missing"))
    elif len(sources) > SOURCES_MAX:
        problems.append(("sources", f"too many ({len(sources)} of {SOURCES_MAX})"))
    else:
        known = register_ids(root, register)
        for source in sources:
            if not isinstance(source, str) or not _source_exists(root, source.strip(), known):
                problems.append(("sources", f"{source} does not exist"))
    blocks = _text(front.get("blocks"))
    if blocks is None:
        problems.append(("blocks", "missing"))
    else:
        _limit("blocks", blocks, "blocks", problems)
    if front.get("meanwhile") is not None:
        value = _text(front.get("meanwhile"))
        if value is not None:
            _limit("meanwhile", value, "meanwhile", problems)
    rubric = front.get("rubric")
    if not isinstance(rubric, str) or not RUBRIC.match(rubric):
        problems.append(("rubric", "is not a rubric line (P1.1 to P1.10, P2.brought)" if rubric else "missing"))
    from gov.decisions import level

    try:
        level.normalise({k: front.get(k) for k in ("touches", "reversible", "inside", "spends", "rounds", "emergency")})
    except level.LevelError as error:
        problems.append((error.message.split()[0] if error.message.split()[0] in ("touches", "reversible", "inside",
                                                                                "spends", "rounds", "emergency")
                         else "touches", error.message))
    return problems
