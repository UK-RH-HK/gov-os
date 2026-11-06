"""Build ``.gov-runtime/store.db``: the record graph, derived from git alone (DEC-012).

Everything is read from ``HEAD``, never from the working tree, so the same
commit gives the same store wherever and whenever it is loaded.

- A record is a Markdown file whose YAML frontmatter carries an ``id``. ``id``,
  ``type`` and ``status`` are required (DEC-239); the path is derived, not
  stored. A record that cannot be loaded is returned in ``invalid`` by its path
  and stops no other record.
- An edge's frontmatter key is its type in lower case, from the record that
  carries the key to each id listed. ``superseded_by`` gives the SUPERSEDES edge
  from the successor. A dangling edge is stored like any other.
- Each entry of the register file that the path map of ``HEAD`` names under ``decision_register`` is a record of
  type ``decision`` (DEC-521, DEC-473, DEC-479): its id is the heading's, its status the word after
  ``**Status:**`` on its first line that is not blank, its path the register file. Its heading, title, span and
  ``content_hash`` are kept in ``register_entries`` (AR-1): the span is its own text, the hash the sha256 of it.
  A heading alone, one inside an HTML comment, an id outside the ``decision_id`` grammar, a status word not in
  capitals and an id under two headings make no record (W2-L221, W2-M145, W2-M106). A named register that
  ``HEAD`` does not hold as a file of text refuses the load (DEC-579: one that is not in the commit too).
- A record of a file whose frontmatter ``title`` is a string keeps it in ``record_titles`` (W2-92 S6), outside the
  digest.
- The links the records state that no edge holds are kept in ``stated_links`` (W2-92 S7, DEC-1072 (1)), outside the
  digest: a record's frontmatter id keys (``CITE_KEYS`` as CITES, ``task`` as OF_TASK, a W2 id read through
  ``wbs_id``/``external-ref``), and the register's statements (``register_statements``): a supersession that names
  ids alone as SUPERSEDES, any other supersession or amendment as AMENDS, ``**Under:**`` as UNDER.
- ``Task:`` and ``Implements:`` trailers are read from the final trailer block;
  a commit made before 2026-10-03 is read from the whole message (DEC-182).
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
from pathlib import Path

from gov.cli.errors import GovError
from gov.util.gitenv import git_env

STORE_REL = ".gov-runtime/store.db"
EDGE_TYPES = ("EVIDENCE_FOR", "CONSTRAINS", "IMPLEMENTS", "TESTS", "GENERATES", "VALIDATES", "SUPERSEDES",
              "DEPENDS_ON")
REQUIRED = ("id", "type", "status")
TRAILER_RULE_DATE = "2026-10-03"  # DEC-182; compared with the committer date, in the commit's own time zone
PATH_MAP_REL = "governance/project/path-map.yaml"
REGISTER_KEY = "decision_register"  # DEC-479
REGISTER_TABLE = "register_entries"

# DEC-473 read through the kernel's decision_id grammar (common.schema.json): a level-3 heading at the start of a
# line, the id of three digits or more, a space, a colon or a dash, and the title
_ENTRY = re.compile(r"### (DEC-[0-9]{3,})(?=[ :\-–—])[ \t:\-–—]*([^\s:\-–—].*)")
_NOT_AN_ID = re.compile(r"### ((?i:dec)-[0-9]+)(?=[ :\-–—])")  # the heading's form, with an id outside the grammar
_HEADING = re.compile(r"#{1,6}(?:\s|$)")
_FENCE = re.compile(r" {0,3}(`{3,}|~{3,})")
_STATUS = re.compile(r"\s*(?:[-*+]\s+)?\*\*Status:\*\*\s*([A-Za-z][A-Za-z_-]*)")
_CANONICAL = re.compile(r"[A-Z][A-Z_-]*")  # a status word in capitals, as the sources write it (W2-M106)
_SUPERSEDES = re.compile(r"\*\*Supersedes:\*\*([^·]*)")
_IDS_ALONE = re.compile(r"DEC-[0-9]+(?:(?:\s*,\s*|\s+and\s+)DEC-[0-9]+)*")

_TRAILER = re.compile(r"^(Task|Implements):[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
_LOG_FORMAT = "--format=%x1e%H%x1f%cs%x1f%(trailers:key=Task,key=Implements,unfold)%x1f%B%x1f"
_TABLES = {
    "records": "path TEXT, id TEXT NOT NULL, type TEXT NOT NULL, status TEXT NOT NULL, PRIMARY KEY (path, id)",
    "edges": "type TEXT, source TEXT, target TEXT, PRIMARY KEY (type, source, target)",
    "commits": "id TEXT PRIMARY KEY",
    "trailers": "commit_id TEXT, key TEXT, value TEXT, PRIMARY KEY (commit_id, key, value)",
    "commit_paths": "commit_id TEXT, path TEXT, PRIMARY KEY (commit_id, path)",
    REGISTER_TABLE: "id TEXT PRIMARY KEY, heading TEXT NOT NULL, title TEXT NOT NULL, span TEXT NOT NULL,"
                    " content_hash TEXT NOT NULL",
}
# W2-92 S6 (DEC-1065 (4)): the frontmatter ``title`` of each record of a file, parsed once at the load, so the record
# route of a plain question reads the titles here instead of parsing every record's file in each process. A table of
# its own (a column of ``records`` would clash with ``register_entries.title`` in the joined query), kept out of the
# digest like the fingerprints row, so the digest of a commit is unchanged; it is part of the schema version
# (``rebuild/seed.py``), so a warm base built without it is refused.
TITLES_TABLE = "record_titles"
_TABLES[TITLES_TABLE] = "path TEXT, id TEXT, title TEXT NOT NULL, PRIMARY KEY (path, id)"
# W2-92 S7 (DEC-1072 (1), the census's kinds 1 to 4): the links the records state between records that no edge holds,
# typed, from the record that states them; ``via`` names the key or the register's form that stated it (the first of
# them, sorted). A table of its own, so the closure, ``gov dangling`` and every reader of ``edges`` are unchanged; kept
# out of the digest like the titles; part of the schema version. Only links whose two ends are records are kept, and
# none that ``edges`` already holds with the same type.
LINKS_TABLE = "stated_links"
_TABLES[LINKS_TABLE] = "type TEXT, source TEXT, target TEXT, via TEXT NOT NULL, PRIMARY KEY (type, source, target)"
CITES = "CITES"  # a record -> a decision, capability or record it rests on (sources:, decisions:, closes:, ...)
OF_TASK = "OF_TASK"  # a checkpoint or close record -> its ticket (task:)
SUPERSEDES = "SUPERSEDES"  # a decision -> a decision it supersedes whole: the statement names ids alone
AMENDS = "AMENDS"  # a decision -> a decision it changes in part: amendments, and supersessions of a part
UNDER = "UNDER"  # a decision -> a decision it stands under (**Under:**)
LINK_TYPES = (CITES, OF_TASK, SUPERSEDES, AMENDS, UNDER)
CITE_KEYS = ("sources", "closes", "decisions", "decisions_applied", "decisions_carried", "decisions_recorded",
             "decisions_read", "requirements_implemented")
TASK_KEYS = ("task",)
ALIAS_KEYS = ("wbs_id", "external-ref")  # a W2 id stands for the record whose frontmatter names it
_DIGESTED = tuple(table for table in _TABLES
                  if table not in (TITLES_TABLE, LINKS_TABLE))  # register_entries stays the last of them
# W2-68: the one row of the load that built the store (its head, the head's two fingerprints, the kind of load),
# kept out of the graph's tables and out of the digest, so the recovery-rebuild check (CAP-38.b) is unchanged.
FINGERPRINTS_TABLE = "fingerprints"
_FINGERPRINTS = "head TEXT NOT NULL, code TEXT, records TEXT, kind TEXT NOT NULL"
REBUILD, RECORDS = "rebuild", "records"


def _git(root: Path, *args: str, stdin: bytes | None = None) -> bytes:
    try:
        return subprocess.run(["git", "-C", str(root), *args], input=stdin, capture_output=True, check=True,
                              env=git_env(root, pinned=True)).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        reason = " ".join(getattr(exc, "stderr", b"").decode("utf-8", "replace").split()) or str(exc)
        raise GovError("STORE_GIT_FAILED", f"git {args[0]} failed in {root}: {reason}", {"root": str(root)}) from None


def _tree(root: Path) -> dict[str, tuple[str, str, str]]:
    """``path -> (mode, type, object id)`` of every entry of ``HEAD``."""
    entries = {}
    for entry in _git(root, "ls-tree", "-r", "-z", "HEAD").decode("utf-8", "replace").split("\0"):
        meta, _, path = entry.partition("\t")
        if path:
            entries[path] = tuple(meta.split())
    return entries


def _file(root: Path, tree: dict, path: str) -> str | None:
    """The text ``HEAD`` holds at ``path``; None where it holds no file of UTF-8 text there (a link is no file)."""
    mode, kind, sha = tree.get(path, ("", "", ""))
    if kind != "blob" or mode == "120000":
        return None
    try:
        text = _git(root, "cat-file", "blob", sha).decode("utf-8")
    except UnicodeDecodeError:
        return None
    return None if "\0" in text else text


def _register(root: Path, tree: dict) -> tuple[str, str] | None:
    """``(path, text)`` of the register file the path map of ``HEAD`` names; None where it names none."""
    import yaml

    def unreadable(named: str, why: str) -> GovError:
        return GovError("STORE_REGISTER_UNREADABLE", f"{named}: {why}; the decisions of the register are not loaded",
                        {"root": str(root), "named": named})

    if PATH_MAP_REL not in tree:
        return None
    try:
        path_map = yaml.safe_load(_file(root, tree, PATH_MAP_REL) or "")
    except yaml.YAMLError:
        path_map = None
    if not isinstance(path_map, dict):
        raise unreadable(REGISTER_KEY, f"{PATH_MAP_REL} cannot be read as a mapping, so whether it names a register "
                                       "is not known")
    if REGISTER_KEY not in path_map:
        return None
    path = path_map[REGISTER_KEY]
    if not isinstance(path, str) or not path.strip():
        raise unreadable(REGISTER_KEY, f"the key of {PATH_MAP_REL} is not a path")
    text = _file(root, tree, path)  # a named register that is not in the commit is refused, never no register (DEC-579)
    if text is None:
        raise unreadable(path, f"HEAD does not hold the register named under '{REGISTER_KEY}' as a file of text")
    return path, text


def register_entries(text: str) -> tuple[list[dict], list[str]]:
    """The live entries of a register's ``text``, and the reason each heading of the entry form is no entry.

    A live entry is a heading of DEC-473's grammar outside fenced code blocks and HTML comments, whose first line
    that is not blank is a status line with a word in capitals (W2-L221, W2-M145, W2-M106). Its ``span`` is its own
    text, from its heading to the line before the next heading, without the blank lines that end it; its
    ``content_hash`` is the sha256 of the span (AR-1). An id under two headings is no entry, named with both lines.
    The store and the decision-citations check count entries by this one rule.
    """
    lines, ends, heads, fence, comment = text.split("\n"), [], [], None, False
    for number, line in enumerate(lines):
        mark = _FENCE.match(line)
        if fence is not None:
            if mark and mark.group(1).startswith(fence) and not line[mark.end():].strip():
                fence = None  # closed by a fence of the same mark, at least as long, with nothing after it
        elif comment:
            comment = "-->" not in line
            if _HEADING.match(line):
                ends.append(number)
        elif mark:
            fence = mark.group(1)
        else:
            if _HEADING.match(line):
                ends.append(number)
                heads.append(number)
            if "<!--" in line:
                comment = "-->" not in line.rpartition("<!--")[2]
    ends.append(len(lines))
    found, refused = {}, []
    for number in heads:
        entry = _ENTRY.match(lines[number])
        if not entry:
            outside = _NOT_AN_ID.match(lines[number])
            if outside:
                refused.append(f"{outside.group(1)} at line {number + 1} is no id of the decision_id grammar "
                               "((ADR|DEC)-[0-9]{3,}): the heading is no record")
            continue
        own = lines[number:next(at for at in ends if at > number)]
        while not own[-1].strip():
            own.pop()
        span = "\n".join(own)
        found.setdefault(entry.group(1), []).append({
            "id": entry.group(1), "line": number + 1, "heading": lines[number].rstrip(),
            "title": entry.group(2).strip(), "first": next((line for line in own[1:] if line.strip()), ""),
            "span": span, "content_hash": hashlib.sha256(span.encode("utf-8")).hexdigest()})
    live = []
    for record_id, entries in found.items():
        status = _STATUS.match(entries[0]["first"])
        if len(entries) > 1:
            *some, last = [str(entry["line"]) for entry in entries]
            refused.append(f"{record_id} stands under {len(entries)} headings of the register, at lines "
                           f"{', '.join(some)} and {last}: none of them is a record")
        elif not status:
            refused.append(f"{record_id} at line {entries[0]['line']} has no status line (`**Status:**` and a word, "
                           "first under its heading)")
        elif not _CANONICAL.fullmatch(status.group(1)):
            refused.append(f"{record_id} at line {entries[0]['line']}: its status word {status.group(1)!r} is not "
                           "canonical (a word in capitals, as the sources write it): the entry is no record")
        else:
            live.append({**entries[0], "status": status.group(1)})
    return live, refused


def _read_register(path: str, text: str, recorded: dict[str, str]):
    """The decision records, the SUPERSEDES edges, the headings, the entries that are no records of a register and
    its statements of change and governance (``register_statements``).

    ``recorded`` is ``id -> path`` of the records of the files: an id a file records is the file's, never two.
    """
    entries, refused = register_entries(text)
    records, edges, headings = [], set(), []
    invalid = [{"path": path, "reason": reason} for reason in refused]
    for entry in entries:
        record_id = entry["id"]
        if record_id in recorded:
            invalid.append({"path": path, "reason": f"{record_id} is recorded by the decision file "
                                                    f"{recorded[record_id]} and by the heading at line "
                                                    f"{entry['line']} of the register: the entry is no record"})
            continue
        records.append((path, record_id, "decision", entry["status"]))
        headings.append((record_id, entry["heading"], entry["title"], entry["span"], entry["content_hash"]))
        superseded = _SUPERSEDES.search(entry["first"])
        if superseded and _IDS_ALONE.fullmatch(superseded.group(1).strip()):  # a part of a decision gives none
            edges.update(("SUPERSEDES", record_id, target)
                         for target in re.findall(r"DEC-[0-9]+", superseded.group(1)))
    return records, edges, headings, invalid, register_statements(text, entries)


# The register's statements of change and governance, by the census's own patterns (docs/research/D4B-link-census.py,
# §1): a label ``**Name:**`` and its value; ``Changed by``-like labels state the change from the other side; free text
# "... amended by DEC-n" takes the nearest id before it as its subject; the change log outside the entries is read too.
# Every pattern is a regular expression, approximate where the census says so. ``gov links`` (W2-129) reads these too.
_LABEL = re.compile(r"\*\*([A-Z][A-Za-z ]{1,40}?):\*\*")
_DEC = re.compile(r"\bDEC-(\d{3,})\b")
_OUT_LABELS = {  # this entry -> the ids its value names
    "Supersedes": "supersede", "Replaces": "supersede", "Withdraws": "supersede", "Reverses": "supersede",
    "Narrows": "amend", "Restores": "amend", "Clarifies": "refine",
    "Amends": "amend", "Changes": "amend", "Corrects": "amend",
    "Refines": "refine", "Extends": "extend", "Settles": "settle", "Ratifies": "ratify", "Confirms": "confirm",
    "Implements": "implement", "Under": "under", "Source": "source",
}
_IN_LABELS = ("Changed by", "Amended by", "Lifted by", "Superseded by", "Amended")  # the ids named -> this entry
_VERB_CLASS = {"supersed": "supersede", "replac": "supersede", "withdr": "supersede", "revers": "supersede",
               "overturn": "supersede", "end": "supersede", "amend": "amend", "correct": "amend", "chang": "amend",
               "lift": "amend", "refin": "refine", "extend": "extend", "settl": "settle", "mark": "mark",
               "shown": "mark", "show": "mark", "carri": "carry", "kept": "mark", "confirm": "confirm"}
_BY = re.compile(r"\b(superseded|replaced|withdrawn|reversed|overturned|ended|amended|corrected|changed|lifted|refined|"
                 r"extended|settled|marked|shown|carried|kept|confirmed)\b[^.;·]{0,60}?\bby\s+(?:the\s+)?((?:DEC-\d{3,}"
                 r"(?:\s*\([^)]{0,40}\))?(?:\s*(?:item|items|Q)\s*[\w.]+(?:\s*(?:and|,)\s*[\w.]+)*)?"
                 r"(?:\s*,\s*|\s+and\s+)?)+)")
_OUTVERB = re.compile(r"\b(supersedes|replaces|withdraws|amends|overturns|reverses|corrects|refines|extends)\s+"
                      r"(?:the\s+[^.;·]{0,40}?of\s+)?(DEC-\d{3,})")
_HERE = re.compile(r"(DEC-\d{3,})((?:\s*\([^)]*\))*?)\s*\((?:[^)]*?\b)?(amended|superseded|replaced|changed|withdrawn)"
                   r" here")


def _verb_class(verb: str) -> str:
    v = verb.lower()
    return next((kind for stem, kind in _VERB_CLASS.items() if v.startswith(stem)), "amend")


def _alone(value: str) -> bool:
    """The value names decisions alone (whole): ids, commas, 'and', dates in parentheses; nothing else."""
    rest = re.sub(r"\(\d{4}-\d{2}-\d{2}[^)]*\)", "", value)
    rest = re.sub(r"\(owner[^)]*\)", "", rest)
    rest = _DEC.sub("", rest)
    return re.sub(r"\b(and|by)\b|[,.;\s]", "", rest) == ""


def _entry_statements(entry: dict) -> list[dict]:
    """One entry's statements, in the census's order (its labels, then its free text)."""
    me, span, found = entry["id"], entry["span"], []

    def said(source, target, cls, form, whole, where):
        found.append({"source": source, "target": target, "cls": cls, "form": form, "whole": whole, "where": where})

    labels, consumed = list(_LABEL.finditer(span)), []
    for index, label in enumerate(labels):
        name = label.group(1).strip()
        end = labels[index + 1].start() if index + 1 < len(labels) else len(span)
        value = span[label.end():end]
        line = (value.split("\n- **")[0] if name == "Changes" else value.split("\n- ")[0]).split(" · ")[0]
        if name in _OUT_LABELS:
            consumed.append((label.start(), label.end() + len(line)))
            for target in _DEC.finditer(line):
                if target.group(0) != me:
                    said(me, target.group(0), _OUT_LABELS[name], f"**{name}:**", _alone(line), "label")
            if name == "Under":  # "DEC-x (amended here)" inside an Under value
                for here in _HERE.finditer(line):
                    said(me, here.group(1), _verb_class(here.group(3)), "(amended here)", False, "label")
        elif name in _IN_LABELS:
            consumed.append((label.start(), label.end() + len(line)))
            whole = bool(re.match(r"\s*(superseded|replaced|withdrawn)\s+by", line)) and _alone(
                re.sub(r"\b(superseded|replaced|withdrawn)\b", "", line))
            by = [(b.group(1), t) for b in _BY.finditer(line) for t in _DEC.findall(b.group(2))]
            for verb, target in by:
                said("DEC-" + target, me, _verb_class(verb), f"**{name}:** {verb} by", whole, "label")
            if not by:  # "**Changed by:** DEC-953 (item 3)": a change with no verb
                for target in _DEC.findall(line):
                    said("DEC-" + target, me, "supersede" if name == "Superseded by" else "amend", f"**{name}:**",
                         False, "label")
        elif name == "Superseded":  # "**Superseded:** DEC-002 (by DEC-058, DEC-064); ..."
            consumed.append((label.start(), label.end() + len(line)))
            for target, by in re.findall(r"(DEC-\d{3,})\s*\(by ([^)]*)\)", line):
                for source in _DEC.findall(by):
                    said("DEC-" + source, target, "supersede", "**Superseded:** X (by Y)", True, "label")

    def free(at: int) -> bool:
        return not any(a <= at < b for a, b in consumed)

    for b in _BY.finditer(span):  # free text: "... superseded by DEC-x": the subject is the nearest id before
        if not free(b.start()):
            continue
        clause = re.split(r"(?<=\.)\s|·|\n", span[max(0, b.start() - 160):b.start()])[-1]
        if clause.count('"') % 2 or clause.count("“") > clause.count("”"):
            continue  # inside a quotation: an example, not a statement
        subject = _DEC.findall(clause.split(";")[-1]) or re.findall(r"DEC-(\d{3,})['’]s\b", clause)
        target = "DEC-" + subject[-1] if subject else me
        for source in _DEC.findall(b.group(2)):
            if "DEC-" + source != target:
                said("DEC-" + source, target, _verb_class(b.group(1)), f"text: {b.group(1)} by", False, "text")
    for o in _OUTVERB.finditer(span):
        if not free(o.start()):
            continue
        clause = re.split(r"(?<=\.)\s|·|\n", span[max(0, o.start() - 120):o.start()])[-1]
        if clause.count('"') % 2:
            continue
        subject = _DEC.findall(clause)
        source = "DEC-" + subject[-1] if subject else me
        if o.group(2) != source:
            said(source, o.group(2), _verb_class(o.group(1)), f"text: {o.group(1)}", False, "text")
    for here in _HERE.finditer(span):
        if free(here.start()) and here.group(1) != me:
            said(me, here.group(1), _verb_class(here.group(3)), "text: (… here)", False, "text")
    return found


def register_statements(text: str, entries: list[dict] | None = None) -> list[dict]:
    """The register's statements that one decision supersedes, amends, stands under, refines, ... another, by the
    census's patterns: ``{source, target, cls, form, whole, where}``, ``source`` the deciding decision, ``cls`` one of
    supersede, amend, under, refine, extend, settle, ratify, confirm, implement, source, mark, carry; ``whole`` where
    the statement names ids alone; ``where`` label, text or preamble (the change log outside the entries).

    ``text`` is the register's; ``entries`` its ``register_entries(text)[0]`` where the caller holds them. One
    statement per (source, target, cls, form) within the entries, then the change log's, as the census counts them.
    """
    if entries is None:
        entries = register_entries(text)[0]
    found, seen = [], set()
    for entry in entries:
        for statement in _entry_statements(entry):
            key = (statement["source"], statement["target"], statement["cls"], statement["form"])
            if key not in seen:
                seen.add(key)
                found.append(statement)
    inside = set()
    for entry in entries:
        inside.update(range(entry["line"], entry["line"] + entry["span"].count("\n") + 1))
    preamble = "\n".join(line for number, line in enumerate(text.split("\n"), 1) if number not in inside)
    for o in _OUTVERB.finditer(preamble):  # the change log: "DEC-051 (...; supersedes DEC-048)"
        subject = _DEC.findall(preamble[max(0, o.start() - 120):o.start()])
        if subject:
            found.append({"source": "DEC-" + subject[-1], "target": o.group(2), "cls": _verb_class(o.group(1)),
                          "form": f"change log: {o.group(1)}", "whole": False, "where": "preamble"})
    return found


def _link_type(statement: dict) -> str | None:
    """The stated link a register statement gives: UNDER, SUPERSEDES (a whole supersession), AMENDS (any other
    supersession or amendment), or None (a refinement, a confirmation, a source, ...)."""
    if statement["cls"] == "under":
        return UNDER
    if statement["cls"] == "supersede" and statement["whole"]:
        return SUPERSEDES
    return AMENDS if statement["cls"] in ("supersede", "amend") else None


def _stated_links(fronts: list[tuple[str, dict]], statements: list[dict], ids: set[str], edges: set) -> set:
    """``(type, source, target, via)`` of the links stated in frontmatter id keys and the register's statements,
    between two records, that ``edges`` does not hold with the same type; one row per (type, source, target)."""
    alias = {}
    for _, front in fronts:
        for key in ALIAS_KEYS:
            if isinstance(front.get(key), str):
                alias.setdefault(front[key].strip(), front["id"])
    lead = re.compile(r"\s*([A-Za-z][A-Za-z0-9]*(?:[-.][A-Za-z0-9]+)*)")  # "DEC-954 Q9c" names DEC-954
    found = {}

    def add(kind, source, target, via):
        if source in ids and target in ids and source != target and (kind, source, target) not in edges:
            key = (kind, source, target)
            found[key] = min(found.get(key, via), via)

    for _, front in fronts:
        for kind, keys in ((CITES, CITE_KEYS), (OF_TASK, TASK_KEYS)):
            for key in keys:
                for value in _ids(front.get(key)):
                    token = lead.match(value)
                    if token:
                        named = token.group(1)
                        add(kind, front["id"], named if named in ids else alias.get(named, ""), key)
    for statement in statements:
        kind = _link_type(statement)
        if kind:
            add(kind, statement["source"], statement["target"], statement["form"])
    return {(*key, via) for key, via in found.items()}


def _markdown(root: Path, tree: dict) -> list[tuple[str, str]]:
    """``(path, text)`` of every Markdown file of ``HEAD``."""
    blobs = [(path, sha) for path, (_, kind, sha) in tree.items() if path.endswith(".md") and kind == "blob"]
    out =_git(root, "cat-file", "--batch", stdin="".join(f"{sha}\n" for _, sha in blobs).encode())
    files, position = [], 0
    for path, _ in blobs:
        header_end = out.index(b"\n", position)
        size = int(out[position:header_end].split()[2])
        files.append((path, out[header_end + 1:header_end + 1 + size].decode("utf-8", "replace")))
        position = header_end + size + 2
    return files


def _frontmatter(text: str):
    """The frontmatter document of ``text``, None when it has none; ValueError when it cannot be read."""
    import yaml

    lines = [line.rstrip() for line in text.split("\n")]
    if lines[0] != "---":
        return None
    if "---" not in lines[1:]:
        raise ValueError("the frontmatter is not closed")
    try:
        return yaml.safe_load("\n".join(lines[1:lines.index("---", 1)]))
    except (yaml.YAMLError, ValueError) as exc:
        raise ValueError("the frontmatter is not valid YAML: " + " ".join(str(exc).split())) from None


def frontmatters(root: Path, but: frozenset[str] = frozenset()) -> list[tuple[str, object, str | None]]:
    """``(path, frontmatter, why it cannot be read)`` of every Markdown file of ``HEAD`` whose path is not in ``but``."""
    found = []
    for path, text in _markdown(root, {path: entry for path, entry in _tree(root).items() if path not in but}):
        try:
            found.append((path, _frontmatter(text), None))
        except ValueError as exc:
            found.append((path, None, str(exc)))
    return found


def _ids(value) -> list[str]:
    if value is None:
        return []
    return [str(item) for item in (value if isinstance(value, list) else [value])]


def _read_records(root: Path):
    """The records, edges, entries that are no records, register headings, frontmatter titles and stated links
    (``LINKS_TABLE``) of ``HEAD``."""
    records, edges, invalid, titles, fronts = [], set(), [], [], []
    tree = _tree(root)
    register = _register(root, tree)
    for path, text in _markdown(root, tree):
        try:
            front = _frontmatter(text)
        except ValueError as exc:
            invalid.append({"path": path, "reason": str(exc)})
            continue
        if not isinstance(front, dict) or "id" not in front:
            continue
        missing = [key for key in REQUIRED if not isinstance(front.get(key), str) or not front[key]]
        if missing:
            invalid.append({"path": path, "reason": f"required key missing or not a string: {', '.join(missing)}"})
            continue
        records.append((path, front["id"], front["type"], front["status"]))
        fronts.append((path, front))
        if isinstance(front.get("title"), str):
            titles.append((path, front["id"], front["title"]))
        for edge_type in EDGE_TYPES:
            edges.update((edge_type, front["id"], target) for target in _ids(front.get(edge_type.lower())))
        edges.update(("SUPERSEDES", successor, front["id"]) for successor in _ids(front.get("superseded_by")))
    headings, statements = [], []
    if register:
        of_files = {record_id: path for path, record_id, _, _ in reversed(records)}
        entries, supersedes, headings, no_records, statements = _read_register(*register, of_files)
        records += entries
        edges |= supersedes
        invalid += no_records
    links = _stated_links(fronts, statements, {record_id for _, record_id, _, _ in records}, edges)
    return records, edges, invalid, headings, titles, links


def _read_commits(root: Path):
    commits, trailers, paths = [], set(), set()
    log = _git(root, "-c", "core.quotePath=false", "log", "--name-only", _LOG_FORMAT, "HEAD")
    for entry in log.decode("utf-8", "replace").split("\x1e")[1:]:
        commit, date, final_block, message, names = entry.split("\x1f")
        commits.append((commit,))
        paths.update((commit, name) for name in names.split("\n") if name)
        for key, value in _TRAILER.findall(message if date < TRAILER_RULE_DATE else final_block):
            trailers.update((commit, key.capitalize(), item) for item in re.split(r"[,\s]+", value) if item)
    return commits, trailers, paths


def _digest(connection: sqlite3.Connection) -> str:
    """sha256 of the store's logical content: every row of every table of the graph, in sorted order."""
    content = [[table, sorted(connection.execute(f"SELECT * FROM {table}").fetchall())] for table in _DIGESTED]
    if not content[-1][1]:  # no register entry: the digest is the one of a store without that table
        del content[-1]
    return hashlib.sha256(json.dumps(content).encode("utf-8")).hexdigest()


def connect(root: Path) -> sqlite3.Connection:
    """The store at ``root``, read-only. ``STORE_MISSING`` when no load has built it."""
    path = Path(root) / STORE_REL
    if not path.is_file():
        raise GovError("STORE_MISSING", f"{STORE_REL}: no store at {root}; load it first", {"root": str(root)})
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)


def _load(root: Path, kind: str, records_fingerprint: bool = True) -> tuple[dict, dict | None]:
    """Write the record graph of ``HEAD`` and the fingerprints row of the load, in one transaction: the load's
    result and ``HEAD``'s fingerprints (None where they cannot be computed). Without ``records_fingerprint`` the
    row states none yet, so the store is not fresh until ``load_records`` writes it after the indexes."""
    from gov.close.fingerprint import of_commit

    head = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode("utf-8").strip()
    records, edges, invalid, headings, titles, links = _read_records(root)
    commits, trailers, paths = _read_commits(root)
    prints = of_commit(root, head)
    rows = {"records": records, "edges": edges, "commits": commits, "trailers": trailers, "commit_paths": paths,
            REGISTER_TABLE: headings, TITLES_TABLE: titles, LINKS_TABLE: links}  # by name, never by position
    (root / STORE_REL).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(root / STORE_REL, isolation_level=None)
    try:
        connection.execute("BEGIN")
        for table, columns in _TABLES.items():
            connection.execute(f"DROP TABLE IF EXISTS {table}")
            connection.execute(f"CREATE TABLE {table} ({columns})")
            for row in sorted(rows[table]):
                connection.execute(f"INSERT INTO {table} VALUES ({', '.join('?' * len(row))})", row)
        connection.execute(f"DROP TABLE IF EXISTS {FINGERPRINTS_TABLE}")
        connection.execute(f"CREATE TABLE {FINGERPRINTS_TABLE} ({_FINGERPRINTS})")
        connection.execute(f"INSERT INTO {FINGERPRINTS_TABLE} VALUES (?, ?, ?, ?)",
                           (head, prints["code"] if prints else None,
                            prints["records"] if prints and records_fingerprint else None, kind))
        connection.execute("COMMIT")
        return {"digest": _digest(connection), "invalid": sorted(invalid, key=lambda entry: entry["path"])}, prints
    finally:
        connection.close()


def load(root: Path) -> dict:
    """Build the store at ``root`` from its git repository, replacing what an earlier load left. The fingerprints
    row records ``HEAD``, its two fingerprints and the kind ``rebuild``."""
    return _load(Path(root), REBUILD)[0]


def fingerprints(connection: sqlite3.Connection) -> dict | None:
    """The store's fingerprints row (``head``, ``code``, ``records``, ``kind``); None where the store has no such
    table (a store built before W2-68), and a row of nothing where the table holds other than one row, which
    matches no head. ``sqlite3.Error`` where the store cannot be asked."""
    if connection.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
                          (FINGERPRINTS_TABLE,)).fetchone() is None:
        return None
    rows = connection.execute(f"SELECT head, code, records, kind FROM {FINGERPRINTS_TABLE}").fetchall()
    return dict(zip(("head", "code", "records", "kind"), rows[0] if len(rows) == 1 else (None,) * 4))


def load_records(root: Path) -> dict:
    """The incremental record load (W2-68): the record graph of ``HEAD`` again, the lexical index and the semantic
    vectors refreshed through their own refresh functions, the code index left as it is.

    It runs only where the store's row holds a code fingerprint equal to ``HEAD``'s; otherwise ``STORE_CODE_CHANGED``
    (a full rebuild is needed). It leaves the store digest a full load of ``HEAD`` leaves, and the row ``HEAD``, its
    fingerprints and the kind ``records``.
    """
    from gov.close.fingerprint import of_commit

    root = Path(root)
    head = _git(root, "rev-parse", "--verify", "HEAD^{commit}").decode("utf-8").strip()
    prints = of_commit(root, head)
    try:
        connection = connect(root)
    except GovError as e:
        if e.code != "STORE_MISSING":
            raise
        row = None
    else:
        try:
            row = fingerprints(connection)
        except sqlite3.Error as e:
            raise GovError("STORE_UNREADABLE", f"the record store {STORE_REL} cannot be read ({e}); run gov rebuild",
                           {"store": STORE_REL}) from None
        finally:
            connection.close()
    if prints is None or row is None or row["code"] is None or row["code"] != prints["code"]:
        why = ("HEAD's code fingerprint cannot be computed" if prints is None
               else "the store records no code fingerprint" if row is None or row["code"] is None
               else "the store was built on another code fingerprint")
        raise GovError("STORE_CODE_CHANGED", f"{why}: the records alone cannot be loaded; run gov rebuild",
                       {"head": head, "code_fingerprint": prints and prints["code"],
                        "store_code_fingerprint": row and row["code"]})
    result, prints = _load(root, RECORDS, records_fingerprint=False)
    if prints is None or prints["code"] != row["code"]:  # HEAD moved to other code during the load
        raise GovError("STORE_CODE_CHANGED", "HEAD's code changed during the load; run gov rebuild",
                       {"head": head, "store_code_fingerprint": row["code"]})
    stores = _refresh_indexes(root)
    connection = sqlite3.connect(root / STORE_REL, isolation_level=None)
    try:
        connection.execute(f"UPDATE {FINGERPRINTS_TABLE} SET records = ?", (prints["records"],))
    finally:
        connection.close()
    return {**result, "head": head, "code_fingerprint": prints["code"], "records_fingerprint": prints["records"],
            "kind": RECORDS, "stores": stores}


def _refresh_indexes(root: Path) -> dict:
    """The lexical index and the semantic vectors refreshed as ``gov rebuild`` refreshes them; the code index is
    left as it is."""
    from gov.config.loader import load_config

    if "path-map.yaml" not in load_config(root):
        return {"lexical": {"status": "not_refreshed", "reason": "no path map: nothing is classified as indexable"},
                "semantic": {"status": "not_refreshed", "reason": "no path map"},
                "codeintel": {"status": "left"}}
    from gov.retrieval import lexical, semantic

    try:
        stores = {"lexical": {"status": "refreshed", "indexed": lexical.refresh(root)["indexed"]}}
    except GovError:
        raise
    except Exception as exc:
        raise GovError("STORE_LOAD_FAILED", f"the lexical index could not be refreshed: {exc}",
                       {"store": "lexical", "error": str(exc)})
    try:
        report = semantic.refresh(root)
        stores["semantic"] = ({"status": "refreshed"} if report.get("available")
                              else {"status": "not_refreshed", "reason": report.get("reason", "unknown")})
    except Exception as exc:  # noqa: BLE001 - the vectors stay stale and the semantic facet says so itself
        stores["semantic"] = {"status": "not_refreshed", "reason": str(exc)}
    stores["codeintel"] = {"status": "left"}
    return stores


def digest(root: Path) -> str:
    """The digest of the store at ``root``."""
    connection = connect(root)
    try:
        return _digest(connection)
    finally:
        connection.close()
