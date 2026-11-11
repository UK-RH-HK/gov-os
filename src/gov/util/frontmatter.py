"""The frontmatter of a record, read in one place (DEC-1039 (2), P1-6; INVENTORY-TESTS-CODE-1 §6b items 1 and 3).

A record opens with a ``---`` line, a YAML mapping follows, and a ``---`` line closes it. ``parse`` reads it by
lines and says why it cannot be read; ``quiet`` and ``of_file`` answer None instead; ``with_body`` is the
validators' form, read by text, which also returns what follows. ``ids`` reads a field that holds one id or a list.
The guard's own parser (``guard/decide.py``, its hot path) and the store's (``store/loader.py``) are not these.
"""

from __future__ import annotations

from pathlib import Path

UNCLOSED, NOT_YAML, NOT_MAPPING = "unclosed", "not_yaml", "not_mapping"


class FrontmatterError(ValueError):
    """Why a text that opens with ``---`` has no readable frontmatter: ``kind`` is ``UNCLOSED``, ``NOT_YAML`` (with
    the YAML error as ``error``) or ``NOT_MAPPING``."""

    def __init__(self, kind: str, error: Exception | None = None):
        super().__init__(kind)
        self.kind, self.error = kind, error


def parse(text: str, *, rstrip: bool = False) -> dict | None:
    """The frontmatter mapping of ``text``; None when its first line is not ``---``; ``FrontmatterError`` when it
    opens so but cannot be read. Without ``rstrip`` the first line counts with white space either side and the
    closing line must be ``---`` exactly; with it every line loses its trailing white space first (the ticket
    files' form), and the first line must then be ``---`` exactly."""
    import yaml

    lines = text.split("\n")
    if rstrip:
        lines = [line.rstrip() for line in lines]
    if (lines[0] if rstrip else lines[0].strip()) != "---":
        return None
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise FrontmatterError(UNCLOSED) from None
    try:
        front = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as error:
        raise FrontmatterError(NOT_YAML, error) from None
    if not isinstance(front, dict):
        raise FrontmatterError(NOT_MAPPING)
    return front


def quiet(text: str) -> dict | None:
    """``parse``, with None for a frontmatter that cannot be read."""
    try:
        return parse(text)
    except FrontmatterError:
        return None


def of_file(path: Path) -> dict | None:
    """The frontmatter of the file ``path``, read as a ticket file is (``rstrip``); None when it is no file, cannot
    be read or has none."""
    try:
        return parse(Path(path).read_text(encoding="utf-8"), rstrip=True)
    except (OSError, ValueError):
        return None


def with_body(content: str) -> tuple[dict | None, str]:
    """``(frontmatter, body)``, read by text: it opens with ``---`` and closes at the next line that starts with
    ``---``, both parts stripped; ``(None, content)`` when there is none or it is not a YAML mapping."""
    import yaml

    if not content.startswith("---"):
        return None, content
    end = content.find("\n---", 3)
    if end < 0:
        return None, content
    fm_text = content[3:end].strip()
    body = content[end + 4:].strip()
    try:
        parsed = yaml.safe_load(fm_text)
    except yaml.YAMLError:
        return None, content
    if not isinstance(parsed, dict):
        return None, content
    return parsed, body


def ids(value) -> list[str]:
    """A frontmatter field of ids as a list: one string as itself, a list's non-empty items as text, else none."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value if v]
    return []
