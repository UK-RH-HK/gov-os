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
import shutil
import sqlite3
from pathlib import Path

import yaml

import w2_81_git as gitlib
from w2_81_judge import NOT_EMBEDDED, PATH_MAP, STORE, FINDINGS, record_name

PERFECT_FIGURES = {"hit_at_5": 85.0, "stacked_share": 99.0}  # exactly at the floors: the edge passes


def _namespace(paths, policy):
    return {"paths": paths, "memory_class": "governance", "sensitivity": "internal", "permitted_roles": ["engineer"],
            "retention": "kept in git history", "export_policy": "allowed", "embedding_policy": policy,
            "provenance": "the W2-81 stand-in", "deletion_rebuild": "rebuilt from git"}


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
    """Write the model: a copy of the built repository's working tree (no .git), with the outputs in it."""
    dest, beside = gitlib.outside_this_repository(dest), gitlib.outside_this_repository(beside)
    shutil.copytree(built.root, dest, ignore=shutil.ignore_patterns(".git"))
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
                                 "text TEXT); CREATE TABLE semantic_vector (chunk_id TEXT PRIMARY KEY, embedding BLOB);")
        for n, (rel, vector) in enumerate(sorted(model["index"].items())):
            connection.execute("INSERT INTO lexical_chunk (chunk_id, path, text) VALUES (?, ?, ?)",
                               (f"c{n}", rel, model.get("index_text", {}).get(rel, rel)))
            if vector:
                connection.execute("INSERT INTO semantic_vector VALUES (?, ?)", (f"c{n}", b"\0" * 16))
        connection.commit()
        connection.close()
    for rel, text in model["beside"].items():
        put(rel, text, beside)
    return dest, beside


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
