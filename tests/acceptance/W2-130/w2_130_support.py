"""Support for the W2-130 acceptance cases: git helpers, the record's block reader, the register and ticket readers,
the clones that ``gov links`` runs on, and the independent trailer recount.

The cases are repository-state cases on the repository these tests sit in (never a planted one, never a store).
Everything here reads git history (``git show``, ``git diff``, ``git log``) or a clone made with ``git clone --shared``
in a temporary folder (so the tree under test is never written, not even the mark ``gov links`` leaves).
The oracles never import ``gov.links``: the register's status lines, the tickets' fields and the trailers are read
here from the text.
"""

from __future__ import annotations

import datetime
import functools
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

REGISTER = "docs/DECISION_REGISTER.md"
# EMERGENCY-2 11.3, DEC-1214 G4: the register the clean-up marked, archived whole; REGISTER keeps the decisions in force
OLD_REGISTER = "docs/archive/DECISION_REGISTER-2026-11-19.md"
ARCHIVE = "governance/project/orchestration/ARCHIVE-SUPERSEDED.md"
IN_FORCE = "governance/project/orchestration/DECISIONS-IN-FORCE.md"
IN_FORCE_AT_HEAD = "docs/emergency-2/archive/DECISIONS-IN-FORCE.md"  # archived as history (EMERGENCY-2 11.1)
SITTING = "governance/project/orchestration/packages/W2-130-SITTING.md"
RECONCILIATION = "governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md"
RECORD = "docs/research/W2-130-link-cleanup.md"
TICKET = ".tickets/DAEO-q8cl.md"

# The fixed facts of the interface (abbreviations are unique in this repository; ``full`` resolves them).
START = "232efc47d"  # the clean-up's starting head (e12f8a30c's parent)
FIRST = "e12f8a30c"  # batches a0, a1, a2 and b1
SECOND = "c4420040f"  # after the owner's sitting
SITTING_COMMIT = "2f9c80b1f"
DEC1098_COMMIT = "9546edd61"
W2_129_LANDING = "34eed411a"
W2_92_ADOPTION = "3679ca0ba"
AUDIT_HEADS = {FIRST: "2f9c80b1f", SECOND: "ce7f10eb8a2a"}
EIGHT = [("DEC-853", "DEC-884"), ("DEC-1050", "DEC-1057"), ("DEC-120", "DEC-173"), ("DEC-724", "DEC-860"),
         ("DEC-056", "DEC-017"), ("DEC-072", "DEC-064"), ("DEC-162", "DEC-156"), ("DEC-1053", "DEC-880")]
BLOCKS = ["commits", "ids-87", "census", "archive-13", "judged-wrong", "audits", "comparison", "patch-a0",
          "patch-a1", "patch-a2", "patch-b1", "patch-sources-2", "patch-marks-3", "trailer-residuals", "recount",
          "drift", "drift-run", "counts-before", "counts-after", "closed-missing", "no-record", "dec-1123-linked",
          "lessons", "left"]
LIVE_STATUSES = ("open", "in_progress")
LINK_FORMS = ("list_rows", "wbs", "dec-798")  # DEC-1123 (2)'s three forms (P-W2-130-4 (a))
BACKLOG_ROW = re.compile(r"^W[0-9]+-[A-Z][0-9]+$")  # W2-H021, W2-M406, W2-L047 ...

PFX = "- **Status:** "
DEC = re.compile(r"\bDEC-(\d+)(?!\d)")
HASH = re.compile(r"^[0-9a-f]{40}$")
MARKS_TAIL = re.compile(r"^(?: · (?:\*\*Changed by:\*\*|SUPERSEDED by) \S.*)+$")


# ------------------------------------------------------------------------------------------------------------- git


def _env() -> dict:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
                "GIT_AUTHOR_NAME": "W2-130 tests", "GIT_AUTHOR_EMAIL": "tests@example.invalid",
                "GIT_COMMITTER_NAME": "W2-130 tests", "GIT_COMMITTER_EMAIL": "tests@example.invalid"})
    return env


def git(*args: str, cwd: Path | None = None, ok: tuple = (0,)) -> str:
    done = subprocess.run(["git", *args], cwd=cwd or ROOT, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=_env(), check=False)
    if done.returncode not in ok:
        raise RuntimeError(f"git {' '.join(args)} failed ({done.returncode}): {done.stderr.strip()}")
    return done.stdout


@functools.lru_cache(maxsize=None)
def full(rev: str) -> str:
    return git("rev-parse", "--verify", f"{rev}^{{commit}}").strip()


def head() -> str:
    return full("HEAD")


def parent(commit: str) -> str:
    return full(f"{full(commit)}^")


def is_ancestor(old: str, new: str) -> bool:
    done = subprocess.run(["git", "merge-base", "--is-ancestor", full(old), full(new)], cwd=ROOT, env=_env(),
                          capture_output=True, check=False)
    return done.returncode == 0


@functools.lru_cache(maxsize=None)
def show(rev: str, path: str) -> str | None:
    """The file's text at ``rev``, or None when the path is not in that commit."""
    done = subprocess.run(["git", "show", f"{full(rev)}:{path}"], cwd=ROOT, env=_env(), capture_output=True,
                          check=False)
    return done.stdout.decode("utf-8", errors="replace") if done.returncode == 0 else None


@functools.lru_cache(maxsize=None)
def changed_files(commit: str) -> dict:
    """``{path: status letter}`` of ``commit`` against its first parent."""
    out = git("diff", "--name-status", "--no-renames", full(f"{full(commit)}^"), full(commit))
    return {line.split("\t", 1)[1]: line[0] for line in out.splitlines() if line}


def committer_date(commit: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(git("log", "-1", "--format=%cI", full(commit)).strip())


def parse_when(value) -> datetime.datetime | None:
    """An ISO 8601 date with a time and a zone, else None."""
    if isinstance(value, datetime.datetime):
        when = value
    else:
        try:
            when = datetime.datetime.fromisoformat(str(value).strip())
        except ValueError:
            return None
    return when if when.tzinfo is not None and "T" in str(value).replace(" ", "T") else None


# ---------------------------------------------------------------------------------------------------- the record

OPEN_FENCE = re.compile(r"^```[A-Za-z]* +w2-130:(\S+)[ \t]*$", re.M)
BLOCK = re.compile(r"^```(yaml|diff|python) w2-130:([A-Za-z0-9_-]+)[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)


class Record:
    """``docs/research/W2-130-link-cleanup.md`` as read from the working tree (the file the ticket delivers)."""

    def __init__(self, path: Path):
        self.path = path
        self.text = path.read_text(encoding="utf-8") if path.is_file() else None
        self.blocks = {}
        self.opens = []
        if self.text is not None:
            self.opens = OPEN_FENCE.findall(self.text)
            for lang, name, body in BLOCK.findall(self.text):
                self.blocks.setdefault(name, (lang, body))

    def need(self) -> None:
        if self.text is None:
            pytest.fail(f"{RECORD} does not exist")

    def block(self, name: str, lang: str | None = None) -> str:
        self.need()
        if name not in self.blocks:
            pytest.fail(f"{RECORD} has no block `w2-130:{name}`")
        found, body = self.blocks[name]
        if lang and found != lang:
            pytest.fail(f"block w2-130:{name} is a `{found}` block, the interface says `{lang}`")
        return body

    def data(self, name: str):
        body = self.block(name, "yaml")
        try:
            return yaml.safe_load(body)
        except yaml.YAMLError as error:
            pytest.fail(f"block w2-130:{name} is not valid YAML: {error}")

    def commits(self) -> dict:
        data = self.data("commits")
        if not isinstance(data, dict):
            pytest.fail("block w2-130:commits is not a mapping")
        return data

    def commit_list(self, key: str) -> list[str]:
        """Full hashes of ``commits.<key>``, each resolving to a commit; a single hash gives a list of one."""
        data = self.commits()
        if key not in data:
            pytest.fail(f"w2-130:commits has no `{key}`")
        raw = data[key]
        raw = raw if isinstance(raw, list) else [raw]
        out = []
        for item in raw:
            text = str(item)
            if not HASH.match(text):
                pytest.fail(f"commits.{key} holds {text!r}: not a full 40-hex commit hash")
            try:
                out.append(full(text))
            except RuntimeError:
                pytest.fail(f"commits.{key} holds {text}: no such commit in this repository")
        if not out:
            pytest.fail(f"commits.{key} is empty")
        return out


def pair(item) -> tuple[str, str]:
    """``(changed, changer)`` from ``{changed, changer}`` or ``DEC-a<-DEC-b``."""
    if isinstance(item, dict) and "changed" in item and "changer" in item:
        return str(item["changed"]), str(item["changer"])
    if isinstance(item, str) and "<-" in item:
        left, right = item.split("<-", 1)
        return left.strip(), right.strip()
    pytest.fail(f"cannot read a pair from {item!r} (use {{changed: DEC-a, changer: DEC-b}})")


def ids_in(text: str) -> list[str]:
    """Every ``DEC-n`` in ``text``, with the register's own spelling (zero padding kept)."""
    return ["DEC-" + n for n in DEC.findall(text)]


# --------------------------------------------------------------------------------------------- the register


def entries(text: str) -> list[tuple[str, int, str]]:
    """``[(id, 0-based line index, status line)]`` in file order: each ``### DEC-n`` heading's first status line."""
    out, current, waiting = [], None, False
    for index, line in enumerate(text.split("\n")):
        heading = re.match(r"### (DEC-\d+)\b", line)
        if heading:
            current, waiting = heading.group(1), True
        elif waiting and line.startswith(PFX):
            out.append((current, index, line))
            waiting = False
    return out


def mask_status(text: str) -> str:
    return re.sub(r"(?m)^- \*\*Status:\*\*.*$", "S", text)


def status_word(line: str) -> str:
    rest = line[len(PFX):] if line.startswith(PFX) else line
    return rest.split()[0] if rest.split() else ""


def has_done_tag(line: str) -> bool:
    return re.search(r" · done\b", line) is not None


def names_changer(line: str, changer: str) -> bool:
    """Whether a status line names ``changer`` as a change: in a ``**Changed by:**`` field or ``SUPERSEDED by``."""
    spans = []
    for found in re.finditer(r"\*\*Changed by:\*\*", line):
        end = line.find(" · **", found.end())
        spans.append(line[found.end(): len(line) if end < 0 else end])
    for found in re.finditer(r"SUPERSEDED by ((?:DEC-\d+)(?:, DEC-\d+)*)", line):
        spans.append(found.group(1))
    return any(changer in ids_in(span) for span in spans)


def classify(old: str, new: str) -> tuple[str, str]:
    """How the status line ``new`` follows ``old``: ``same``, ``append`` (marks only), ``status`` (a decided status
    word first, the old status text kept after ``; it was``, marks after it allowed) or ``other``. The second item is
    the appended marks (a tail starting `` · ``), or ``""``."""
    if old == new:
        return "same", ""
    if new.startswith(old) and MARKS_TAIL.match(new[len(old):]):
        return "append", new[len(old):]
    if old.startswith(PFX) and new.startswith(PFX):
        kept = "; it was " + old[len(PFX):]
        at = new.find(kept)
        if at > len(PFX):
            tail = new[at + len(kept):]
            if tail == "" or MARKS_TAIL.match(tail):
                return "status", tail
    return "other", ""


def register_delta(old_rev: str, new_rev: str, path: str = REGISTER) -> dict:
    """The register at two commits compared entry by entry: the ids, the masked text and each changed status line.
    ``path`` is the register's (``REGISTER``) or the archived old register's (``OLD_REGISTER``); a commit that does not
    hold the file (the archive before the register's move) compares as other ids, with no change."""
    old_text, new_text = show(old_rev, path), show(new_rev, path)
    if old_text is None or new_text is None:
        return {"same_ids": False, "masked_equal": False, "changes": []}
    old_entries, new_entries = entries(old_text), entries(new_text)
    result = {"same_ids": [e[0] for e in old_entries] == [e[0] for e in new_entries],
              "masked_equal": mask_status(old_text) == mask_status(new_text), "changes": []}
    if result["same_ids"]:
        for (entry, _, before), (_, _, after) in zip(old_entries, new_entries):
            if before != after:
                kind, tail = classify(before, after)
                result["changes"].append({"id": entry, "old": before, "new": after, "kind": kind, "tail": tail})
    return result


def added_marks(commit: str) -> list[dict]:
    """The marks ``commit`` appends to status lines: ``[{changed, changer, tail}]``, one per entry and changer."""
    out = []
    for change in register_delta(parent(commit), commit)["changes"]:
        if change["kind"] in ("append", "status") and change["tail"]:
            for changer in dict.fromkeys(ids_in(change["tail"])):
                out.append({"changed": change["id"], "changer": changer, "tail": change["tail"]})
    return out


# ---------------------------------------------------------------------------------------------------- tickets

FIELD = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):", re.M)


def split_ticket(text: str) -> tuple[list[str], dict, str]:
    """``(field order, {field: its raw lines}, body)`` of a ticket file."""
    assert text.startswith("---\n"), "a ticket file starts with ---"
    end = text.index("\n---\n", 3)
    front, body = text[4: end + 1], text[end + 5:]
    keys, fields, current = [], {}, None
    for line in front.splitlines(keepends=True):
        found = FIELD.match(line)
        if found:
            current = found.group(1)
            keys.append(current)
            fields[current] = line
        elif current is not None:
            fields[current] += line
    return keys, fields, body


def ticket_status(text: str) -> str:
    found = re.search(r"(?m)^status: *(\S+)", text.split("\n---\n", 1)[0])
    return found.group(1) if found else ""


def ticket_sources(text: str) -> list[str]:
    raw = split_ticket(text)[1].get("sources")
    if raw is None:
        return []
    loaded = yaml.safe_load(raw) or {}
    return [str(item) for item in (loaded.get("sources") or [])]


def ticket_kpis(text: str) -> dict:
    return (yaml.safe_load(split_ticket(text)[1]["kpis"]) or {}).get("kpis") or {}


def ticket_delta(old: str, new: str) -> dict:
    """What changed between two versions of one ticket file: the fields (other than the body), and the body."""
    old_keys, old_fields, old_body = split_ticket(old)
    new_keys, new_fields, new_body = split_ticket(new)
    changed = {key for key in set(old_fields) | set(new_fields) if old_fields.get(key) != new_fields.get(key)}
    return {"same_keys": old_keys == new_keys, "fields": changed, "body": old_body != new_body}


def ticket_changes(commit: str) -> dict:
    """``{path: (old text, new text)}`` for each ``.tickets/*.md`` the commit touches (None where absent)."""
    before = parent(commit)
    return {path: (show(before, path), show(commit, path)) for path in changed_files(commit)
            if path.startswith(".tickets/") and path.endswith(".md")}


def sources_added(commit: str) -> dict:
    """``{ticket path: [ids added to its sources:]}`` over the tickets the commit changes."""
    out = {}
    for path, (old, new) in ticket_changes(commit).items():
        if old is None or new is None:
            continue
        old_ids = ticket_sources(old)
        added = [item for item in ticket_sources(new) if item not in old_ids]
        if added:
            out[path] = added
    return out


def ticket_field(text: str, key: str):
    """The parsed value of one front-matter field of a ticket (None where the field is absent)."""
    raw = split_ticket(text)[1].get(key)
    return None if raw is None else (yaml.safe_load(raw) or {}).get(key)


def ticket_aliases(tree: Path) -> dict:
    """``{alias: {ticket ids}}``: each ticket's ``wbs_id`` (and ``external-ref``, the other key ``gov`` resolves a W2 id
    by) over the ticket files of ``tree``; a ticket's id is its file's stem."""
    out: dict = {}
    for path in sorted((tree / ".tickets").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for key in ("wbs_id", "external-ref"):
            value = ticket_field(text, key)
            if isinstance(value, str) and value.strip():
                out.setdefault(value.strip(), set()).add(path.stem)
    return out


def unlinked_on_live(findings: list[dict], tree: Path) -> dict:
    """``{ticket id: {ids}}`` of the UNLINKED_ID findings on tickets open or in progress in ``tree`` (the ticket is
    the finding's second id, the ids that ticket's KPI brackets or worker commits name come first)."""
    out: dict = {}
    for finding in findings:
        if finding["code"] == "UNLINKED_ID" and finding["path"].startswith(".tickets/"):
            text = (tree / finding["path"]).read_text(encoding="utf-8")
            if ticket_status(text) in LIVE_STATUSES:
                out.setdefault(finding["ids"][1], set()).add(finding["ids"][0])
    return out


def linked_form_problem(tree: Path, ticket: str, entry: dict, findings: list[dict]) -> str | None:
    """Why ``entry`` (``{id, form, via}`` of ``ticket``) is not of its DEC-1123 (2) form in ``tree``, else None.

    ``list_rows``: the id is a backlog row, held by the ticket's ``list_rows``, ``via`` the id as it stands there.
    ``wbs``: the id is a ticket's ``wbs_id`` (or ``external-ref``), ``via`` the id of a ticket that has it, and that
    ticket id is in the ticket's ``sources:``. ``dec-798``: the id is DEC-798, ``via`` is DEC-1033, in the ticket's
    ``sources:``, and ``gov links`` reports DEC-1033 as no NOT_IN_FORCE_AS_RULE (so it is live)."""
    text = (tree / ".tickets" / f"{ticket}.md").read_text(encoding="utf-8")
    ident, form, via = entry["id"], entry["form"], entry["via"]
    sources = ticket_sources(text)
    if form == "list_rows":
        rows = [str(row) for row in (ticket_field(text, "list_rows") or [])]
        if not BACKLOG_ROW.match(ident):
            return f"{ident} is no backlog row (W2-H.., W2-M.., W2-L..)"
        if ident not in rows:
            return f"{ident} is not in {ticket}'s list_rows {rows}"
        if via != ident:
            return f"via {via!r} is not the id as it stands in list_rows ({ident})"
    elif form == "wbs":
        owners = ticket_aliases(tree).get(ident, set())
        if not owners:
            return f"{ident} is no ticket's wbs_id"
        if via not in owners:
            return f"via {via} is no ticket with wbs_id {ident} (those are {sorted(owners)})"
        if via not in sources:
            return f"{via} is not in {ticket}'s sources:"
    elif form == "dec-798":
        if ident != "DEC-798" or via != "DEC-1033":
            return f"form dec-798 is DEC-798 via DEC-1033, not {ident} via {via}"
        if via not in sources:
            return f"DEC-1033 is not in {ticket}'s sources:"
        if any(f["code"] == "NOT_IN_FORCE_AS_RULE" and f["ids"][0] == "DEC-1033" for f in findings):
            return "DEC-1033 is not live (gov links reports it NOT_IN_FORCE_AS_RULE)"
    else:
        return f"form {form!r} is none of {list(LINK_FORMS)}"
    return None


# ------------------------------------------------------------------------------------------------- unified diffs

HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def patch_sections(patch: str) -> dict:
    """``{path: section text}`` of a ``git apply`` patch."""
    out = {}
    for section in re.split(r"(?m)^(?=diff --git )", patch):
        found = re.match(r"diff --git a/(\S+) b/", section)
        if found:
            out[found.group(1)] = section
    return out


def patch_line_changes(section: str) -> list[tuple[int, str, str]]:
    """``[(old line number, old text, new text)]`` for each removed line paired with the added line after it."""
    out, removed, added, old_no = [], [], [], 0

    def flush():
        for (number, text), new in zip(removed, added):
            out.append((number, text, new))
        removed.clear()
        added.clear()

    for line in section.split("\n"):
        hunk = HUNK.match(line)
        if hunk:
            flush()
            old_no = int(hunk.group(1))
        elif line.startswith("--- ") or line.startswith("+++ ") or line.startswith("diff "):
            continue
        elif line.startswith("-"):
            if added:
                flush()
            removed.append((old_no, line[1:]))
            old_no += 1
        elif line.startswith("+"):
            added.append(line[1:])
        else:
            flush()
            old_no += 1
    flush()
    return out


def patch_register_pairs(patch: str, base_rev: str) -> set[tuple[str, str]]:
    """The ``(changed, changer)`` pairs a patch appends to register status lines, the entry found from the old line
    number in the register at ``base_rev`` (the patches are append-only, so line numbers hold across batches). A
    patch with no hunk of the register (a0: ARCHIVE-SUPERSEDED's one-decision-per-line change) appends none; a patch
    that holds no diff of any file is no patch and fails."""
    sections = patch_sections(patch)
    if not sections:
        pytest.fail("a patch block holds no `diff --git` section")
    section = sections.get(REGISTER)
    if section is None:
        return set()
    by_line = {index + 1: entry for entry, index, _ in entries(show(base_rev, REGISTER))}
    out = set()
    for number, old, new in patch_line_changes(section):
        if number not in by_line:
            pytest.fail(f"a patch hunk changes register line {number}, which is no entry's status line at {base_rev}")
        tail = new[len(old):] if new.startswith(old) else ""
        for changer in ids_in(tail):
            out.add((by_line[number], changer))
    return out


def patch_source_ids(patch: str) -> dict:
    """``{ticket path: [ids added to sources:]}`` from a patch: ``+- ID`` lines of a block list, and the ids a
    changed flow-style ``sources: [...]`` line gains."""
    out = {}
    for path, section in patch_sections(patch).items():
        added = [line[3:].strip() for line in section.split("\n") if line.startswith("+- ")]
        for _, old, new in patch_line_changes(section):
            if old.startswith("sources:") and new.startswith("sources:"):
                before = (yaml.safe_load(old) or {}).get("sources") or []
                added += [str(item) for item in ((yaml.safe_load(new) or {}).get("sources") or []) if item not in before]
        out[path] = added
    return out


# ---------------------------------------------------------------------------------------------------- the sitting

ROW = re.compile(r"^\| (DEC-\d+) \| ")


def sitting_rows(text: str) -> list[dict]:
    """The sitting file's rows of groups A to F: ``{id, group, proposal, reason}`` (proposal without ``**``, the
    reason the row's Evidence column, verbatim)."""
    out, group = [], None
    for line in text.split("\n"):
        heading = re.match(r"## ([A-H])\. ", line)
        if heading:
            group = heading.group(1)
        elif group is not None and group in "ABCDEF" and ROW.match(line):
            cells = line.strip()[1:-1].split(" | ", 5)
            cells = [cell.strip() for cell in cells]
            if len(cells) == 6:
                out.append({"id": cells[0], "group": group, "proposal": cells[3].replace("**", ""),
                            "reason": cells[5].rstrip("|").strip()})
    return out


def reconciliation_rows(text: str) -> dict:
    """``{id: {group, proposal, reason, ruling}}`` from ``| id | group | proposal | reason | ruling |`` rows."""
    out = {}
    for line in text.split("\n"):
        if ROW.match(line):
            cells = [cell.strip() for cell in line.strip()[1:-1].split(" | ")]
            if len(cells) >= 5:
                out[cells[0]] = {"group": cells[1], "proposal": cells[2].replace("**", ""),
                                 "reason": " | ".join(cells[3:-1]), "ruling": cells[-1]}
    return out


# ----------------------------------------------------------------------------------------- the trailer recount


def own_recount(rev: str) -> list[dict]:
    """Every trailer value in ``git log <rev>`` that names no record, read by this module, not the record's script.

    ``Task:`` a value with no ``.tickets/<value>.md`` at ``rev`` (``decision-record`` is valid, DEC-861);
    ``Implements:`` a value some element of which resolves to no register entry, ticket, W2 id (a ticket's
    ``wbs_id`` or ``external-ref``) or capability. Elements are split on commas and white space as the census
    splits them. Each item: ``{trailer, value, tokens}`` (the value as written; its unresolved elements)."""
    sha = full(rev)
    log = git("log", "--format=%x1e%H%x1f%(trailers:key=Task,key=Implements,unfold)", sha)
    tickets = {Path(name).stem for name in git("ls-tree", "--name-only", sha, ".tickets/").split()}
    aliases = set(re.findall(r"(?m)^(?:wbs_id|external-ref): *(\S+)",
                             git("grep", "-h", "-E", "^(wbs_id|external-ref):", sha, "--", ".tickets", ok=(0, 1))))
    register = set(re.findall(r"(?m)^### (DEC-\d+)\b", show(sha, REGISTER) or ""))
    contract = show(sha, "docs/contract/contract.yaml") or ""
    capabilities = set(re.findall(r"\b(?:CAP-\d+(?:\.[a-z])?|MR-\d+)\b", contract))
    known = register | tickets | aliases | capabilities
    found: dict = {}
    for item in log.split("\x1e")[1:]:
        _, block = item.split("\x1f", 1)
        for line in block.splitlines():
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            tokens = [token for token in re.split(r"[,\s]+", value) if token]
            if key == "Task":
                bad = [token for token in tokens if token != "decision-record" and token not in tickets]
            elif key == "Implements":
                bad = [token for token in tokens if token not in known]
            else:
                continue
            if bad:
                found.setdefault((key, value), bad)
    return [{"trailer": key, "value": value, "tokens": bad} for (key, value), bad in sorted(found.items())]


# --------------------------------------------------------------------------------------------------- gov links


def src_dir() -> Path:
    first = os.environ.get("PYTHONPATH", "").split(os.pathsep)[0]
    return Path(first).resolve() if first else ROOT / "src"


def child_env(home: Path, src: Path | None = None) -> dict:
    """The environment of a ``gov links`` run: ``src`` is the tool's source folder; None is the test run's own (the
    branch's ``src``), a clone's ``<clone>/src`` runs the tool of the tree under test (``pinned_src``)."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"HOME": str(home), "PYTHONPATH": str(src if src is not None else src_dir()), "PYTHONDONTWRITEBYTECODE": "1",
                "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    return env


def pinned_src(tree: Path) -> Path:
    """The ``src`` of a clone: the ``gov links`` the tree itself holds. A case pinned to a commit runs this tool, so a
    later change to ``gov links`` on the branch cannot move a pinned count (DEC-1156 (7), DEC-1164 (18))."""
    src = tree / "src"
    assert (src / "gov" / "links.py").is_file() or (src / "gov" / "links").is_dir(), f"{tree} holds no gov links source under src/"
    return src


def run_links(tree: Path, home: Path, *flags: str, src: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "gov.cli.main", "links", *flags, "--root", str(tree)], cwd=tree,
                          capture_output=True, text=True, env=child_env(home, src), check=False, timeout=900)


def links_json(tree: Path, home: Path, src: Path | None = None) -> list[dict]:
    """The findings of ``gov links --all --json`` on ``tree`` (exit 0 or 1 both mean it ran). ``src`` None runs the
    branch's tool; ``pinned_src(tree)`` runs the tree's own."""
    done = run_links(tree, home, "--all", "--json", src=src)
    try:
        return json.loads(done.stdout)["result"]["findings"]
    except (ValueError, KeyError, TypeError):
        pytest.fail(f"gov links --all --json gave no result (exit {done.returncode}): {done.stderr.strip()[-400:]}")


def measured_at(record: "Record") -> str:
    """``counts-after.measured_at``: the tree the record says it counted. Pinned, not HEAD: a ticket closed or reopened
    after the land moves what ``gov links`` finds at HEAD (122 -> 124 CLOSED_TICKET_EDITED in five hours), and the
    record's counts must not turn red for it (DEC-1156 (7), DEC-1164 (18)). The tree is one this branch really holds:
    a full hash, ``counts-after.head`` (the last clean-up commit) or a descendant of it, and an ancestor of HEAD."""
    after = record.data("counts-after")
    if not isinstance(after, dict) or "head" not in after:
        pytest.fail("counts-after lacks head")
    if "measured_at" not in after:
        pytest.fail("counts-after lacks measured_at, the tree the counts were taken at")
    measured = need_hash(after["measured_at"], "counts-after.measured_at")
    last_cleanup = need_hash(after["head"], "counts-after.head")
    assert is_ancestor(last_cleanup, measured), "counts-after.measured_at is not counts-after.head or a descendant of it"
    assert is_ancestor(measured, head()), "counts-after.measured_at is not an ancestor of HEAD"
    return measured


def make_clone(dest: Path, rev: str) -> Path:
    git("clone", "-q", "-s", "-n", str(ROOT), str(dest))
    git("checkout", "-q", "--detach", full(rev), cwd=dest)
    return dest


def variant_register(commit: str) -> str:
    """The register of ``commit`` with the marks it appends taken off again: each appended tail dropped, a decided
    status kept. Judged by ``gov links``, it shows which pairs the marks were written for."""
    text = show(commit, REGISTER)
    lines = text.split("\n")
    by_id = {entry: index for entry, index, _ in entries(text)}
    for change in register_delta(parent(commit), commit)["changes"]:
        if change["kind"] in ("append", "status") and change["tail"]:
            lines[by_id[change["id"]]] = change["new"][: len(change["new"]) - len(change["tail"])]
    return "\n".join(lines)


def whole_register(tree: Path) -> str | None:
    """The register whole, as the clean-up marked it, where ``tree`` has archived it (EMERGENCY-2 11.3, DEC-1214 G4):
    the archive's text under its first line, each entry's status line the kept register's own where the register still
    holds the entry (a mark added after the move is added there), and the entries only the register holds (the
    decisions since) after it. None where ``tree`` holds no archive: its register is whole."""
    archive = tree / OLD_REGISTER
    if not archive.is_file():
        return None
    lines = archive.read_text(encoding="utf-8").split("\n")[1:]
    kept_text = (tree / REGISTER).read_text(encoding="utf-8")
    kept = {entry: line for entry, _, line in entries(kept_text)}
    for entry, index, _ in entries("\n".join(lines)):
        if entry in kept:
            lines[index] = kept[entry]
    held = set(re.findall(r"(?m)^### (DEC-\d+)\b", "\n".join(lines)))
    later = [chunk for chunk in re.split(r"(?m)^(?=### DEC-\d+\b)", kept_text)[1:]
             if re.match(r"### (DEC-\d+)\b", chunk).group(1) not in held]
    return "\n".join(lines) + ("\n\n" + "".join(later) if later else "")


def commit_all(tree: Path, message: str) -> None:
    git("add", "-A", cwd=tree)
    git("commit", "-q", "-m", message, cwd=tree)


def owner_decided(line: str) -> bool:
    """Whether a status line records the owner's decision: ``ACCEPTED (owner`` or a ``Decided-by: owner`` trailer."""
    rest = line[len(PFX):] if line.startswith(PFX) else line
    return rest.startswith("ACCEPTED (owner") or re.search(r"Decided-by: owner\b", line) is not None


def not_owner_marked(pairs, register_text: str) -> list[tuple[str, str]]:
    """The ``(changed, changer)`` pairs whose changer is not recorded as the owner's decision in ``register_text``.

    A pair whose later decision (the changer) is the owner's is a marked change by rule: the owner approved the
    change when he decided. A changer the register does not hold counts as not the owner's."""
    lines = {entry: line for entry, _, line in entries(register_text)}
    return sorted(pair_ for pair_ in pairs if not owner_decided(lines.get(pair_[1], "")))


CLASS_SEGMENT = " \u00b7 **Class:**"


def outside_marks_problem(old: str, new: str, census_ids) -> str | None:
    """Why a status-line change made outside a marks commit is refused, or ``None`` when it is allowed.

    It must keep the old line whole (an append) and its appended tail must name none of ``census_ids`` (the census
    changers of that entry). The ids inside the appended `` \u00b7 **Class:** ...`` segment (from that text to the end of
    the line, the form ``docs/emergency-2/audits/08-apply.py`` writes) are audit 8's classification of the entry
    (DEC-1214 G4), not a clean-up mark, and do not count."""
    if not new.startswith(old):
        return "edited outside a marks commit, not an append"
    tail = new[len(old):]
    cut = tail.find(CLASS_SEGMENT)
    if cut != -1:
        tail = tail[:cut]
    if set(ids_in(tail)) & set(census_ids):
        return "a census pair marked outside a marks commit"
    return None


def by_pair(findings: list[dict], code: str = "UNMARKED_CHANGE") -> dict:
    return {(f["ids"][0], f["ids"][1]): f for f in findings if f["code"] == code}


# ------------------------------------------------------------------------------------------- the record's audits


def need_hash(value, what: str) -> str:
    text = str(value)
    if not HASH.match(text):
        pytest.fail(f"{what}: {text!r} is not a full 40-hex commit hash")
    try:
        return full(text)
    except RuntimeError:
        pytest.fail(f"{what}: {text} is no commit of this repository")


def audits_by_commit(record: Record) -> dict:
    """``{full commit hash: audits item}``; a commit twice, or an item with no commit, fails."""
    data = record.data("audits")
    if not isinstance(data, list) or not data:
        pytest.fail("w2-130:audits is not a non-empty list")
    out = {}
    for item in data:
        if not isinstance(item, dict) or "commit" not in item:
            pytest.fail(f"an audits item has no `commit`: {item!r}")
        sha = need_hash(item["commit"], "audits.commit")
        if sha in out:
            pytest.fail(f"audits holds two items for {sha}")
        out[sha] = item
    return out


def audit_marks(item: dict, key: str) -> list[dict]:
    marks = item.get(key)
    if not isinstance(marks, list):
        pytest.fail(f"audits item for {item.get('commit')} has no list `{key}`")
    for mark in marks:
        if not isinstance(mark, dict) or not {"changed", "changer", "mark", "verdict", "fate"} <= set(mark):
            pytest.fail(f"an audited mark lacks changed, changer, mark, verdict or fate: {mark!r}")
    return marks


def marks_commits(record: Record) -> list[str]:
    return record.commit_list("marks")


def committed_pairs(commit: str) -> set[tuple[str, str]]:
    return {(m["changed"], m["changer"]) for m in added_marks(commit)}
