"""The standing retrieval measure: an evaluation set's questions asked of ``gov retrieve``, scored (W2-61; DEC-828
items 3 and 4, DEC-833, DEC-860, DEC-820 (d)).

``python3 -m gov.retrieval.measure <set> [--root <dir>] [--sets-root <dir>] [--part visible|hidden|all]
[--gov <executable> | --kept <dir>] [--batch-size 10] [--bundle-budget 6000] [--stack-budget 24000] [--json]
[--out <dir>] [--compare <record>]...``

The set is one the ``evaluation_sets`` block of the sets root's path map declares; its questions are
``<sets-root>/fixtures/evaluation/<set>/<part>/*.yaml``, taken in file-name order. The hidden folder must be covered
by the set's ``hidden`` globs, and a session the set measures (its ``GOV_ROLE`` or ``GOV_TICKET``) is refused the
hidden part before any hidden file is opened.

**The question form** (one YAML file per question, the same for both halves): ``question`` (the text passed to
``gov retrieve``), ``gold_answer`` (the answer as the governing source states it) and ``sources``, all required.
Each ``sources`` entry is one piece of evidence the answer needs: a map with ``path`` and optionally ``heading``
and/or ``lines: [first, last]`` and ``commit``; or a list of such maps, alternatives of which any one counts.
Optional: ``id`` (default: the file name without ``.yaml``), ``category``, ``commit``, ``ticket`` (``--ticket``),
``ids`` (each ``--id``) and ``radius`` (``--radius``). Other fields are ignored and never printed.

**How a source is matched:** an evidence item matches a source when its ``path`` equals the source's and its lines
(``start_line`` to ``end_line``) overlap the source's span. A path alone is the whole file. A ``heading`` is the
full text of one line of the file (Markdown with its ``#`` marks, code the whole line), found in the measured root
as the first line equal to it with trailing whitespace removed; found, it governs over ``lines``: a ``#`` heading
spans to the line before the next heading of the same or a higher level (or the end of the file), any other
heading as many lines as ``lines`` state (its own line without them). Not found, ``lines`` are used; with neither,
the question is malformed. An item from the set's own parts or ``fixtures/evaluation/`` is never a hit.

**Re-anchoring, in memory** (W2-134 S1 to S3; DEC-1084, DEC-1085 (2)): a source scored by its ``lines`` (no heading
found) that names a ``commit``, its own or else the question's, is found again in the measured root: its block is
those lines of the file at that commit (read with ``git show``), and the source is scored against the lines where the
block stands now, the same lines when unmoved, else its one place elsewhere. A block that cannot be read, or is found
nowhere or more than once, is unresolved: named by question id and ``entry <n>`` (``<n>.<m>`` for an alternative) and
counted as not found (on standard output, or standard error with ``--json``). A source with no commit keeps its stated
lines. The measure never writes the sets root or a question file.

**Source families** (S7; DEC-1078 (4), DEC-1079): the path map's top-level ``evaluation_families`` (the sets root's,
else the measured root's) maps a family's name to the list of its member path globs: a gold source and its official
copies. An evidence item in another member of a gold source's family is a hit on that source only when its own text
holds the gold span's text, both normalised (whitespace; Markdown and YAML formatting: ``#`` heading marks, list
marks, ``>`` quote marks, quotes, backticks, ``*`` emphasis and ``key:`` prefixes, but never an id such as
``DEC-1078:``); never by its path alone. The gold's normalised text must be at least 4 words and 24 characters
(below that it counts only in its own path) and is held only on token edges (``CAP-1`` is not held by ``CAP-10``, nor
``85`` by ``1985``) (W2-134 S5). A question's line names each such item ("family hit: <path>"; for the hidden part
only their count). The text output's first line names the families in force, ``families: <name> (<n> members), …``
or ``families: none`` (S6). With no family declared, every figure and question line is as before.

**Re-scoring kept outputs:** ``--kept <dir>`` reads each call's ranked output from ``<dir>`` (``00001.json`` … in call
order, as the measure's ``GOV_KEEP`` wrapper keeps them) in place of running a retriever; the same set, parts and
budgets as the kept run give the same calls. A kept output missing, or one left over, refuses the run.

**The figures**, always together (DEC-833 item 3): hit@5, a source matched by one of the first five items of the
stacked context (in the bundle: by an item of the first call), against CAP-10's floor of 85; full evidence, every
entry matched by the stacked context across batches, against the owner's target of 99 %. The stacked context is
the calls' items in order, each taken once, within the stack budget (an item's size: its text's length / 4,
rounded up); a call continues the last while it returned a continuation and the stack budget is not reached
(DEC-860). For the hidden part, only ids, counts, ranks, digests and pass or fail are shown or written.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

from gov.guard.reads import PATH_MAP_REL, SETS_KEY, PolicyError, _Part, _ticket, evaluation_sets, set_fault

EVALUATION = "fixtures/evaluation"
FAMILIES_KEY = "evaluation_families"
FLOOR, TARGET = 85, 99
TOKEN_CHARS = 4
FIGURES = ("hit_at_5", "in_bundle", "full_evidence", "first_gold_rank", "stacked_digest")
_HEADING = re.compile(r"(#{1,6})\s")
_KEPT = re.compile(r"\d+\.json")
# the formatting a copy may differ by: escapes before quotes, quote and emphasis characters, then leading marks
# (``>`` quotes, ``#`` headings, list marks) and a YAML ``key:`` prefix, each line; whitespace collapsed after
_ESCAPED = re.compile(r"\\([\"'])")
_DROPPED = re.compile(r"[\"'`*]")
_MARKS = re.compile(r"^(?:\s*(?:>(?=\s|$)|#{1,6}(?=\s|$)|[-+](?=\s)|\d+[.)](?=\s)))+\s*")
# a key, but never an id (``DEC-1078:``, ``CAP-10.a:``), so two ids' lines never normalise alike (S5)
_KEY = re.compile(r"^(?![A-Za-z]+-\d)[A-Za-z_][\w.-]*:(?:\s+|$)")
_BLOCK = {"|", ">", "|-", ">-", "|+", ">+"}
# a family hit's floor and its token edges: no hit inside a longer token (``CAP-10``, ``1985``, ``0.85``) (S5)
FAMILY_WORDS, FAMILY_CHARS = 4, 24
_EDGE_BEFORE, _EDGE_AFTER = r"(?<![\w-])(?<!\w[.,])", r"(?![\w-])(?![.,]\w)"


class MeasureError(Exception):
    """A refusal or a fault that ends the run; its text names a hidden question by its id only."""


def _normal(text: str) -> str:
    """The text with whitespace and Markdown or YAML formatting normalised away (S7)."""
    out = []
    for line in text.splitlines():
        line = _DROPPED.sub("", _ESCAPED.sub(r"\1", line))
        line = _KEY.sub("", _MARKS.sub("", line).strip()).strip()
        if line and line not in _BLOCK:
            out.append(line)
    return " ".join(" ".join(out).split())


def _families_in(root: Path) -> dict | None:
    """One path map's ``evaluation_families``: ``None`` when it declares none; a fault when malformed."""
    path = root / PATH_MAP_REL
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError):
        raise MeasureError(f"{PATH_MAP_REL} cannot be read") from None
    if FAMILIES_KEY not in text:
        return None
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        raise MeasureError(f"{PATH_MAP_REL} cannot be read") from None
    if not isinstance(data, dict) or data.get(FAMILIES_KEY) is None:
        return None
    block = data[FAMILIES_KEY]
    if not (isinstance(block, dict) and all(
            isinstance(name, str) and isinstance(globs, list) and globs and all(
                isinstance(g, str) and g and not g.startswith("/") and ".." not in g.split("/") for g in globs)
            for name, globs in block.items())):
        raise MeasureError(f"{PATH_MAP_REL}: {FAMILIES_KEY} is not a map of names to lists of path globs")
    return block


def families(sets_root: Path, root: Path) -> list[_Part]:
    """The declared source families, each a part matched against ``/f/<path>``: the sets root's, else the root's."""
    for where in dict.fromkeys([sets_root, root]):
        block = _families_in(where)
        if block is not None:
            return [_Part("/f", globs, name) for name, globs in block.items()]
    return []


def _fault(part: str, qid: str, kind: str, detail: str = "") -> MeasureError:
    return MeasureError(f"{part} question {qid}: {kind}" + (f": {detail}" if detail and part != "hidden" else ""))


def _measured(entry: dict, sets_root: Path) -> bool:
    measures = entry["measures"]
    if os.environ.get("GOV_ROLE", "") in measures.get("roles", []):
        return True
    tickets, ticket = measures.get("tickets", []), os.environ.get("GOV_TICKET")
    return bool(tickets and ticket) and not _ticket(str(sets_root), ticket)[0].isdisjoint(tickets)


def _lines_at(root: Path, commit: str, path: str, cache: dict) -> list[str] | None:
    """A file's lines at a commit, read with git once per run (S1); ``None`` when git cannot show them. Only read:
    nothing is written (S2)."""
    if (commit, path) not in cache:
        lines = None
        if not commit.startswith("-"):  # never an option to git
            done = subprocess.run(["git", "-C", str(root), "show", f"{commit}:./{path}"], capture_output=True)
            lines = done.stdout.decode("utf-8", "replace").splitlines() if done.returncode == 0 else None
        cache[(commit, path)] = lines
    return cache[(commit, path)]


def _anchored(stated: list, now: list[str], old: list[str] | None) -> tuple[int, int] | None:
    """The stated block's lines in the measured root: the same lines when unmoved, else its one place elsewhere;
    ``None`` when it cannot be read or is found nowhere or more than once (as ``repin_gold.py`` finds it)."""
    first, last = stated
    if old is None or last > len(old):
        return None
    block = old[first - 1:last]
    if now[first - 1:last] == block:
        return first, last
    size = len(block)
    found = [i + 1 for i in range(len(now) - size + 1) if now[i:i + size] == block]
    return (found[0], found[0] + size - 1) if len(found) == 1 else None


def _span(source: dict, root: Path, part: str, qid: str, base=None, cache: dict | None = None
          ) -> tuple[int, int] | None:
    """A source's span in the measured root; ``None`` when its line-cited block is unresolved (S1, S3). ``base`` is
    the question's commit, used when the source names none."""
    stated = source.get("lines")
    if stated is not None and not (isinstance(stated, list) and len(stated) == 2
                                   and all(isinstance(n, int) for n in stated) and 1 <= stated[0] <= stated[1]):
        raise _fault(part, qid, "malformed question", "lines is not [first, last]")
    commit = next((str(c) for c in (source.get("commit"), base) if c is not None and str(c).strip()), "").strip()
    file = root / source["path"]
    if not file.is_file():
        if stated and commit:  # a line-cited block whose file is gone is not found at the measured root
            return None
        raise _fault(part, qid, "a source's path does not exist in the measured root", source["path"])
    lines = file.read_text(encoding="utf-8", errors="replace").splitlines()

    def by_lines() -> tuple[int, int] | None:
        if not commit:
            return tuple(stated)
        return _anchored(stated, lines, _lines_at(root, commit, source["path"], {} if cache is None else cache))

    heading = source.get("heading")
    if heading is None:
        return by_lines() if stated else (1, max(len(lines), 1))
    at = next((i for i, line in enumerate(lines) if line.rstrip() == str(heading).rstrip()), None)
    if at is None:
        if not stated:
            raise _fault(part, qid, "malformed question", "a heading is not found and no lines are stated")
        return by_lines()
    mark = _HEADING.match(lines[at])
    if not mark:
        return at + 1, at + (stated[1] - stated[0] + 1 if stated else 1)
    level = len(mark.group(1))
    end = next((j for j in range(at + 1, len(lines))
                if (m := _HEADING.match(lines[j])) and len(m.group(1)) <= level), len(lines))
    return at + 1, end


def _alternative(a: dict, root: Path, part: str, qid: str, declared: list[_Part], base=None,
                 cache: dict | None = None) -> tuple | None:
    """One source alternative: its path and span, and, when it is in a family, those families and the span's
    normalised text (empty below the floor, and an empty text never makes a family hit); ``None`` when unresolved."""
    span = _span(a, root, part, qid, base, cache)
    if span is None:
        return None
    first, last = span
    own = tuple(f for f in declared if f.match(a["path"]))
    text = ""
    if own:
        lines = (root / a["path"]).read_text(encoding="utf-8", errors="replace").splitlines()
        text = _normal("\n".join(lines[first - 1:last]))
        if len(text.split()) < FAMILY_WORDS or len(text) < FAMILY_CHARS:
            text = ""
    return a["path"], first, last, own, text


def _load(file: Path, part: str, root: Path, quoting: _Part, declared: list[_Part] = (),
          cache: dict | None = None) -> dict:
    qid = file.stem
    try:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        raise _fault(part, qid, "malformed question", "not YAML") from None
    if not isinstance(data, dict):
        raise _fault(part, qid, "malformed question", "not a map")
    qid = str(data.get("id", qid))
    sources = data.get("sources")
    if not (isinstance(data.get("question"), str) and data["question"].strip() and data.get("gold_answer")
            and isinstance(sources, list) and sources):
        raise _fault(part, qid, "malformed question", "question, gold_answer and sources are required")
    entries, unresolved, cache = [], [], {} if cache is None else cache
    for n, entry in enumerate(sources, 1):
        alternatives = entry if isinstance(entry, list) else [entry]
        if not alternatives or not all(isinstance(a, dict) and isinstance(a.get("path"), str) and a["path"]
                                       for a in alternatives):
            raise _fault(part, qid, "malformed question", "a source names no path")
        kept = []
        for m, a in enumerate(alternatives, 1):
            # an alternative in the set's own parts or the evaluation files never counts and is never opened
            if quoting.inside(f"/q/{a['path']}"):
                continue
            alt = _alternative(a, root, part, qid, list(declared), data.get("commit"), cache)
            if alt is None:  # named by its entry number only, never its text, path or lines (S3)
                unresolved.append(f"entry {n}.{m}" if isinstance(entry, list) else f"entry {n}")
            else:
                kept.append(alt)
        entries.append(kept)
    return {"id": qid, "part": part, "question": data["question"], "sources": entries, "ticket": data.get("ticket"),
            "ids": data.get("ids") or [], "radius": data.get("radius"), "families": bool(declared),
            "unresolved": unresolved}


def _retriever(gov: str, root: Path, env: dict) -> dict:
    found = shutil.which(gov, path=os.environ.get("PATH"))
    if not found:
        raise MeasureError(f"no gov executable: {gov}")
    exe = str(Path(found).resolve())
    done = subprocess.run([exe, "--version"], cwd=root, env=env, capture_output=True, text=True)
    version = (done.stdout.splitlines() or [None])[0] if done.returncode == 0 else None
    gov_file = None
    with open(exe, "rb") as handle:
        first = handle.readline().decode("utf-8", "replace").strip()
    if first.startswith("#!"):
        probe = "import sys; sys.path.pop(0); import gov; print(gov.__file__)"
        done = subprocess.run([*first[2:].split(), "-c", probe], cwd=root, env=env, capture_output=True, text=True)
        gov_file = done.stdout.strip() or None if done.returncode == 0 else None
    return {"executable": exe, "version": version, "gov_file": gov_file}


class _Kept:
    """The kept ranked outputs of a run, read in call order in place of a retriever (``--kept``)."""

    def __init__(self, folder: str):
        self.folder = Path(folder)
        if not self.folder.is_dir():
            raise MeasureError(f"the kept outputs' folder does not exist: {folder}")
        self.files = sorted((f for f in self.folder.iterdir() if _KEPT.fullmatch(f.name) and f.is_file()),
                            key=lambda f: int(f.stem))
        self.used = 0

    def __call__(self, q: dict, words: list[str]) -> tuple[int, str]:
        if self.used >= len(self.files):
            raise _fault(q["part"], q["id"], "the kept outputs end before the run's calls",
                         f"{len(self.files)} kept")
        file = self.files[self.used]
        self.used += 1
        try:
            return 0, file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return 1, ""

    def done(self) -> None:
        if self.used != len(self.files):
            raise MeasureError(f"the kept outputs do not match the run: {len(self.files)} kept, {self.used} calls")


def _runner(exe: str, root: Path, env: dict):
    def call(q: dict, words: list[str]) -> tuple[int, str]:
        done = subprocess.run([exe, "retrieve", *words], cwd=root, env=env, capture_output=True, text=True)
        return done.returncode, done.stdout
    return call


def _match(item: tuple, entry: list[tuple]) -> str | None:
    """``direct`` when the item lies in an alternative's span, ``family`` when it lies in another member of an
    alternative's family and its normalised text holds the span's normalised text on token edges, else ``None``."""
    if any(item[0] == path and item[1] <= last and first <= item[2] for path, first, last, *_ in entry):
        return "direct"
    held = None
    for path, _, _, own, text in entry:
        if text and item[0] != path and any(f.match(item[0]) for f in own):
            held = _normal(item[3]) if held is None else held
            if re.search(_EDGE_BEFORE + re.escape(text) + _EDGE_AFTER, held):
                return "family"
    return None


def _ask(q: dict, args, call, quoting: _Part) -> dict:
    options = [*(["--ticket", str(q["ticket"])] if q["ticket"] else []),
               *[w for i in q["ids"] for w in ("--id", str(i))],
               *(["--radius", str(q["radius"])] if q["radius"] is not None else []),
               "--batch-size", str(args.batch_size), "--bundle-budget", str(args.bundle_budget)]
    stacked, seen, used, first, token, calls = [], set(), 0, None, None, 0
    while True:
        code, stdout = call(q, [*options, *(["--continue", token] if token else []), q["question"], "--json"])
        calls += 1
        try:
            doc = json.loads(stdout)
            bundle = doc["result"] if isinstance(doc.get("result"), dict) else doc
            items = [(i["path"], int(i["start_line"]), int(i["end_line"]), str(i.get("text", "")))
                     for i in bundle["evidence"]]
        except (ValueError, KeyError, TypeError, AttributeError):
            items = None
        if code != 0 or items is None or doc.get("ok") is False:
            raise _fault(q["part"], q["id"], "the retrieval failed", f"exit {code}")
        first = items if first is None else first
        full = False
        for item in items:
            if item[:3] in seen:
                continue
            size = -(-len(item[3]) // TOKEN_CHARS)
            if used + size > args.stack_budget:
                full = True
                break
            seen.add(item[:3])
            stacked.append(item)
            used += size
        token = bundle.get("continuation")
        if full or not token or used >= args.stack_budget:
            break

    matched: dict[tuple, list] = {}

    def kinds(item) -> list:
        if item[:3] not in matched:
            matched[item[:3]] = ([None] * len(q["sources"]) if quoting.inside(f"/q/{item[0]}")
                                 else [_match(item, e) for e in q["sources"]])
        return matched[item[:3]]

    def hits(item, n):
        return kinds(item)[n] is not None

    pieces = range(len(q["sources"]))
    rank = next((n for n, item in enumerate(stacked, 1) if any(hits(item, e) for e in pieces)), None)
    found = sum(any(hits(item, e) for item in stacked) for e in pieces)
    digest = hashlib.sha256(json.dumps([list(i[:3]) for i in stacked]).encode()).hexdigest()[:16]
    scored = {"id": q["id"], "part": q["part"], "hit_at_5": rank is not None and rank <= 5,
              "in_bundle": any(hits(item, e) for item in first for e in pieces),
              "full_evidence": found == len(q["sources"]), "first_gold_rank": rank, "pieces_found": found,
              "pieces_needed": len(q["sources"]), "calls": calls, "stacked_digest": digest}
    if q.get("families"):
        # each stacked or first-call item that is a hit by its family only, in order, once
        named = list(dict.fromkeys(item[0] for item in [*stacked, *first] if "family" in kinds(item)))
        scored["family_hit_count"] = len(named)
        if q["part"] != "hidden":
            scored["family_hits"] = named
    if q.get("unresolved"):
        scored["unresolved"] = list(q["unresolved"])
    return scored


def _total(questions: list[dict]) -> dict:
    n = len(questions)

    def share(key, line, name):
        count = sum(q[key] for q in questions)
        return {"count": count, "of": n, "percent": round(100 * count / n, 1) if n else 0.0, name: line}
    return {"questions": n, "hit_at_5": share("hit_at_5", FLOOR, "floor"),
            "full_evidence": share("full_evidence", TARGET, "target")}


def _compare(questions: list[dict], records: list[str]) -> None:
    for record in records:
        try:
            earlier = {(q.get("part"), q["id"]): q for q in json.loads(Path(record).read_text())["questions"]}
        except (OSError, ValueError, KeyError, TypeError):
            raise MeasureError(f"the record to compare cannot be read: {record}") from None
        for q in questions:
            old = earlier.get((q["part"], q["id"]), {})
            differs = [name for name in FIGURES if old.get(name, object()) != q[name]]
            q.setdefault("compare", []).append({"same": not differs, "differs": differs})


def _line(q: dict) -> str:
    def yes(v):
        return "yes" if v else "no"
    line = (f"{q['id']} ({q['part']}): hit@5 {yes(q['hit_at_5'])} (first gold rank {q['first_gold_rank'] or '-'}), "
            f"in the bundle {yes(q['in_bundle'])}; full evidence {yes(q['full_evidence'])} "
            f"({q['pieces_found']} of {q['pieces_needed']} pieces); {q['calls']} calls")
    if q.get("family_hits"):
        line += f"; family hit: {', '.join(q['family_hits'])}"
    elif q.get("family_hit_count"):  # the hidden part: the count only, never a path
        line += f"; family hits: {q['family_hit_count']}"
    return line


def _unresolved(q: dict) -> list[str]:
    """One line per unresolved source: the question's id and the entry number, nothing of the label (S3)."""
    return [f"{q['id']} ({q['part']}): {e} unresolved: its cited block is not found once at the measured commit; "
            f"counted as not found" for e in q.get("unresolved", [])]


def _families_line(doc: dict) -> str:
    named = doc.get("families") or []
    return "families: " + (", ".join(f"{f['name']} ({f['members']} members)" for f in named) or "none")


def _text(doc: dict) -> str:
    r, b, t = doc["retriever"], doc["budget"], doc["total"]
    out = [_families_line(doc), f"measure: set {doc['set']}, part {doc['part']}",
           f"retriever: kept outputs in {r['kept']} (no retriever run)" if r.get("kept") else
           f"retriever: {r['executable']}; version: {r['version']}; gov.__file__: {r['gov_file']}",
           f"root: {doc['root']} at commit {doc['commit']}",
           f"budget: batch size {b['batch_size']}, bundle budget {b['bundle_budget']}, "
           f"stack budget {b['stack_budget']} tokens"]
    for q in doc["questions"]:
        out.append(_line(q))
        out += _unresolved(q)
        for n, c in enumerate(q.get("compare", []), 1):  # a line that names one figure gives both (DEC-833)
            now = (f"; now hit@5 {'yes' if q['hit_at_5'] else 'no'}, "
                   f"full evidence {'yes' if q['full_evidence'] else 'no'}")
            out.append(f"{q['id']} ({q['part']}): " + (f"the same as record {n}" if c["same"] else
                                                       f"differ from record {n}: {', '.join(c['differs'])}{now}"))
    h, f = t["hit_at_5"], t["full_evidence"]
    out.append(f"total: hit@5 {h['count']} of {h['of']} ({h['percent']} %, floor {FLOOR}); "
               f"full evidence {f['count']} of {f['of']} ({f['percent']} %, target {TARGET} %)")
    return "\n".join(out)


def measure(args) -> dict:
    root, sets_root = Path(args.root).resolve(), Path(args.sets_root or args.root).resolve()
    try:
        entry = evaluation_sets(str(sets_root)).get(args.set)
        if not isinstance(entry, dict) or set_fault(entry):
            raise MeasureError(f"the set {args.set} is not declared, well formed, in {PATH_MAP_REL}'s {SETS_KEY}")
        parts = ["visible", "hidden"] if args.part == "all" else [args.part]
        if "hidden" in parts and _measured(entry, sets_root):
            raise MeasureError(f"the set {args.set} measures this session: its hidden part is refused (DEC-820 (d))")
    except PolicyError as error:
        raise MeasureError(f"the set {args.set} cannot be worked out: {error}") from None
    quoting = _Part("/q", [*entry.get("visible", []), *entry["hidden"], f"{EVALUATION}/**"], "")
    declared = families(sets_root, root)
    questions, cache = [], {}  # the gold files' lines at their commits, read once per run (S1)
    for part in parts:
        folder = sets_root / EVALUATION / args.set / part
        files = sorted(folder.glob("*.yaml")) if folder.is_dir() else []
        if part == "hidden":
            covered = _Part(str(sets_root), entry["hidden"], "")
            if not (covered.inside(str(folder)) or files and all(covered.inside(str(f)) for f in files)):
                raise MeasureError(f"the set {args.set}'s hidden globs do not cover its hidden folder: refused")
        questions += [_load(f, part, root, quoting, declared, cache) for f in files]
    if getattr(args, "kept", None):
        call = _Kept(args.kept)
        retriever = {"executable": None, "version": None, "gov_file": None, "kept": str(call.folder.resolve())}
    else:
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "GOV_TICKET")}
        retriever = _retriever(args.gov, root, env)
        call = _runner(retriever["executable"], root, env)
    done = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    scored = [_ask(q, args, call, quoting) for q in questions]
    if isinstance(call, _Kept):
        call.done()
    _compare(scored, args.compare)
    return {"families": [{"name": f.reason, "members": len(f.globs)} for f in declared],
            "retriever": retriever, "root": str(root), "commit": done.stdout.strip()[:12] or None, "set": args.set,
            "part": args.part, "budget": {"batch_size": args.batch_size, "bundle_budget": args.bundle_budget,
                                          "stack_budget": args.stack_budget},
            "questions": scored, "total": _total(scored)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m gov.retrieval.measure", description=__doc__.split("\n")[0])
    parser.add_argument("set")
    parser.add_argument("--root", default=".")
    parser.add_argument("--sets-root")
    parser.add_argument("--part", choices=("visible", "hidden", "all"), default="visible")
    parser.add_argument("--gov", default="gov")
    parser.add_argument("--kept", help="re-score a run's kept outputs (00001.json ... in call order); no retriever")
    parser.add_argument("--batch-size", type=int, default=10)
    parser.add_argument("--bundle-budget", type=int, default=6000)
    parser.add_argument("--stack-budget", type=int, default=24000)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out")
    parser.add_argument("--compare", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        doc = measure(args)
    except MeasureError as error:
        print(f"measure: {error}", file=sys.stderr)
        return 1
    if args.json:  # standard output stays one JSON document; the unresolved lines go to standard error
        for q in doc["questions"]:
            for line in _unresolved(q):
                print(line, file=sys.stderr)
    print(json.dumps(doc, indent=2) if args.json else _text(doc))
    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        n = 0
        while (path := out / f"measure-{args.set}-{args.part}-{stamp}{f'-{n}' if n else ''}.json").exists():
            n += 1
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
