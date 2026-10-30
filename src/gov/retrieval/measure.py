"""The standing retrieval measure: an evaluation set's questions asked of ``gov retrieve``, scored (W2-61; DEC-828
items 3 and 4, DEC-833, DEC-860, DEC-820 (d)).

``python3 -m gov.retrieval.measure <set> [--root <dir>] [--sets-root <dir>] [--part visible|hidden|all]
[--gov <executable>] [--batch-size 10] [--bundle-budget 6000] [--stack-budget 24000] [--json] [--out <dir>]
[--compare <record>]...``

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
FLOOR, TARGET = 85, 99
TOKEN_CHARS = 4
FIGURES = ("hit_at_5", "in_bundle", "full_evidence", "first_gold_rank", "stacked_digest")
_HEADING = re.compile(r"(#{1,6})\s")


class MeasureError(Exception):
    """A refusal or a fault that ends the run; its text names a hidden question by its id only."""


def _fault(part: str, qid: str, kind: str, detail: str = "") -> MeasureError:
    return MeasureError(f"{part} question {qid}: {kind}" + (f": {detail}" if detail and part != "hidden" else ""))


def _measured(entry: dict, sets_root: Path) -> bool:
    measures = entry["measures"]
    if os.environ.get("GOV_ROLE", "") in measures.get("roles", []):
        return True
    tickets, ticket = measures.get("tickets", []), os.environ.get("GOV_TICKET")
    return bool(tickets and ticket) and not _ticket(str(sets_root), ticket)[0].isdisjoint(tickets)


def _span(source: dict, root: Path, part: str, qid: str) -> tuple[int, int]:
    file = root / source["path"]
    if not file.is_file():
        raise _fault(part, qid, "a source's path does not exist in the measured root", source["path"])
    lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
    stated = source.get("lines")
    if stated is not None and not (isinstance(stated, list) and len(stated) == 2
                                   and all(isinstance(n, int) for n in stated) and 1 <= stated[0] <= stated[1]):
        raise _fault(part, qid, "malformed question", "lines is not [first, last]")
    heading = source.get("heading")
    if heading is None:
        return tuple(stated) if stated else (1, max(len(lines), 1))
    at = next((i for i, line in enumerate(lines) if line.rstrip() == str(heading).rstrip()), None)
    if at is None:
        if not stated:
            raise _fault(part, qid, "malformed question", "a heading is not found and no lines are stated")
        return tuple(stated)
    mark = _HEADING.match(lines[at])
    if not mark:
        return at + 1, at + (stated[1] - stated[0] + 1 if stated else 1)
    level = len(mark.group(1))
    end = next((j for j in range(at + 1, len(lines))
                if (m := _HEADING.match(lines[j])) and len(m.group(1)) <= level), len(lines))
    return at + 1, end


def _load(file: Path, part: str, root: Path, quoting: _Part) -> dict:
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
    entries = []
    for entry in sources:
        alternatives = entry if isinstance(entry, list) else [entry]
        if not alternatives or not all(isinstance(a, dict) and isinstance(a.get("path"), str) and a["path"]
                                       for a in alternatives):
            raise _fault(part, qid, "malformed question", "a source names no path")
        # an alternative in the set's own parts or the evaluation files never counts and is never opened
        entries.append([(a["path"], *_span(a, root, part, qid)) for a in alternatives
                        if not quoting.inside(f"/q/{a['path']}")])
    return {"id": qid, "part": part, "question": data["question"], "sources": entries, "ticket": data.get("ticket"),
            "ids": data.get("ids") or [], "radius": data.get("radius")}


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


def _ask(q: dict, args, exe: str, root: Path, env: dict, quoting: _Part) -> dict:
    options = [*(["--ticket", str(q["ticket"])] if q["ticket"] else []),
               *[w for i in q["ids"] for w in ("--id", str(i))],
               *(["--radius", str(q["radius"])] if q["radius"] is not None else []),
               "--batch-size", str(args.batch_size), "--bundle-budget", str(args.bundle_budget)]
    stacked, seen, used, first, token, calls = [], set(), 0, None, None, 0
    while True:
        done = subprocess.run([exe, "retrieve", *options, *(["--continue", token] if token else []), q["question"],
                               "--json"], cwd=root, env=env, capture_output=True, text=True)
        calls += 1
        try:
            doc = json.loads(done.stdout)
            bundle = doc["result"] if isinstance(doc.get("result"), dict) else doc
            items = [(i["path"], int(i["start_line"]), int(i["end_line"]), str(i.get("text", "")))
                     for i in bundle["evidence"]]
        except (ValueError, KeyError, TypeError, AttributeError):
            items = None
        if done.returncode != 0 or items is None or doc.get("ok") is False:
            raise _fault(q["part"], q["id"], "the retrieval failed", f"exit {done.returncode}")
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

    def hits(item, entry):
        return not quoting.inside(f"/q/{item[0]}") and any(
            item[0] == path and item[1] <= last and first_line <= item[2] for path, first_line, last in entry)

    rank = next((n for n, item in enumerate(stacked, 1) if any(hits(item, e) for e in q["sources"])), None)
    found = sum(any(hits(item, e) for item in stacked) for e in q["sources"])
    digest = hashlib.sha256(json.dumps([list(i[:3]) for i in stacked]).encode()).hexdigest()[:16]
    return {"id": q["id"], "part": q["part"], "hit_at_5": rank is not None and rank <= 5,
            "in_bundle": any(hits(item, e) for item in first for e in q["sources"]),
            "full_evidence": found == len(q["sources"]), "first_gold_rank": rank, "pieces_found": found,
            "pieces_needed": len(q["sources"]), "calls": calls, "stacked_digest": digest}


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
    return (f"{q['id']} ({q['part']}): hit@5 {yes(q['hit_at_5'])} (first gold rank {q['first_gold_rank'] or '-'}), "
            f"in the bundle {yes(q['in_bundle'])}; full evidence {yes(q['full_evidence'])} "
            f"({q['pieces_found']} of {q['pieces_needed']} pieces); {q['calls']} calls")


def _text(doc: dict) -> str:
    r, b, t = doc["retriever"], doc["budget"], doc["total"]
    out = [f"measure: set {doc['set']}, part {doc['part']}",
           f"retriever: {r['executable']}; version: {r['version']}; gov.__file__: {r['gov_file']}",
           f"root: {doc['root']} at commit {doc['commit']}",
           f"budget: batch size {b['batch_size']}, bundle budget {b['bundle_budget']}, "
           f"stack budget {b['stack_budget']} tokens"]
    for q in doc["questions"]:
        out.append(_line(q))
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
    questions = []
    for part in parts:
        folder = sets_root / EVALUATION / args.set / part
        files = sorted(folder.glob("*.yaml")) if folder.is_dir() else []
        if part == "hidden":
            covered = _Part(str(sets_root), entry["hidden"], "")
            if not (covered.inside(str(folder)) or files and all(covered.inside(str(f)) for f in files)):
                raise MeasureError(f"the set {args.set}'s hidden globs do not cover its hidden folder: refused")
        questions += [_load(f, part, root, quoting) for f in files]
    env = {k: v for k, v in os.environ.items() if k not in ("PYTHONPATH", "GOV_TICKET")}
    retriever = _retriever(args.gov, root, env)
    done = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    scored = [_ask(q, args, retriever["executable"], root, env, quoting) for q in questions]
    _compare(scored, args.compare)
    return {"retriever": retriever, "root": str(root), "commit": done.stdout.strip()[:12] or None, "set": args.set,
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
