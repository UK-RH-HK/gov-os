"""The retrieval learning loop: a miss is a memory-quality event with its root cause, its repair and a held-out
regression case (W2-32 S3; CAP-19.c, Framework v4.1.2 §18; P-W2-32-1).

``record(root, miss)`` takes a miss as a map:

- ``question``: the question retrieval missed;
- ``expected``: the sources the answer needed, ``[{"path": ...}, ...]``;
- ``observed``: the paths retrieval gave first (optional, a list);
- ``root_cause`` and ``repair``: why it was missed and what was changed (text, or a map of text);
- ``regression``: a case in the standing measure's question form (``question``, ``gold_answer``, ``sources``;
  ``gov.retrieval.measure``) that fails while the miss stands and passes once it is repaired.

A miss without any of these parts, or a case without its own, raises ``ValueError`` naming the part, and nothing is
written. Otherwise the case is written as a file of its own under ``CASES_REL`` and the event under ``EVENTS_REL``,
both YAML in the project and outside ``.gov-runtime/``, so they are kept with the tree. The folder is never embedded
(``gov.retrieval.semantic`` leaves it out whatever the path map says), as tests and probe records stay out of memory
(DEC-1052): the case is held out. ``events(root)`` lists every event recorded, oldest first.
"""

from __future__ import annotations

import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

LEARNING_REL = "fixtures/memory-quality"
EVENTS_REL, CASES_REL = f"{LEARNING_REL}/events", f"{LEARNING_REL}/cases"
TYPE = "memory-quality"
REQUIRED = ("question", "expected", "root_cause", "repair", "regression")
CASE_REQUIRED = ("question", "gold_answer", "sources")
FIELDS = ("id", "type", "question", "root_cause", "repair", "path", "regression_case")


def _empty(value) -> bool:
    return value is None or (isinstance(value, (str, list, dict, tuple)) and not (
        value.strip() if isinstance(value, str) else value))


def _text(value, name: str) -> str | dict:
    """``value`` as text, or a map of text: what a root cause or a repair may be."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict) and all(isinstance(key, str) for key in value):
        return value
    raise ValueError(f"the miss's {name} must be text or a map, not {type(value).__name__}")


def _source(entry, where: str) -> None:
    alternatives = entry if isinstance(entry, list) else [entry]
    if not alternatives or not all(isinstance(a, dict) and isinstance(a.get("path"), str) and a["path"].strip()
                                   for a in alternatives):
        raise ValueError(f"{where}: a source names no path")


def _checked(miss) -> dict:
    """The miss's parts, each checked; raises ``ValueError`` naming the first part missing or malformed."""
    if not isinstance(miss, dict):
        raise ValueError("a miss must be a map with question, expected, root_cause, repair and regression")
    for name in REQUIRED:
        if _empty(miss.get(name)):
            raise ValueError(f"the miss has no {name}")
    if not isinstance(miss["question"], str):
        raise ValueError("the miss's question must be text")
    expected = miss["expected"]
    if not isinstance(expected, list):
        raise ValueError("the miss's expected must be a list of sources")
    for entry in expected:
        _source(entry, "the miss's expected")
    observed = miss.get("observed") or []
    if not isinstance(observed, list) or not all(isinstance(path, str) for path in observed):
        raise ValueError("the miss's observed must be a list of paths")
    case = miss["regression"]
    if not isinstance(case, dict):
        raise ValueError("the miss's regression must be a case: a map with question, gold_answer and sources")
    for name in CASE_REQUIRED:
        if _empty(case.get(name)):
            raise ValueError(f"the regression case has no {name}")
    if not isinstance(case["question"], str):
        raise ValueError("the regression case's question must be text")
    if not isinstance(case["sources"], list):
        raise ValueError("the regression case's sources must be a list")
    for entry in case["sources"]:
        _source(entry, "the regression case's sources")
    return {"question": miss["question"].strip(), "expected": expected, "observed": observed,
            "root_cause": _text(miss["root_cause"], "root_cause"), "repair": _text(miss["repair"], "repair"),
            "regression": case}


def _new_id(root: Path, question: str, now: datetime) -> str:
    stem = f"MQ-{now:%Y%m%dT%H%M%SZ}-{hashlib.sha256(question.encode('utf-8', 'surrogatepass')).hexdigest()[:8]}"
    n, name = 1, stem
    while (root / EVENTS_REL / f"{name}.yaml").exists() or (root / CASES_REL / f"{name}.yaml").exists():
        n, name = n + 1, f"{stem}-{n + 1}"
    return name


def _write(path: Path, document: dict) -> None:
    """``document`` as YAML at ``path``, whole or not at all."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            yaml.safe_dump(document, out, sort_keys=False, allow_unicode=True)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def record(root, miss) -> dict:
    """Record ``miss`` as a memory-quality event with its held-out regression case; the event, as ``events`` gives
    it. Raises ``ValueError`` naming a missing part, and then writes nothing."""
    root = Path(root)
    parts = _checked(miss)
    now = datetime.now(timezone.utc)
    event_id = _new_id(root, parts["question"], now)
    case_rel, event_rel = f"{CASES_REL}/{event_id}.yaml", f"{EVENTS_REL}/{event_id}.yaml"
    event = {"id": event_id, "type": TYPE, "question": parts["question"], "root_cause": parts["root_cause"],
             "repair": parts["repair"], "path": event_rel, "regression_case": case_rel,
             "expected": parts["expected"], "observed": parts["observed"],
             "recorded_at": now.strftime("%Y-%m-%dT%H:%M:%SZ")}
    _write(root / case_rel, {"id": event_id, **parts["regression"]})
    try:
        _write(root / event_rel, event)
    except BaseException:
        (root / case_rel).unlink(missing_ok=True)  # no case without its event
        raise
    return event


def events(root) -> list[dict]:
    """Every memory-quality event recorded at ``root``, oldest first (by id). A file that is no event is skipped."""
    folder = Path(root) / EVENTS_REL
    found = []
    for path in sorted(folder.glob("*.yaml")) if folder.is_dir() else []:
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError):
            continue
        if isinstance(document, dict) and document.get("type") == TYPE and all(key in document for key in FIELDS):
            found.append(document)
    return found
