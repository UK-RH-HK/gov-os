#!/usr/bin/env python3
"""Query instantiation (REPAIR_PLAN.md section 2.1; REPAIR_DAG.yaml node R1-GA1, repairing RC-2: "30 of 41 queries
never compiled"). ``govbridge.compile.packet._load_queries`` (out of this node's mutation scope) silently drops any
query-set entry that carries no ``text`` -- exactly the ``{class, subject}`` shape a query-DESIGN document uses. This
module is the generic fix: it reads the tables a query-set document ITSELF carries (``query_classes``, ``subjects``)
and instantiates every entry into executable text, or fails loudly with :class:`QueryNotExecutable` -- never a
silent skip.

Nothing here names a class id or a subject id: both are caller-chosen data, read generically from whatever tables
the document happens to carry (OC-BR-02).

Query-set document shape (``schemas/task-spec.yaml``'s own ``queries: 'path | list'`` field, generalised):

    schema: <any>
    query_classes: {<class id>: <str> | {template|text: <str>}}   # optional
    subjects: {<subject id>: <str> | {text|subject|description: <str>}}   # optional
    queries:
      - {id: <str>, text: <str>, routes?: [...], target_section?: <str>, ...}        # already executable
      - {id: <str>, class: <class id>, subject: <subject id>, ...}                    # instantiated from the tables

A ``{class, subject}`` entry's executable text is composed generically: if the class's own template string contains
a ``{subject}`` placeholder, ``str.format(subject=...)`` fills it; a subject that is itself a mapping additionally
offers its own fields as format arguments. A template with no placeholder at all is joined with the subject's text
by a fixed separator. Either shape a real query-set document turns out to use, this module needs no code change.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Optional

from govbridge.core.yamlutil import load_yaml_file

CODE_QUERY_NOT_EXECUTABLE = "QUERY_NOT_EXECUTABLE"


class QueryNotExecutable(Exception):
    """Raised for one query-set entry that cannot be resolved to executable text -- REPAIR_DAG.yaml node R1-GA1:
    "a query that cannot be made executable is the compile error QUERY_NOT_EXECUTABLE and is never skipped"."""
    CODE = CODE_QUERY_NOT_EXECUTABLE

    def __init__(self, query_id, reason: str):
        self.query_id = query_id
        self.reason = reason
        super().__init__(f"{self.CODE}: query {query_id!r} is not executable: {reason}")

    def to_dict(self) -> dict:
        return {"code": self.CODE, "query_id": self.query_id, "reason": self.reason}


def _as_text(value, keys=("text", "template", "subject", "description")) -> Optional[str]:
    """A generic "this table cell is text" coercion: a plain string is used as-is; a mapping is searched, in order,
    for the first of ``keys`` that itself holds a non-empty string. Anything else (a list, a number, ``None``) is
    not text. Never guesses at meaning beyond that -- a caller that gets ``None`` back treats the cell as absent."""
    if isinstance(value, str):
        return value if value.strip() else None
    if isinstance(value, dict):
        for k in keys:
            v = value.get(k)
            if isinstance(v, str) and v.strip():
                return v
    return None


def _compose(template: str, subject_text: str, subject_fields: Optional[dict]) -> str:
    """Generic composition of one class template with one subject (module docstring). A template with a ``
    {subject}`` (or, when the subject is itself a mapping, any of its own field names) placeholder is filled with
    ``str.format``; a template with no placeholder at all -- the shape REPAIR-1's own real query-set document
    uses -- is simply joined with the subject's text. ``str.format`` failures (an unknown placeholder name) fall
    back to the plain join too, rather than raising: a template's own wording is never grounds for
    QUERY_NOT_EXECUTABLE as long as a subject was actually found."""
    fmt_kwargs = {"subject": subject_text}
    if subject_fields:
        fmt_kwargs.update({k: v for k, v in subject_fields.items() if isinstance(v, str)})
    if "{" in template and "}" in template:
        try:
            return template.format(**fmt_kwargs)
        except (KeyError, IndexError, ValueError):
            pass
    return f"{template.strip()} {subject_text.strip()}".strip()


def instantiate_entry(entry: dict, query_classes: Optional[dict] = None, subjects: Optional[dict] = None) -> dict:
    """One normalised, executable query dict: ``{id, text, routes, target_section, kind, class, subject}`` (the
    last two are carried through, ``None`` when the entry was already plain text). Raises
    :class:`QueryNotExecutable` -- never returns a query with empty/missing text."""
    if not isinstance(entry, dict):
        raise QueryNotExecutable(query_id=repr(entry)[:80], reason="entry is not a mapping")
    query_id = entry.get("id")
    if not isinstance(query_id, str) or not query_id:
        raise QueryNotExecutable(query_id=repr(entry)[:80], reason="entry has no string 'id'")

    text = _as_text(entry.get("text"), keys=("text",))
    cls_id, subj_id = entry.get("class"), entry.get("subject")

    if text is None and (cls_id or subj_id):
        if not cls_id or not subj_id:
            raise QueryNotExecutable(query_id, "a {class, subject} entry needs BOTH keys; only one was given")
        query_classes = query_classes or {}
        subjects = subjects or {}
        if cls_id not in query_classes:
            raise QueryNotExecutable(query_id, f"class {cls_id!r} is not a row in this query set's query_classes table")
        if subj_id not in subjects:
            raise QueryNotExecutable(query_id, f"subject {subj_id!r} is not a row in this query set's subjects table")
        template = _as_text(query_classes[cls_id])
        if template is None:
            raise QueryNotExecutable(query_id, f"query_classes[{cls_id!r}] has no usable template text")
        subject_text = _as_text(subjects[subj_id])
        if subject_text is None:
            raise QueryNotExecutable(query_id, f"subjects[{subj_id!r}] has no usable text")
        subject_fields = subjects[subj_id] if isinstance(subjects[subj_id], dict) else None
        text = _compose(template, subject_text, subject_fields)

    if text is None or not text.strip():
        raise QueryNotExecutable(query_id, "no 'text', and no resolvable {class, subject} pair")

    return {
        "id": query_id,
        "text": text,
        "routes": entry.get("routes"),
        "target_section": entry.get("target_section"),
        "kind": entry.get("kind"),
        "class": cls_id,
        "subject": subj_id,
        "facets": entry.get("facets"),
    }


def instantiate_all(doc: dict) -> list:
    """Every entry of ``doc['queries']``, instantiated in order. Raises :class:`QueryNotExecutable` on the FIRST
    entry that cannot be made executable -- REPAIR_DAG.yaml node R1-GA1: "the compiler never skips it" (a caller
    that wants a best-effort partial list, e.g. to report every bad entry at once, catches per-entry itself; this
    function's own contract is "all or a named failure," matching the deliverable text exactly)."""
    query_classes = doc.get("query_classes")
    subjects = doc.get("subjects")
    queries = doc.get("queries") or []
    return [instantiate_entry(q, query_classes=query_classes, subjects=subjects) for q in queries]


def load_query_set(raw, repo: Optional[str] = None, base_dir: Optional[str] = None) -> dict:
    """Resolve ``schemas/task-spec.yaml``'s own ``queries: 'path | list'`` field into the FULL query-set document
    (never just the flat, text-only list ``govbridge.compile.packet._load_queries`` reduces it to -- that reduction
    is RC-2 itself). ``raw`` is a task spec's ``queries`` value: a list (already the entries), a path to a document
    whose own top-level ``queries`` is the entries (optionally alongside ``query_classes``/``subjects``), or a bare
    list document at that path."""
    if raw is None:
        return {"queries": []}
    if isinstance(raw, list):
        return {"queries": raw}
    if isinstance(raw, str):
        import os
        path = raw if os.path.isabs(raw) or not base_dir else os.path.join(base_dir, raw)
        doc = load_yaml_file(path)
        if isinstance(doc, list):
            return {"queries": doc}
        if isinstance(doc, dict):
            return doc
        return {"queries": []}
    return {"queries": []}


def find_raw_entry(doc: dict, query_id: str) -> Optional[dict]:
    for q in doc.get("queries") or []:
        if isinstance(q, dict) and q.get("id") == query_id:
            return q
    return None


def resolve_query(doc: dict, query_id_or_text: str) -> dict:
    """The one entry point ``govbridge gather --query <id|text>`` uses: if ``query_id_or_text`` names an entry in
    ``doc['queries']``, instantiate exactly that entry (never scanning or validating the rest of the query set --
    an unrelated malformed entry elsewhere in the file must not block a caller asking for a different, healthy one).
    Otherwise ``query_id_or_text`` is treated as literal, already-executable ad hoc text, with a synthesised id."""
    entry = find_raw_entry(doc, query_id_or_text)
    if entry is not None:
        return instantiate_entry(entry, query_classes=doc.get("query_classes"), subjects=doc.get("subjects"))
    from govbridge.core.yamlutil import sha256_text
    return {
        "id": f"adhoc:{sha256_text(query_id_or_text)[:12]}",
        "text": query_id_or_text,
        "routes": None,
        "target_section": None,
        "kind": "adhoc",
        "class": None,
        "subject": None,
        "facets": None,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.gather.instantiate")
    p.add_argument("query_set_path")
    args = p.parse_args(argv)

    doc = load_yaml_file(args.query_set_path)
    try:
        result = instantiate_all(doc)
    except QueryNotExecutable as exc:
        print(json.dumps(exc.to_dict(), indent=1, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
