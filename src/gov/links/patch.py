"""The two patches ``gov links`` prints and never applies (W2-129; DEC-1073 (5)(a), DEC-866).

- ``marks``: for each UNMARKED_CHANGE, its entry's status line gains `` · **Changed by:** DEC-y (the part)``, or
  `` · SUPERSEDED by DEC-y`` for a whole supersession by ids alone; the changers of one entry go on one line.
- ``sources``: for each UNLINKED_ID, its ticket's ``sources:`` gains the id.

Each is a unified diff with three lines of context, against ``HEAD``'s text, that ``git apply`` accepts.
"""

from __future__ import annotations

import difflib
import re


def _diff(path: str, before: str, after: str) -> str:
    if before == after:
        return ""
    old, new = before.splitlines(keepends=True), after.splitlines(keepends=True)
    lines = []
    for line in difflib.unified_diff(old, new, f"a/{path}", f"b/{path}", n=3):
        if not line.endswith("\n"):  # the file's last line has no newline
            line += "\n\\ No newline at end of file\n"
        lines.append(line)
    return f"diff --git a/{path} b/{path}\n" + "".join(lines)


def marks(register_path: str, register_text: str, findings: list[dict], status_lines: dict[str, int]) -> str:
    """The patch adding each UNMARKED_CHANGE's mark to its entry's status line (``status_lines``: id -> line)."""
    wanted: dict[int, list[dict]] = {}
    for finding in findings:
        if finding["code"] == "UNMARKED_CHANGE":
            wanted.setdefault(status_lines[finding["ids"][0]], []).append(finding)
    lines = register_text.split("\n")
    for number, found in wanted.items():
        whole = [f["ids"][1] for f in found if f["whole"]]
        parts = [f["mark"].removeprefix("**Changed by:** ") for f in found if not f["whole"]]
        line = lines[number - 1].rstrip()
        if whole:
            line += f" · SUPERSEDED by {', '.join(whole)}"
        if parts:
            line += f" · **Changed by:** {', '.join(parts)}"
        lines[number - 1] = line
    return _diff(register_path, register_text, "\n".join(lines))


_KEY = re.compile(r"^sources[ \t]*:[ \t]*(.*)$")


def _with_sources(text: str, ids: list[str]) -> str:
    """``text`` with ``ids`` added to its frontmatter's ``sources:`` (a block list, a flow list, or a new key)."""
    lines = text.split("\n")
    end = lines.index("---", 1) if lines and lines[0] == "---" and "---" in lines[1:] else None
    if end is None:
        return text
    for index in range(1, end):
        found = _KEY.match(lines[index])
        if not found:
            continue
        value = found.group(1).strip()
        if value.startswith("["):  # a flow list: sources: [DEC-1, DEC-2]
            inner = value.strip("[]").strip()
            lines[index] = "sources: [" + ", ".join(([inner] if inner else []) + ids) + "]"
            return "\n".join(lines)
        if value:  # one scalar: made a list
            lines[index:index + 1] = ["sources:", f"- {value}"] + [f"- {record_id}" for record_id in ids]
            return "\n".join(lines)
        last, indent = index, "- "
        for item in range(index + 1, end):
            bullet = re.match(r"^([ \t]*-[ \t]+)", lines[item])
            if bullet:
                last, indent = item, bullet.group(1)
            elif lines[item].strip() and not lines[item].startswith((" ", "\t")):
                break
        lines[last + 1:last + 1] = [f"{indent}{record_id}" for record_id in ids]
        return "\n".join(lines)
    lines[end:end] = ["sources:"] + [f"- {record_id}" for record_id in ids]
    return "\n".join(lines)


def sources(files: dict[str, str], findings: list[dict]) -> str:
    """The patch adding each UNLINKED_ID to its ticket's ``sources:`` (``files``: path -> ``HEAD``'s text)."""
    wanted: dict[str, list[str]] = {}
    for finding in findings:
        if finding["code"] == "UNLINKED_ID" and finding["ids"][0] not in wanted.get(finding["path"], []):
            wanted.setdefault(finding["path"], []).append(finding["ids"][0])
    return "".join(_diff(path, files[path], _with_sources(files[path], ids)) for path, ids in sorted(wanted.items()))
