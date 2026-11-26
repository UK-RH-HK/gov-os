"""The plan file: one JSON object a line, nine fields on each (SL-5), each line's own faults (SL-8), and the hash of
a plan at a standard and a commit (SL-13)."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from dataclasses import dataclass, field

from gov.layout.standard import ASK, Standard

FIELDS = ("path", "class", "destination", "reason", "kind", "stale_class", "import", "sign", "ask")
PROVENANCE = ("chunk", "agent")  # may be written; no check judges them
KINDS = ("file", "folder", "untracked", "ignored-root", "submodule", "declared")
SIGNS = ("path", "manifest", "licence", "header", "front-matter", "history", "imports", "content", "registry")
_MOST_COPIES = 10  # the most paths one reason may stand on


def finding(code: str, line: int | None, path: str, message: str, **more) -> dict:
    return {"code": code, "line": line, "path": path, "message": message, **more}


@dataclass
class Line:
    number: int
    path: str
    data: dict
    pinned: bool = False        # it never moves
    moving: bool = False        # the plan moves it
    expected: str = ""          # where the standard puts it
    root: str = ""              # an import line's import root
    items: list = field(default_factory=list)  # the items it covers

    def text(self, key: str) -> str:
        value = self.data.get(key)
        return value if isinstance(value, str) else ""

    @property
    def cls(self) -> str:
        return self.text("class")

    @property
    def kind(self) -> str:
        return self.text("kind")

    @property
    def dest(self) -> str:
        return self.text("destination")

    @property
    def name(self) -> str:
        return self.text("import")


def _path_ok(path, kind) -> bool:
    if not isinstance(path, str) or not path or path.endswith("/") or "\0" in path:
        return False
    # declared material may lie outside the tree, and is named as the register names it
    return kind == "declared" or not (path.startswith("/") or {"", ".", ".."} & set(path.split("/")))


def read(text: str, std: Standard) -> tuple[list[Line], list[dict], list[str]]:
    """``(the lines that name a path, the faults, the canonical form of every line)`` of the plan ``text``."""
    lines, faults, canonical = [], [], []
    for number, raw in enumerate(text.split("\n"), 1):
        if not raw.strip():
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            data = None
        if not isinstance(data, dict):
            canonical.append(raw.strip())
            faults.append(finding("LAYOUT_INVALID", number, "", "the line is no JSON object", field="line"))
            continue
        canonical.append(json.dumps({key: value for key, value in data.items() if key not in PROVENANCE},
                                    sort_keys=True, ensure_ascii=False, separators=(",", ":")))
        path = data.get("path")
        named = path if isinstance(path, str) else ""

        def fault(key: str, message: str) -> None:
            faults.append(finding("LAYOUT_INVALID", number, named, message, field=key))

        for key in FIELDS:
            if key not in data:
                fault(key, f"the field {key} is missing")
        for key in sorted(set(data) - set(FIELDS) - set(PROVENANCE)):
            fault(key, f"{key} is no field of a plan line")
        _values(data, std, fault)
        if _path_ok(path, data.get("kind")):
            lines.append(Line(number, path, data))
    return lines, faults + _copied(lines), canonical


def _values(data: dict, std: Standard, fault) -> None:
    """A fault for each field present whose value is not one the field takes on this line."""
    name = data.get("class")
    known = isinstance(name, str) and (name == ASK or name in std.classes)

    def check(key: str, ok: bool, message: str) -> None:
        if key in data and not ok:
            fault(key, message)

    def one_of(value, allowed) -> bool:
        return isinstance(value, str) and value in allowed

    check("path", _path_ok(data.get("path"), data.get("kind")),
          "path is a repository-relative path with / and no trailing slash")
    check("class", known, "class is not in the standard's closed list, nor ask")
    check("kind", one_of(data.get("kind"), KINDS), "kind is one of " + ", ".join(KINDS))
    check("sign", one_of(data.get("sign"), SIGNS), "sign is one of " + ", ".join(SIGNS))
    check("destination", isinstance(data.get("destination"), str) and bool(data.get("destination")),
          "destination is empty or no text")
    reason = data.get("reason")
    check("reason", isinstance(reason, str) and bool(reason.strip()), "reason is empty or no text")
    if not known:
        return
    if std.stale(name):
        check("stale_class", one_of(data.get("stale_class"), std.stale_classes),
              "this class needs a stale class: " + ", ".join(std.stale_classes))
    else:
        check("stale_class", data.get("stale_class") is None, "only an archive line has a stale class")
    if std.whole(name):
        value = data.get("import")
        check("import", isinstance(value, str) and bool(value.strip()) and "/" not in value
              and value not in (".", ".."), "an import class needs the import's name, one folder name")
    else:
        check("import", data.get("import") is None, "only an import class has an import name")
    ask = data.get("ask")
    if name == ASK:
        check("ask", isinstance(ask, dict) and isinstance(ask.get("question"), str) and bool(ask["question"].strip())
              and one_of(ask.get("recommended"), std.classes),
              "an ask line needs a question and a recommended class")
    else:
        check("ask", ask is None, "only an ask line has an ask value")


def _copied(lines: list[Line]) -> list[dict]:
    reasons = defaultdict(list)
    for line in lines:
        if line.text("reason").strip():
            reasons[line.text("reason").strip()].append(line)
    return [finding("LAYOUT_INVALID", line.number, line.path,
                    f"one reason stands on {len({each.path for each in same})} paths, more than {_MOST_COPIES}",
                    field="reason")
            for same in reasons.values() if len({each.path for each in same}) > _MOST_COPIES for line in same]


def digest(canonical: list[str], version: int, commit: str) -> str:
    """The plan's hash: its lines whatever their order, the standard's version and the commit."""
    return hashlib.sha256(json.dumps([sorted(canonical), version, commit]).encode("utf-8")).hexdigest()
