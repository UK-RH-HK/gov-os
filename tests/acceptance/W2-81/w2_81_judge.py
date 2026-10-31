"""The judge of the W2-81 proving ground (DEC-936 item 3.6, DEC-941; CAP-44.b to CAP-44.j).

Given one repository's manifest and an adoption's outputs on it, the judge gives
each planted problem FOUND_AND_HANDLED, MISSED, MISHANDLED or NOT_BUILT, with the
evidence it read (record and field), and each control CLEAN or FLAGGED. Over all
the repositories and the question figures, it gives READY or NOT_READY, naming
each reason. It writes nothing and prints nothing.

**What it reads (the adoption's outputs).** The adopted repository's working tree:

- the stage records ``governance/adoption/<stage>-<title>.md`` (YAML front matter), named
  as ``gov.adopt.project.record_path`` names them for the stages built, and as
  ``PROVISIONAL`` names them for the stages not built yet (A7, A10, the lite verdict);
- the findings ``governance/adoption/findings/*.md`` (CAP-44.g, not built: provisional form);
- the project's path map ``governance/project/path-map.yaml`` (its namespaces' ``embedding_policy``);
- the index ``.gov-runtime/store.db`` (``lexical_chunk.path``, ``semantic_vector.chunk_id``);
- for the secret, every file of the working tree outside ``.git`` and every file of the
  folder beside it (logs, reports), read as bytes, and every path name.

**It fails closed.**

- A missing, unreadable or malformed record proves nothing, so a planted problem that
  needs it is MISSED, never handled.
- A handling that needs a capability not built today is NOT_BUILT and names the
  capability. It is never passed.
- A judge error is an ERROR result, never READY.
- Where several statuses apply, MISHANDLED comes first, then NOT_BUILT, then MISSED.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import w2_81_manifest as manifest_form

FOUND, MISSED, MISHANDLED, NOT_BUILT = "FOUND_AND_HANDLED", "MISSED", "MISHANDLED", "NOT_BUILT"
CLEAN, FLAGGED = "CLEAN", "FLAGGED"
READY, NOT_READY, ERROR = "READY", "NOT_READY", "ERROR"
PRECEDENCE = (MISHANDLED, NOT_BUILT, MISSED, FOUND)

FOLDER = "governance/adoption"
FINDINGS = f"{FOLDER}/findings"
PATH_MAP = "governance/project/path-map.yaml"
STORE = ".gov-runtime/store.db"
NOT_EMBEDDED = "not embedded"

# The classes a content classification gives (A2, provisional: CAP-44.b as built classes by namespace only).
CLASSES = ("current", "historical", "superseded", "live", "dead", "legacy", "large")
FLAGGING_CLASSES = ("historical", "superseded", "dead", "legacy", "stale")
FINDING_KINDS = ("secret", "orphaned-test", "drift")
FINDING_STATES = ("OPEN", "ACCEPTED", "RESOLVED")
VERDICTS = ("ADOPTED_HEALTHY", "ADOPTED_WITH_ACCEPTED_EXCEPTIONS", "NOT_ADOPTED_HEALTHY")
LEAVING = ("MOVE", "RENAME", "SPLIT", "MERGE", "EXTRACT", "RETIRE", "DELETE_FROM_ACTIVE_TREE")
from w2_81_score import FLOORS  # noqa: E402 - CAP-10's floor; DEC-833's target, one constant each

# The record names of the stages not built yet: the provisional form the stand-ins write (README, "The judge").
PROVISIONAL = {"A7": f"{FOLDER}/A7-independent-migration-verification.md",
               "A10": f"{FOLDER}/A10-independent-memory-verification.md",
               "VERDICT": f"{FOLDER}/VERDICT-lite.md"}
BUILT_STAGES = ("A0", "A1", "A2", "A3", "A4", "A5", "A6", "A8")
STAGES = (*BUILT_STAGES, "A7", "A10", "VERDICT")

# What each handling needs. ``built`` is today's state of the code, as read in src/gov/adopt/ on 2026-10-31.
CAPABILITIES = {
    "A2-namespace": ("CAP-44.b", True, "A2 classes each tracked file by the path map's namespace "
                     "(stages.a2, project.classify)"),
    "A2-content-class": ("CAP-44.b", False, "A2 classes by path-map namespace only and reads no content: "
                         "no class current, historical, superseded, live or dead, no successor or newer "
                         "source, is recorded"),
    "findings": ("CAP-44.g", False, "finding states and human gates: no stage scans the history for secrets or "
                 "records a finding (a secret, an orphaned test, drift) with a state and a gate"),
    "A8-documents": ("CAP-44.e", False, "A8 retires rule files, memory stores and chat databases only "
                     "(legacy.KINDS); it extracts or retires no legacy document"),
    "index": ("CAP-44.d", True, "gov rebuild after A6 and A8 recreates .gov-runtime/store.db; the semantic "
              "vectors hold only namespaces whose embedding_policy is `embedded`"),
    "A3": ("CAP-44.b", True, "A3 records the path map from the caller's proposal"),
    "A5": ("CAP-44.c", True, "A5 records the independent review of the path map"),
    "A6": ("CAP-44.d", True, "A6 executes the batches"),
    "A7": ("CAP-44.f", False, "the lite A7 gate: independent migration verification"),
    "A10": ("CAP-44.f", False, "the lite A10 gate: independent memory verification"),
    "VERDICT": ("CAP-44.h", False, "the lite adoption verdict"),
}
NEEDS = {"stale-spec": ("A2-content-class", "findings"),  # either one suffices
         "superseded-plan": ("A2-content-class",), "misleading-name": ("A2-content-class",),
         "secret": ("findings",), "orphaned-test": ("findings",), "legacy-document": ("A8-documents",),
         "large-file": ("A2-namespace", "index")}
ALL_OF = {"large-file"}  # every capability listed is needed; for the others, any one
_SKIP_MARKS = ("mark." + "skip", "#[" + "ignore]", "test." + "skip", "it." + "skip", "describe." + "skip", "xit(",
               "t." + "Skip(")


class JudgeError(Exception):
    """The judge cannot judge: its result is ERROR, never READY."""


def built_today():
    """Today's built capabilities. A7 and A10 count as built once the adoption tool lists them as stages."""
    built = {name for name, (_, is_built, _) in CAPABILITIES.items() if is_built}
    from gov.adopt import project  # the code under test (DEC-732): this worktree's src/

    built |= {stage for stage in ("A7", "A10") if stage in project.STAGES}
    return built


def record_name(stage):
    if stage in BUILT_STAGES:
        from gov.adopt import project

        return project.record_path(stage)
    return PROVISIONAL[stage]


# --------------------------------------------------------------------------
# Reading the outputs, failing closed
# --------------------------------------------------------------------------

@dataclass
class Record:
    rel: str
    state: str  # PRESENT, ABSENT, UNREADABLE, MALFORMED
    data: dict = field(default_factory=dict)
    raw: bytes = b""
    why: str = ""


def _front(raw):
    text = raw.decode("utf-8")
    lines = text.split("\n")
    if lines[0].rstrip() != "---" or "---" not in [line.rstrip() for line in lines[1:]]:
        raise ValueError("no front matter")
    end = [line.rstrip() for line in lines].index("---", 1)
    data = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(data, dict):
        raise ValueError("the front matter is not a mapping")
    return data


def _is_list_of_maps(value, required=()):
    return isinstance(value, list) and all(isinstance(item, dict) and all(
        isinstance(item.get(key), str) for key in required) for item in value)


SHAPES = {  # record -> the field that must be a list of mappings, and the string keys each mapping needs
    "A2": ("artefacts", ("path",)), "A3": ("artefacts", ("path", "action")), "A6": ("batches", ()),
    "A8": ("retired", ("path",)),
}


def read_record(root, rel, stage=None):
    path = Path(root) / rel
    if not path.is_file():
        return Record(rel, "ABSENT", why="no such record")
    try:
        raw = path.read_bytes()
        data = _front(raw)
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
        return Record(rel, "UNREADABLE", why=type(exc).__name__)
    shape = SHAPES.get(stage)
    if shape and not _is_list_of_maps(data.get(shape[0]), shape[1]):
        return Record(rel, "MALFORMED", data, raw, why=f"`{shape[0]}` is not a list of mappings with {shape[1]}")
    if stage == "A2" and not all(item.get("class") is None or item.get("class") in CLASSES
                                 for item in data["artefacts"]):
        return Record(rel, "MALFORMED", data, raw, why="a class outside the vocabulary")
    if stage == "VERDICT" and data.get("verdict") not in VERDICTS:
        return Record(rel, "MALFORMED", data, raw, why="`verdict` is none of " + ", ".join(VERDICTS))
    return Record(rel, "PRESENT", data, raw)


def read_findings(root):
    """The findings, each a Record; the folder's own state (ABSENT, PRESENT)."""
    folder = Path(root) / FINDINGS
    if not folder.is_dir():
        return "ABSENT", []
    found = []
    for path in sorted(folder.iterdir()):
        rel = f"{FINDINGS}/{path.name}"
        record = read_record(root, rel)
        if record.state == "PRESENT":
            data = record.data
            if data.get("kind") not in FINDING_KINDS or data.get("state") not in FINDING_STATES \
                    or not isinstance(data.get("paths", []), list):
                record = Record(rel, "MALFORMED", data, record.raw, why="kind, state or paths outside the form")
        found.append(record)
    return "PRESENT", found


def read_path_map(root):
    path = Path(root) / PATH_MAP
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        spaces = data["namespaces"]
        if not isinstance(spaces, dict):
            raise ValueError
        return spaces, ""
    except FileNotFoundError:
        return None, "absent"
    except (OSError, UnicodeDecodeError, yaml.YAMLError, KeyError, TypeError, ValueError):
        return None, "unreadable"


def read_index(root):
    """The paths in the lexical index and in the semantic vectors; None and why when the store cannot be read."""
    path = Path(root) / STORE
    if not path.is_file():
        return None, "absent"
    try:
        connection = sqlite3.connect(f"file:{path}?mode=ro&immutable=1", uri=True)
        try:
            lexical = {row[0] for row in connection.execute("SELECT path FROM lexical_chunk")}
            semantic = {row[0] for row in connection.execute(
                "SELECT c.path FROM lexical_chunk c JOIN semantic_vector v ON v.chunk_id = c.chunk_id")}
        finally:
            connection.close()
    except sqlite3.Error:
        return None, "unreadable"
    return {"lexical": lexical, "semantic": semantic}, ""


def output_files(root, beside):
    """Every output file: the working tree outside .git, and the folder beside it. Returns (files, unreadable)."""
    files, unreadable = [], []
    for base in [Path(root)] + ([Path(beside)] if beside else []):
        for folder, dirs, names in os.walk(base):
            dirs[:] = sorted(d for d in dirs if not (Path(folder) == Path(root) and d == ".git"))
            for name in sorted(names) + [d for d in dirs if (Path(folder) / d).is_symlink()]:
                files.append(Path(folder) / name)
    readable = []
    for path in files:
        if path.is_symlink() or not path.is_file():
            unreadable.append(path)
        else:
            readable.append(path)
    return readable, unreadable


# --------------------------------------------------------------------------
# Judging one repository
# --------------------------------------------------------------------------

class _View:
    """The outputs of one adoption, read once."""

    def __init__(self, root, beside):
        self.root, self.beside = Path(root), beside
        self.records = {stage: read_record(root, record_name(stage), stage) for stage in STAGES}
        self.findings_state, self.findings = read_findings(root)
        self.spaces, self.map_why = read_path_map(root)
        self.index, self.index_why = read_index(root)

    def ok(self, stage):
        return self.records[stage].state == "PRESENT"

    def entry(self, stage, path):
        if not self.ok(stage):
            return None
        key = SHAPES[stage][0]
        return next((item for item in self.records[stage].data[key] if item.get("path") == path), None)

    def exists(self, path):
        return (self.root / path).is_file()

    def reviewed(self):
        """A5's record stands on A3's record as it is (its path_map_hash), so the path map was reviewed."""
        return self.ok("A3") and self.ok("A5") and \
            self.records["A5"].data.get("path_map_hash") == hashlib.sha256(self.records["A3"].raw).hexdigest()

    def good_findings(self, kind):
        return [r for r in self.findings if r.state == "PRESENT" and r.data.get("kind") == kind]


class _Case:
    """The judgement of one planted problem: statuses with their evidence, the most severe wins."""

    def __init__(self, entry):
        self.entry, self.seen = entry, []

    def add(self, status, record, fieldname, said):
        self.seen.append({"status": status, "record": record, "field": fieldname, "said": said})

    def result(self):
        statuses = [s["status"] for s in self.seen] or [MISSED]
        status = next(s for s in PRECEDENCE if s in statuses)
        return {"id": self.entry["id"], "kind": self.entry["kind"], "variant": self.entry["variant"],
                "status": status, "evidence": self.seen or [{"status": MISSED, "record": None, "field": None,
                                                              "said": "no record shows it"}]}


def _class_of(view, path):
    entry = view.entry("A2", path)
    return entry.get("class") if entry else None


def _missing_records(case, view, *stages):
    """MISSED for each record the handling reads that is absent, unreadable or malformed. True if any."""
    bad = False
    for stage in stages:
        record = view.records[stage]
        if record.state != "PRESENT":
            case.add(MISSED, record.rel, None, f"the record is {record.state}: {record.why}")
            bad = True
    return bad


def _moved_or_deleted(case, view, path, what):
    """MISHANDLED when ``path`` left its place without a proposal reviewed at A5; True when it left."""
    if view.exists(path):
        return False
    entry = view.entry("A3", path)
    if entry and entry.get("action") in ("MOVE", "RENAME") and view.reviewed() and what == "rename":
        return True  # a governed batch reviewed at A5: allowed, but it is not the handling itself
    case.add(MISHANDLED, path, None, f"{path} is gone from the working tree "
             + ("without a proposal reviewed at A5" if what == "rename" else "(deleted or moved away)"))
    return True


def _cited_as_governing(view, path):
    """Where a record names ``path`` as the governing or newer source."""
    cites = []
    if view.ok("A2"):
        for item in view.records["A2"].data["artefacts"]:
            if path in (item.get("newer_source"), item.get("superseded_by"), item.get("governing_source")):
                cites.append(record_name("A2"))
    for record in view.findings:
        if record.state == "PRESENT" and path in (record.data.get("newer_source"), record.data.get("governing_source")):
            cites.append(record.rel)
    return cites


def _stale_spec(case, view, ev, built):
    stale, governing = ev["stale"], ev["governing"]
    for where in _cited_as_governing(view, stale):
        case.add(MISHANDLED, where, "newer_source", f"{stale} is cited as the governing source")
    if "A2-content-class" in built:
        if not _missing_records(case, view, "A2"):
            klass = _class_of(view, stale)
            if klass == "historical":
                case.add(FOUND, record_name("A2"), "artefacts[].class", f"{stale} classed historical")
            elif klass == "current":
                case.add(MISHANDLED, record_name("A2"), "artefacts[].class", f"{stale} classed current")
            if _class_of(view, governing) in FLAGGING_CLASSES:
                case.add(MISHANDLED, record_name("A2"), "artefacts[].class", f"the newer source {governing} "
                         "classed as not current")
    if "findings" in built:
        for record in view.good_findings("drift"):
            if stale in record.data.get("paths", []) and record.data.get("newer_source") == governing:
                case.add(FOUND, record.rel, "newer_source", f"drift flagged on {stale}, naming {governing}")


def _superseded_plan(case, view, ev, built):
    plan, successor = ev["plan"], ev["successor"]
    _moved_or_deleted(case, view, plan, "delete")
    entry = view.entry("A3", plan)
    if entry and entry.get("action") in LEAVING:
        case.add(MISHANDLED, record_name("A3"), "artefacts[].action", f"{plan}: {entry['action']}")
    if "A2-content-class" in built and not _missing_records(case, view, "A2"):
        a2 = view.entry("A2", plan) or {}
        if a2.get("class") == "superseded" and a2.get("superseded_by") == successor:
            case.add(FOUND, record_name("A2"), "artefacts[].superseded_by", f"{plan} linked to {successor}")
        elif a2.get("class") == "current":
            case.add(MISHANDLED, record_name("A2"), "artefacts[].class", f"{plan} classed current")


def _misleading_name(case, view, ev, path, built):
    _moved_or_deleted(case, view, path, "rename")
    entry = view.entry("A3", path)
    if ev["live"] and entry and entry.get("action") in ("RETIRE", "DELETE_FROM_ACTIVE_TREE"):
        case.add(MISHANDLED, record_name("A3"), "artefacts[].action", f"the live {path}: {entry['action']}")
    if "A2-content-class" in built and not _missing_records(case, view, "A2"):
        klass, wanted = _class_of(view, path), ("live" if ev["live"] else "dead")
        if klass == wanted:
            case.add(FOUND, record_name("A2"), "artefacts[].class", f"{path} classed {wanted} by its references")
        elif klass in ("live", "dead", "current", "legacy", "historical"):
            case.add(MISHANDLED, record_name("A2"), "artefacts[].class", f"{path} classed {klass}, not {wanted}")


def _secret(case, view, ev, built, held, verdict):
    files, unreadable = output_files(view.root, view.beside)
    if held is None:
        case.add(MISSED, None, None, "no value was given to compare the outputs with")
    else:
        for path in files:
            try:
                data = path.read_bytes()
            except OSError:
                unreadable.append(path)
                continue
            if held.found_in(str(path)):  # the name itself holds the value: the evidence names its folder only
                case.add(MISHANDLED, _rel(path.parent, view) + "/<a name holding the value>", None,
                         f"the value of the secret in {ev['path']} names an output")
            elif held.found_in(data):
                case.add(MISHANDLED, _rel(path, view), None, f"the value of the secret in {ev['path']} is in "
                         "this output")
    for path in unreadable:
        case.add(MISSED, _rel(path, view), None, "an output cannot be read, so it rules nothing out")
    if "findings" not in built:
        return
    if view.findings_state == "ABSENT":
        case.add(MISSED, FINDINGS, None, "no findings were recorded")
    for record in view.findings:
        if record.state != "PRESENT":
            case.add(MISSED, record.rel, None, f"a finding is {record.state}")
    for record in view.good_findings("secret"):
        data = record.data
        if data.get("path") != ev["path"]:
            continue
        extra = sorted(set(data) - {"id", "type", "kind", "state", "human_gate", "paths", "path", "commit", "rule",
                                    "status", "state_class"})
        if data.get("commit") != ev["added_in"] or data.get("rule") != ev["rule"]:
            case.add(MISSED, record.rel, "commit, rule", f"the finding on {ev['path']} names another commit or rule")
        elif extra:
            case.add(MISHANDLED, record.rel, ", ".join(extra), "the finding holds more than path, commit and rule")
        elif data.get("state") != "OPEN" or data.get("human_gate") != "owner":
            case.add(MISHANDLED, record.rel, "state, human_gate", "the finding does not stand behind the owner's gate")
        else:
            case.add(FOUND, record.rel, "path, commit, rule", f"{ev['path']} at {ev['added_in']}, {ev['rule']}, "
                     "open behind the owner's gate")
            if verdict == "ADOPTED_HEALTHY":
                case.add(MISHANDLED, record_name("VERDICT"), "verdict", "ADOPTED_HEALTHY while the secret's finding "
                         "is open")


def _rel(path, view):
    for base in (view.root, Path(view.beside) if view.beside else None):
        if base is not None:
            try:
                return f"{'beside' if base != view.root else 'repository'}:{Path(path).relative_to(base).as_posix()}"
            except ValueError:
                pass
    return str(path)


def _orphaned_test(case, view, ev, built):
    test = ev["test"]
    if not view.exists(test):
        case.add(MISHANDLED, test, None, f"the orphaned test {test} is deleted")
    else:
        text = (view.root / test).read_text(encoding="utf-8", errors="replace")
        if ev["used_as"] not in text or any(mark in text for mark in _SKIP_MARKS):
            case.add(MISHANDLED, test, None, f"the orphaned test {test} is changed or skipped")
    entry = view.entry("A3", test)
    if entry and entry.get("action") in ("RETIRE", "DELETE_FROM_ACTIVE_TREE"):
        case.add(MISHANDLED, record_name("A3"), "artefacts[].action", f"{test}: {entry['action']}")
    if "findings" not in built:
        return
    subject_names = {ev["subject"], ev["subject"].split("::")[0], ev["definition"]}
    for record in view.good_findings("orphaned-test"):
        if record.data.get("test") == test and record.data.get("subject") in subject_names:
            case.add(FOUND, record.rel, "test, subject", f"{test} reported with its missing subject")


def _legacy_document(case, view, ev, built):
    if "A8-documents" not in built or _missing_records(case, view, "A8"):
        return
    documents = view.records["A8"].data.get("documents")
    if not _is_list_of_maps(documents, ("path", "disposition")):
        case.add(MISSED, record_name("A8"), "documents", "the record's documents are not a list of mappings")
        return
    entry = next((item for item in documents if item["path"] == ev["path"]), None)
    wanted = {"extract": "extracted", "retire": "retired"}[ev["handling"]]
    if entry is None:
        return
    if entry["disposition"] == wanted and (wanted != "extracted" or (
            isinstance(entry.get("into"), str) and view.exists(entry["into"]))):
        case.add(FOUND, record_name("A8"), "documents[].disposition", f"{ev['path']} {wanted}")
    else:
        case.add(MISHANDLED, record_name("A8"), "documents[].disposition",
                 f"{ev['path']} {entry['disposition']}, not {wanted}")


def _large_file(case, view, ev, built):
    path = ev["path"]
    if _missing_records(case, view, "A2"):
        return
    entry = view.entry("A2", path)
    if view.index is None:
        case.add(MISSED, STORE, None, f"the index is {view.index_why}")
    elif path in view.index["semantic"]:
        case.add(MISHANDLED, STORE, "semantic_vector", f"{path} is in the semantic index")
    if view.spaces is None:
        case.add(MISSED, PATH_MAP, None, f"the path map is {view.map_why}")
        return
    space = view.spaces.get(entry.get("namespace")) if entry and isinstance(entry.get("namespace"), str) else None
    if not isinstance(space, dict):
        case.add(MISSED, record_name("A2"), "artefacts[].namespace", f"{path} is not classed")
    elif space.get("embedding_policy") != NOT_EMBEDDED:
        case.add(MISHANDLED, PATH_MAP, "namespaces.embedding_policy", f"{path}'s namespace is embedded")
    elif view.index is not None and path not in view.index["semantic"]:
        case.add(FOUND, record_name("A2"), "artefacts[].namespace", f"{path} classed in a namespace not embedded, "
                 "and absent from the semantic vectors")


def _control(view, control):
    path, seen = control["paths"][0], []
    if not view.exists(path):
        seen.append({"record": path, "said": f"{path} is gone from the working tree"})
    for stage, key in (("A3", "action"),):
        record = view.records[stage]
        if record.state in ("UNREADABLE", "MALFORMED"):
            seen.append({"record": record.rel, "said": f"the record is {record.state}: it cannot show {path} clean"})
        entry = view.entry(stage, path)
        if entry and entry.get(key) in LEAVING:
            seen.append({"record": record.rel, "said": f"{path}: {entry[key]}"})
    record = view.records["A2"]
    if record.state in ("UNREADABLE", "MALFORMED"):
        seen.append({"record": record.rel, "said": f"the record is {record.state}: it cannot show {path} clean"})
    klass = _class_of(view, path)
    if klass in FLAGGING_CLASSES:
        seen.append({"record": record.rel, "said": f"{path} classed {klass}"})
    if view.ok("A8") and any(item.get("path") == path for item in view.records["A8"].data["retired"]):
        seen.append({"record": view.records["A8"].rel, "said": f"{path} retired"})
    documents = view.records["A8"].data.get("documents") if view.ok("A8") else None
    if isinstance(documents, list) and any(isinstance(d, dict) and d.get("path") == path for d in documents):
        seen.append({"record": view.records["A8"].rel, "said": f"{path} taken as a legacy document"})
    for record in view.findings:
        if record.state == "PRESENT" and (path in (record.data.get("paths") or []) or path in (
                record.data.get("path"), record.data.get("test"))):
            seen.append({"record": record.rel, "said": f"a finding names {path}"})
        elif record.state != "PRESENT":
            seen.append({"record": record.rel, "said": f"a finding is {record.state}: it cannot show {path} clean"})
    return {"id": control["id"], "kind": control["kind"], "status": FLAGGED if seen else CLEAN, "evidence": seen}


def judge_repository(manifest, root, beside=None, secrets=(), built=None):
    """The judgement of one repository's adoption outputs. ``secrets``: the builder's Held values."""
    manifest_form.validate(manifest)
    built = built_today() if built is None else set(built)
    view = _View(root, beside)
    verdict_record = view.records["VERDICT"]
    verdict = verdict_record.data.get("verdict") if verdict_record.state == "PRESENT" else None
    held = {h.form: h for h in secrets}
    planted = []
    for entry in manifest["planted"]:
        case, ev = _Case(entry), entry["evidence"]
        needs = NEEDS[entry["kind"]]
        absent = [c for c in needs if c not in built]
        not_built = absent if entry["kind"] in ALL_OF else (absent if len(absent) == len(needs) else [])
        for capability in not_built:
            contract, _, what = CAPABILITIES[capability]
            case.add(NOT_BUILT, None, capability, f"{capability} ({contract}): {what}")
        kind = entry["kind"]
        if kind == "stale-spec":
            _stale_spec(case, view, ev, built)
        elif kind == "superseded-plan":
            _superseded_plan(case, view, ev, built)
        elif kind == "misleading-name":
            _misleading_name(case, view, ev, entry["paths"][0], built)
        elif kind == "secret":
            _secret(case, view, ev, built, held.get(ev["form"]), verdict)
        elif kind == "orphaned-test":
            _orphaned_test(case, view, ev, built)
        elif kind == "legacy-document":
            _legacy_document(case, view, ev, built)
        elif kind == "large-file":
            _large_file(case, view, ev, built)
        planted.append(case.result())
    stages = {}
    for stage in STAGES:
        record = view.records[stage]
        if stage in ("A7", "A10", "VERDICT") and stage not in built:
            stages[stage] = {"status": NOT_BUILT, "record": record.rel, "capability": CAPABILITIES[stage][0]}
        else:
            stages[stage] = {"status": record.state, "record": record.rel}
    if "findings" not in built:
        stages["findings"] = {"status": NOT_BUILT, "record": FINDINGS, "capability": CAPABILITIES["findings"][0]}
    return {"repository": manifest["repository"], "seed": manifest["seed"], "planted": planted,
            "controls": [_control(view, c) for c in manifest["controls"]], "stages": stages,
            "not_built": sorted({s["field"] for p in planted for s in p["evidence"] if s["status"] == NOT_BUILT}
                                | {k for k, v in stages.items() if v["status"] == NOT_BUILT}),
            "adoption_verdict": verdict}


def overall(judgements, figures, expected):
    """READY only when every repository expected is judged, every planted problem is FOUND_AND_HANDLED, no control is
    FLAGGED, every stage is present (none NOT_BUILT), and both figures of every repository meet their floors."""
    reasons = []
    by_name = {j["repository"]: j for j in judgements}
    reasons += [f"{name}: not judged" for name in expected if name not in by_name]
    for j in judgements:
        name = j["repository"]
        reasons += [f"{name}: {p['id']} is {p['status']}" for p in j["planted"] if p["status"] != FOUND]
        reasons += [f"{name}: {c['id']} is FLAGGED" for c in j["controls"] if c["status"] != CLEAN]
        reasons += [f"{name}: stage {s} is {v['status']}" for s, v in j["stages"].items() if v["status"] != "PRESENT"]
        given = (figures or {}).get(name)
        for figure, floor in FLOORS.items():
            value = given.get(figure) if isinstance(given, dict) else None
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                reasons.append(f"{name}: the figure {figure} is missing (its floor is {floor:g})")
            elif value < floor:
                reasons.append(f"{name}: the figure {figure} is {value:g}, below its floor of {floor:g}")
    return {"verdict": NOT_READY if reasons else READY, "reasons": reasons, "repositories": judgements}


def judge(cases, figures, expected, built=None):
    """The whole judgement, failing closed: ``cases`` is a list of (manifest or its path, root, beside, secrets).

    Any error is an ERROR result, never READY; no secret value is ever in the result (checked in memory)."""
    held = [h for case in cases for h in case[3]]
    try:
        judgements = []
        for manifest, root, beside, secrets in cases:
            if not isinstance(manifest, dict):
                manifest = manifest_form.load(manifest)
            judgements.append(judge_repository(manifest, root, beside, secrets, built))
        result = overall(judgements, figures, expected)
        text = json.dumps(result, sort_keys=True)
    except Exception as exc:  # noqa: BLE001 - whatever stops the judge is an error, never a pass
        result = {"verdict": ERROR, "error": type(exc).__name__, "reasons": ["the judge could not judge"]}
        text = json.dumps(result)
    if any(h.found_in(text) for h in held):
        return {"verdict": ERROR, "error": "SecretInJudgement", "reasons": ["the judgement would hold a secret"]}
    return result
