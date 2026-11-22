"""Stand-in adoption outputs for the judge's mutation self-tests (DEC-936 item 3.6). No adoption runs.

``perfect(built)`` is a model of what an adoption that handles every planted
problem and flags no control would leave. It holds the stage records in their
real names and fields (A0 to A6 and A8 as built), the provisional forms of what
is not built (A2's ``class``, the findings, A8's ``documents``, A7, A10 and the
lite verdict: README, "The judge"), the path map and the index. ``render(model,
dest, beside)`` writes it into a copy of the built repository's working tree. A
mutant is that model with one thing changed.
"""

from __future__ import annotations

import copy
import hashlib
import sqlite3
from pathlib import Path

import yaml

import w2_81_git as gitlib
from w2_81_judge import NOT_EMBEDDED, PATH_MAP, STORE, FINDINGS, record_name
from w2_81_score import E2E_BAR

PERFECT_FIGURES = {"end_to_end": E2E_BAR}  # exactly at the bar: the edge passes (hit@5 and the stacked share are diagnostics)


def _namespace(paths, policy):
    return {"paths": paths, "memory_class": "governance", "sensitivity": "internal", "permitted_roles": ["engineer"],
            "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": policy,
            "provenance": "the W2-81 stand-in", "deletion_rebuild": "rebuilt from git"}


VERDICT_CONDITIONS = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8", "lite A7 gate", "lite A10 gate")


def verdict_conditions(last="met"):
    """The lite verdict's conditions as a well-formed record gives them (W2-210 V5): every one met but the last, whose
    state is ``last`` (``met``, ``not met`` or ``accepted``, the last with its owner entry). The verdict that agrees:
    ADOPTED_HEALTHY, NOT_ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS."""
    found = [{"name": name, "source": "CAP-44.h", "state": "met"} for name in VERDICT_CONDITIONS]
    found[-1]["state"] = last
    if last == "accepted":
        found[-1]["owner_entry"] = "DEC-999"
    return found


def perfect(built):
    """The model of an adoption that handles everything planted in ``built`` and flags no control."""
    data = built.manifest
    files = sorted(gitlib.tree(built.root))
    large = {e["evidence"]["path"] for e in data["planted"] if e["kind"] == "large-file"}
    classes = {path: "current" for path in files}
    links = {}
    for entry in data["planted"]:
        ev = entry["evidence"]
        if entry["kind"] == "stale-spec":
            classes[ev["stale"]] = "historical"
            links[ev["stale"]] = {"newer_source": ev["governing"]}
        elif entry["kind"] == "superseded-plan":
            classes[ev["plan"]] = "superseded"
            links[ev["plan"]] = {"superseded_by": ev["successor"]}
        elif entry["kind"] == "misleading-name":
            classes[entry["paths"][0]] = "live" if ev["live"] else "dead"
        elif entry["kind"] == "large-file":
            classes[ev["path"]] = "large"
        elif entry["kind"] == "legacy-document":
            classes[ev["path"]] = "legacy"
    for control in data["controls"]:
        classes[control["paths"][0]] = "live" if control["kind"] == "live-file-in-legacy-folder" else "current"
    a2 = [{"path": p, "namespace": "large" if p in large else "project", "class": classes[p], **links.get(p, {})}
          for p in files]
    findings, documents = [], []
    secret_open = False
    for entry in data["planted"]:
        ev, n = entry["evidence"], len(findings) + 1
        if entry["kind"] == "secret":
            secret_open = True
            findings.append({"id": f"FINDING-{n:03d}", "type": "finding", "kind": "secret", "state": "OPEN",
                             "human_gate": "owner", "paths": [ev["path"]], "path": ev["path"],
                             "commit": ev["added_in"], "rule": ev["rule"]})
        elif entry["kind"] == "orphaned-test":
            findings.append({"id": f"FINDING-{n:03d}", "type": "finding", "kind": "orphaned-test", "state": "OPEN",
                             "human_gate": "owner", "paths": [ev["test"]], "test": ev["test"],
                             "subject": ev["subject"]})
        elif entry["kind"] == "stale-spec":
            findings.append({"id": f"FINDING-{n:03d}", "type": "finding", "kind": "drift", "state": "OPEN",
                             "human_gate": "owner", "paths": [ev["stale"]], "newer_source": ev["governing"]})
        elif entry["kind"] == "legacy-document":
            into = f"docs/records/extracted-{Path(ev['path']).stem}.md" if ev["handling"] == "extract" else None
            documents.append({"path": ev["path"], "disposition": "extracted" if into else "retired",
                              **({"into": into} if into else {})})
    return {
        "files": files,
        "records": {
            "A0": {"baseline_commit": data["head"], "backup_ref": f"refs/gov/adoption/backup/{data['head']}",
                   "tree": "clean"},
            "A1": {"commit": data["head"], "artefacts": [{"path": p} for p in files]},
            "A2": {"artefacts": a2, "unknown": [], "packages": []},
            "A3": {"artefacts": [{"path": p, "action": "KEEP"} for p in files]},
            "A4": {"batches": [], "dependents": [], "retirements": []},
            "A5": {"verdict": "governance/adoption/review/verdict.md"},
            "A6": {"batches": []},
            "A8": {"retired": [], "documents": documents, "imported": []},
            "A7": {"result": "pass", "checked": ["A6 against A3 and A4"]},
            "A10": {"result": "pass", "checked": ["A8", "the derived state rebuilt from git", "the canaries"]},
            "VERDICT": {"verdict": "NOT_ADOPTED_HEALTHY" if secret_open else "ADOPTED_HEALTHY", "lite": True,
                        "conditions": verdict_conditions("not met" if secret_open else "met"),
                        "conditions_not_checked": ["(2)", "(7)", "(8)", "(10)"]},
        },
        "findings": findings,
        "path_map": {"namespaces": {"large": _namespace(sorted(large) or ["data/none"], NOT_EMBEDDED),
                                    "project": _namespace(["**"], "embedded")}},
        "index": {p: (p not in large) for p in files if p not in large},  # path -> has semantic vectors
        "extra": {d["into"]: "---\nid: EXTRACTED\ntype: record\nstatus: ACTIVE\n---\nThe procedure, extracted.\n"
                  for d in documents if "into" in d},
        "removed": [],
        "beside": {"adoption.log": f"adoption of {data['repository']}: stages A0 to A10 recorded\n"},
        "raw": {},  # record or file -> bytes written as they are (unreadable or binary records)
    }


def _front(stage, data):
    head = {"id": f"ADOPT-{stage}", "type": "evidence", "status": "RECORDED", "state_class": "EVIDENCE",
            "stage": stage, **data}
    return "---\n" + yaml.safe_dump(head, sort_keys=False) + f"---\n\n# ADOPT-{stage}\n"


def render(model, built, dest, beside):
    """Write the model: a copy of the built repository's working tree (no .git), with the outputs in it. With
    ``dest`` the built repository itself, the outputs are written in place, as a launched session's adoption would."""
    dest, beside = gitlib.outside_this_repository(dest), gitlib.outside_this_repository(beside)
    if dest != Path(built.root).resolve():  # a shared clone: the build's history is there to compare with
        dest.parent.mkdir(parents=True, exist_ok=True)
        gitlib.run_git(dest.parent, "clone", "-q", "--shared", str(built.root), str(dest))
    beside.mkdir(parents=True, exist_ok=True)

    def put(rel, content, base=dest):
        path = gitlib.outside_this_repository(base / rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))

    for rel in model["removed"]:
        (dest / rel).unlink()
    a3_raw = None
    for stage in ("A0", "A1", "A2", "A3", "A4", "A6", "A8", "A7", "A10", "VERDICT", "A5"):
        if model["records"].get(stage) is None:
            continue
        data = dict(model["records"][stage])
        if stage == "A5" and a3_raw is not None and "path_map_hash" not in data:
            data["path_map_hash"] = hashlib.sha256(a3_raw).hexdigest()
        text = _front(stage, data).encode("utf-8")
        if stage == "A3":
            a3_raw = text
        put(record_name(stage), text)
    for item in model["findings"]:
        put(f"{FINDINGS}/{item['id']}.md", "---\n" + yaml.safe_dump(item, sort_keys=False) + "---\n")
    if model["path_map"] is not None:
        put(PATH_MAP, yaml.safe_dump(model["path_map"], sort_keys=False))
    for rel, text in model["extra"].items():
        put(rel, text)
    for rel, content in model["raw"].items():
        put(rel, content)
    if model["index"] is not None:
        store = gitlib.outside_this_repository(dest / STORE)
        store.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(store)
        connection.executescript("CREATE TABLE lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT UNIQUE, path TEXT, "
                                 "text TEXT);")
        vectors_table = not model.get("index_without_vector_table")  # gov rebuild without its embedder makes none
        if vectors_table:
            connection.execute("CREATE TABLE semantic_vector (chunk_id TEXT PRIMARY KEY, embedding BLOB)")
        for n, (rel, vector) in enumerate(sorted(model["index"].items())):
            connection.execute("INSERT INTO lexical_chunk (chunk_id, path, text) VALUES (?, ?, ?)",
                               (f"c{n}", rel, model.get("index_text", {}).get(rel, rel)))
            if vector and vectors_table:
                connection.execute("INSERT INTO semantic_vector VALUES (?, ?)", (f"c{n}", b"\0" * 16))
        connection.commit()
        connection.close()
    for rel, text in model["beside"].items():
        put(rel, text, beside)
    return dest, beside


_GOV = """#!/bin/sh
# A stand-in gov for the W2-81 runner's self-tests: it writes nothing but its call log and prints no question.
d="$0.d"
echo "$1" >> "$d/calls"
case "$1" in
  --version) echo "gov $(cat "$d/version") (commit 0123456789ab)" ;;
  retrieve)
    h=$(printf '%s\n%s' "${PWD##*/}" "$2" | sha256sum | cut -c1-64)  # its repository (the folder it runs in)
    if [ -f "$d/$h.json" ]; then cat "$d/$h.json"; else cat "$d/none.json"; fi ;;
  queue) exit "$(cat "$d/queue_exit")" ;;
  adopt) exit "$(cat "$d/adopt_exit")" ;;
  *) exit 64 ;;
esac
"""


def question_key(repository, text):
    """A question's key: its repository and its text, so two repositories asking the same text are answered apart
    (the runner runs ``gov retrieve`` in the repository's own folder, whose name the stand-in reads)."""
    return hashlib.sha256(f"{repository}\n{text}".encode()).hexdigest()


def write_gov(folder, name="gov", ranking=None, queue_exit=0, adopt_exit=0, version="0.1.4"):
    """A stand-in ``gov`` executable in ``folder`` (a POSIX shell script, quick to start): ``retrieve`` answers from
    ``ranking`` (question hash -> items), one answer file per question; ``queue`` and ``adopt`` exit as given;
    ``--version`` names ``version``; ``<gov>.d/calls`` lists the subcommands it was called with, one a line."""
    import json

    folder = gitlib.outside_this_repository(folder)
    answers = folder / f"{name}.d"
    answers.mkdir(parents=True, exist_ok=True)
    exe = folder / name
    exe.write_text(_GOV, encoding="utf-8")
    exe.chmod(0o755)

    def bundle(items):
        return json.dumps({"ok": True, "result": {"evidence": items, "continuation": None}})
    for key, items in (ranking or {}).items():
        (answers / f"{key}.json").write_text(bundle(items), encoding="utf-8")
    (answers / "none.json").write_text(bundle([]), encoding="utf-8")
    (answers / "queue_exit").write_text(str(queue_exit), encoding="utf-8")
    (answers / "adopt_exit").write_text(str(adopt_exit), encoding="utf-8")
    (answers / "version").write_text(version, encoding="utf-8")
    (answers / "calls").write_text("", encoding="utf-8")
    return exe


def calls_of(gov):
    """The subcommands a stand-in ``gov`` was called with so far, in order."""
    return (Path(f"{gov}.d") / "calls").read_text(encoding="utf-8").split()


def ranking_for(repository, asked, order="gold"):
    """A known ranking for one repository's resolved questions: ``gold`` puts each gold source first; ``forbidden``
    puts a forbidden citation first (where the question has one), then the gold; ``late`` puts five filler items
    before the gold (hit@5 is 0, the gold is in the context); ``none`` returns nothing useful."""
    out = {}
    for q in asked:
        gold = [{"path": p, "start_line": line, "end_line": line, "text": "evidence"} for p, line, _ in q.sources]
        bad = [{"path": p, "start_line": 1, "end_line": 1, "text": "planted"} for p in q.forbidden[:1]]
        filler = [{"path": f"filler/f{n}.md", "start_line": 1, "end_line": 1, "text": "filler"} for n in range(5)]
        out[question_key(repository, q.question)] = {"gold": gold, "forbidden": bad + gold, "none": [],
                                                     "late": filler + gold}[order]
    return out


def write_hidden_stand_in(folder, count=10):
    """A stand-in hidden half in a case's own folder (never the real one): for each repository, ``count`` questions
    in the visible form, made from the visible half's templates with texts of their own."""
    import yaml

    import w2_81_questions as questions

    folder = gitlib.outside_this_repository(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name, data in questions.sets_in(questions.VISIBLE).items():
        made = []
        for n in range(count):
            item = data["questions"][n % len(data["questions"])]
            made.append({**item, "id": f"{name}-h{n + 1:02d}",
                         "question": f"Stand-in hidden question {n + 1}: {item['question']}",
                         "gold_answer": f"Stand-in hidden answer {n + 1}: {item['gold_answer']}"})
        (folder / f"{name}.yaml").write_text(yaml.safe_dump({"form": questions.FORM, "repository": name,
                                                             "questions": made}, sort_keys=False), encoding="utf-8")
    return folder


def mutant(model):
    return copy.deepcopy(model)


def a2_entry(model, path):
    return next(item for item in model["records"]["A2"]["artefacts"] if item["path"] == path)


def a3_entry(model, path):
    return next(item for item in model["records"]["A3"]["artefacts"] if item["path"] == path)


def miss(model, entry):
    """The model with exactly the handling of ``entry`` (a planted problem) missing."""
    m, ev, kind = mutant(model), entry["evidence"], entry["kind"]
    if kind == "stale-spec":
        a2_entry(m, ev["stale"]).pop("class")
        a2_entry(m, ev["stale"]).pop("newer_source")
        m["findings"] = [f for f in m["findings"] if not (f["kind"] == "drift" and ev["stale"] in f["paths"])]
    elif kind == "superseded-plan":
        a2_entry(m, ev["plan"]).pop("class")
        a2_entry(m, ev["plan"]).pop("superseded_by")
    elif kind == "misleading-name":
        a2_entry(m, entry["paths"][0]).pop("class")
    elif kind == "secret":
        m["findings"] = [f for f in m["findings"] if not (f["kind"] == "secret" and f["path"] == ev["path"])]
    elif kind == "orphaned-test":
        m["findings"] = [f for f in m["findings"] if not (f["kind"] == "orphaned-test" and f["test"] == ev["test"])]
    elif kind == "legacy-document":
        m["records"]["A8"]["documents"] = [d for d in m["records"]["A8"]["documents"] if d["path"] != ev["path"]]
    elif kind == "large-file":
        a2_entry(m, ev["path"])["namespace"] = None
    else:
        raise AssertionError(f"no miss for {kind}")
    return m


def flag(model, control):
    """The model with ``control`` flagged: classed by its looks, not by its content and references."""
    m = mutant(model)
    a2_entry(m, control["paths"][0])["class"] = "historical" if control["kind"] == "current-spec-looks-old" \
        else "legacy"
    return m


# --------------------------------------------------------------------------
# A stand-in model CLI (the reader's and the grader's sessions): no model runs
# --------------------------------------------------------------------------

def _argv_value(argv, flag):
    return argv[argv.index(flag) + 1]


class Sessions:
    """A stand-in session starter: ``start(argv, prompt, cwd)`` answers the way the product's ``claude -p`` prints.

    It records every call (``calls``: ``(role, argv)``, the role told by the argv's system prompt). The reader cites
    the first item of the last bundle it is shown (so a ranking that puts a gold source first is cited right, and one
    that puts a forbidden citation first is cited wrong). The grader says ``correct``. Knobs, each keyed by a
    question's text (the prompt carries it): ``forbid`` maps a text to a forbidden path the reader also cites;
    ``grade`` maps a text to the grade the grader gives it; ``reader`` is ``cite-first`` (answers at once),
    ``search-first`` (asks for one more search in the question's own words, then answers), ``search-twice``
    (asks for a second search too), ``error`` (answers nothing), ``not-found``, or ``cite-gold`` (cites the gold
    source ``gold`` maps the question's text to, wherever it ranks). ``grade`` may hold ``"*"`` for every other text."""

    def __init__(self, reader="cite-first", forbid=None, grade=None, gold=None):
        self.reader, self.forbid, self.grade, self.gold = reader, dict(forbid or {}), dict(grade or {}), dict(gold or {})
        self.calls = []

    def roles(self):
        return [role for role, _ in self.calls]

    def argvs(self, role):
        return [argv for r, argv in self.calls if r == role]

    def __call__(self, argv, prompt, cwd):
        import json

        from gov.memaudit import prompts

        system = _argv_value(argv, "--system-prompt")
        role = "reader" if system == prompts.READER_SYS else "grader" if system == prompts.GRADER_SYS else "other"
        self.calls.append((role, list(argv)))
        if role == "reader":
            out = self._reader(prompt)
        elif role == "grader":
            text = next((t for t in self.grade if f"Question: {t}\n\nGold answer:" in prompt), None)
            out = {"grade": self.grade.get(text, self.grade.get("*", "correct")),
                   "reason": "the stand-in grader's reason"}
        else:
            return ""
        return "" if out is None else json.dumps({"structured_output": out, "total_cost_usd": 0.0,
                                                  "usage": {"input_tokens": 1, "output_tokens": 1}})

    def _reader(self, prompt):
        import re

        text = prompt[len("Question: "):prompt.index("\n\n=== Bundle 1 ===")]
        bundles = prompt.split("=== Bundle ")[1:]
        items = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in
                 re.finditer(r"^--- (\S+) lines (\d+)-(\d+)$", bundles[-1] if bundles else "", re.M)]
        if self.reader == "error":
            return None
        if self.reader == "not-found" or not items and self.reader == "cite-first":
            return {"verdict": "not_found", "answer": "Not in the bundles.", "citations": [], "search": ""}
        if self.reader == "search-twice" or (self.reader == "search-first" and len(bundles) < 2):
            return {"verdict": "search_again", "answer": "", "citations": [], "search": text}
        cites = [{"path": p, "start_line": a, "end_line": z} for p, a, z in items[:1]]
        if self.reader == "cite-gold":
            cites = [{"path": p, "start_line": line, "end_line": line} for p, line in self.gold[text]]
        if text in self.forbid:
            cites.append({"path": self.forbid[text], "start_line": 1, "end_line": 1})
        return {"verdict": "answer", "answer": "STAND-IN ANSWER: see " + (items[0][0] if items else "nothing"),
                "citations": cites, "search": ""}


def write_claude(folder, name="claude"):
    """A stand-in ``claude`` executable for the command run as a process (a small script, quick to start): the reader
    cites the first item of the last bundle it is shown and the grader says ``correct``. No model runs."""
    import sys

    exe = gitlib.outside_this_repository(folder) / name
    exe.parent.mkdir(parents=True, exist_ok=True)
    exe.write_text(f"""#!{sys.executable}
import json, re, sys
argv, prompt = sys.argv, sys.stdin.read()
system = argv[argv.index("--system-prompt") + 1]
if system.startswith("You answer one question"):
    last = prompt.split("=== Bundle ")[-1]
    items = re.findall(r"^--- (\\S+) lines (\\d+)-(\\d+)$", last, re.M)
    out = {{"verdict": "answer", "answer": "STAND-IN ANSWER", "search": "", "citations": [
        {{"path": p, "start_line": int(a), "end_line": int(z)}} for p, a, z in items[:1]]}}
else:
    out = {{"grade": "correct", "reason": "the stand-in grader's reason"}}
print(json.dumps({{"structured_output": out, "total_cost_usd": 0.0}}))
""", encoding="utf-8")
    exe.chmod(0o755)
    return exe
