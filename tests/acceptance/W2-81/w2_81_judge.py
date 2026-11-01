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
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import w2_81_manifest as manifest_form
from w2_81_secret import make_secret

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
# Where each kind's files must stay as built, and how each may leave (README, "Planted files stay as built"):
# "move" a MOVE or RENAME in A3 reviewed at A5 whose target holds the file as built; "retire" a RETIRE reviewed at A5;
# None never. A file that changes content, or leaves otherwise, is MISHANDLED.
# The configuration the test runners read in a test's parent folders. In the test's own folder no list is needed:
# every file there other than the test is held to the build's (``_collection_kept``).
_TEST_CONFIG = ("conftest.py", "pytest.ini", ".pytest.ini", "pytest.toml", ".pytest.toml", "pyproject.toml",
                "setup.cfg", "tox.ini", "noxfile.py", "package.json", "Cargo.toml", "build.rs", "go.mod", "go.work")
_TEST_CONFIG_PREFIXES = ("vitest.config", "vitest.workspace", "vitest.projects", "vite.config", "jest.config",
                         "tsconfig", "karma.conf", ".mocharc", "pytest.", ".pytest.")
NOT_MEASURED = {"large-file": "`within the budget`: no budget for the index is stated in the path map (its schema has "
                              "no such field), in the index's records or in the Contract, so the judge has none to "
                              "read; the clause is not measured today"}


def places(entry):
    """The files a planted problem's handling depends on, each with how it may leave its place."""
    kind, ev = entry["kind"], entry["evidence"]
    if kind == "stale-spec":
        return [(ev["stale"], "move"), (ev["governing"], "move")]
    if kind == "superseded-plan":
        return [(ev["plan"], None), (ev["successor"], "move")]
    if kind == "misleading-name":
        return [(entry["paths"][0], "move")]
    if kind == "secret":
        return [(ev["path"], "move")]
    if kind == "orphaned-test":
        return [(ev["test"], None)]
    if kind == "legacy-document":
        return [(ev["path"], "retire" if ev["handling"] == "retire" else "move")]
    if kind == "large-file":
        return [(ev["path"], "move")]
    return []


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


def blob_id(data):
    """Git's id of a blob holding ``data``: a file's content compared with the build's without reading git."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _git(root, *args, data=None):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, input=data,
                          env={"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(Path(root).parent),
                               "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    return done.returncode, done.stdout


def head_tree(root, head):
    """Path -> blob id of the build's HEAD, read from the adopted repository's git; None when it cannot be read."""
    code, out = _git(root, "ls-tree", "-r", "-z", f"{head}^{{commit}}")
    if code != 0:
        return None
    listed = {}
    for line in out.decode("utf-8", "surrogateescape").split("\0"):
        if line:
            meta, _, path = line.partition("\t")
            listed[path] = meta.split()[2]
    return listed


def adoption_history(root, head):
    """Every object the adoption added after the build's HEAD, on any ref or reflog: [(id, kind, bytes)], or None
    when the history cannot be read (it then rules nothing out)."""
    code, out = _git(root, "rev-list", "--objects", "--all", "--reflog", "--not", f"{head}^{{commit}}")
    if code != 0:
        return None
    ids = [line.split()[0] for line in out.decode("utf-8", "surrogateescape").splitlines() if line.strip()]
    if not ids:
        return []
    code, out = _git(root, "cat-file", "--batch", data=("\n".join(ids) + "\n").encode())
    if code != 0:
        return None
    objects, at = [], 0
    while at < len(out):
        end = out.index(b"\n", at)
        header = out[at:end].split()
        if len(header) != 3:
            return None
        size = int(header[2])
        objects.append((header[0].decode(), header[1].decode(), out[end + 1:end + 1 + size]))
        at = end + 1 + size + 1
    return objects


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

    def __init__(self, root, beside, head=None):
        self.root, self.beside, self.head = Path(root), beside, head
        self.records = {stage: read_record(root, record_name(stage), stage) for stage in STAGES}
        self.findings_state, self.findings = read_findings(root)
        self.spaces, self.map_why = read_path_map(root)
        self.index, self.index_why = read_index(root)
        self.built = head_tree(root, head) if head else None  # the build's HEAD: path -> blob id
        self._history = False

    def history(self):
        if self._history is False:
            self._history = adoption_history(self.root, self.head) if self.head else None
        return self._history

    def blob_of(self, path):
        """The blob id of the working tree's file, or None when there is none."""
        try:
            return blob_id((self.root / path).read_bytes()) if self.exists(path) else None
        except OSError:
            return None

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


def _in_place(case, view, path, leave):
    """MISHANDLED when ``path`` changed content, or left its place other than as ``leave`` allows (CAP-44.b to
    CAP-44.d, CAP-44.j): adoption proposes restructuring, it does not do it on its own."""
    if view.built is None:
        case.add(MISSED, path, None, "the build's history cannot be read in the adopted repository, so the file's "
                 "place and content cannot be compared with the build's")
        return
    original = view.built.get(path)
    if original is None:
        return  # not a file of the build's HEAD
    if view.exists(path):
        if view.blob_of(path) != original:
            case.add(MISHANDLED, path, None, f"{path} was changed in place: its content is not the build's")
        return
    entry = view.entry("A3", path)
    action = entry.get("action") if entry else None
    if leave == "move" and action in ("MOVE", "RENAME") and view.reviewed():
        target = entry.get("target")
        if isinstance(target, str) and view.blob_of(target) == original:
            return  # a governed batch reviewed at A5: allowed, but it is not the handling itself
        case.add(MISHANDLED, record_name("A3"), "artefacts[].target", f"{path} was moved by a reviewed action, "
                 "but its target does not hold it as built")
        return
    if leave == "retire" and action == "RETIRE" and view.reviewed():
        return
    case.add(MISHANDLED, path, None, f"{path} left its place without an action reviewed at A5 that allows it")


def _collection_kept(case, view, test):
    """MISHANDLED when a test-runner configuration file in the test's folder or above it is new, changed or gone:
    a test kept from being collected is skipped, whatever the form."""
    if view.built is None:
        return
    own = Path(test).parent
    folders = [own] + list(own.parents)

    def configuration(rel):
        name, parent = Path(rel).name, Path(rel).parent
        if parent == own:  # the test's own folder: any file but the test itself, whatever its name
            return rel != test
        return parent in folders and (name in _TEST_CONFIG or name.startswith(_TEST_CONFIG_PREFIXES))
    now = set()
    for folder in folders:
        here = view.root / folder
        if here.is_dir():
            now |= {(folder / p.name).as_posix() for p in here.iterdir() if p.is_file()}
    for rel in sorted({r for r in now | set(view.built) if configuration(r)}):
        if view.blob_of(rel) != view.built.get(rel):
            case.add(MISHANDLED, rel, None, f"the collection configuration {rel} of {test} is not the build's")


def reviewed_moves(root):
    """Path -> target of each MOVE or RENAME in A3 whose path map A5 reviewed (a forbidden citation follows it)."""
    view = _View(root, None)
    if not view.reviewed():
        return {}
    return {item["path"]: item["target"] for item in view.records["A3"].data["artefacts"]
            if item.get("action") in ("MOVE", "RENAME") and isinstance(item.get("target"), str)}


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
    entry = view.entry("A3", plan)
    if entry and entry.get("action") in LEAVING:
        case.add(MISHANDLED, record_name("A3"), "artefacts[].action", f"{plan}: {entry['action']}")
    following = view.entry("A3", successor)  # the current plan proposed out of the active tree (read today)
    if following and following.get("action") in ("DELETE_FROM_ACTIVE_TREE", "RETIRE"):
        case.add(MISHANDLED, record_name("A3"), "artefacts[].action", f"the successor {successor}: "
                 f"{following['action']}")
    if "A2-content-class" in built and not _missing_records(case, view, "A2"):
        a2 = view.entry("A2", plan) or {}
        if a2.get("class") == "superseded" and a2.get("superseded_by") == successor:
            case.add(FOUND, record_name("A2"), "artefacts[].superseded_by", f"{plan} linked to {successor}")
        elif a2.get("class") == "current":
            case.add(MISHANDLED, record_name("A2"), "artefacts[].class", f"{plan} classed current")
        if _class_of(view, successor) in FLAGGING_CLASSES:
            case.add(MISHANDLED, record_name("A2"), "artefacts[].class", f"the successor {successor} classed as "
                     "not current")


def _misleading_name(case, view, ev, path, built):
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
        history = view.history()
        if history is None:
            case.add(MISSED, "history", None, "the adoption's own commits cannot be read, so they rule nothing out")
        for object_id, kind, data in history or []:
            if held.found_in(data):
                case.add(MISHANDLED, f"history:{object_id[:12]}", kind, f"the value of the secret in {ev['path']} is "
                         "in a commit the adoption made (any ref or reflog after the build's HEAD)")
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
            if verdict is not None and verdict != "NOT_ADOPTED_HEALTHY":
                case.add(MISHANDLED, record_name("VERDICT"), "verdict", f"{verdict} while the secret's finding is "
                         "open, and no owner's acceptance of it by name is read (its record is NOT_BUILT, CAP-44.h)")


def _rel(path, view):
    for base in (view.root, Path(view.beside) if view.beside else None):
        if base is not None:
            try:
                return f"{'beside' if base != view.root else 'repository'}:{Path(path).relative_to(base).as_posix()}"
            except ValueError:
                pass
    return str(path)


def _orphaned_test(case, view, ev, built):
    test = ev["test"]  # its place and content are held to the build's (places); so is its collection
    _collection_kept(case, view, test)
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


def moved_to(view, path):
    """Where ``path`` now is when a MOVE or RENAME in A3, reviewed at A5, took it there and its target holds it as
    built; None otherwise (a file in its place, or one that left without such an action)."""
    if view.built is None or view.exists(path) or not view.built.get(path):
        return None
    entry = view.entry("A3", path)
    if not entry or entry.get("action") not in ("MOVE", "RENAME") or not view.reviewed():
        return None
    target = entry.get("target")
    return target if isinstance(target, str) and view.blob_of(target) == view.built[path] else None


def namespace_by_patterns(view, path):
    """The namespace the path map's patterns give ``path`` now, as the adoption tool classes (the code under test's
    own matcher); None when none holds it or the path map cannot be read."""
    if not isinstance(view.spaces, dict):
        return None
    from gov.adopt.project import classify

    try:
        return classify({"path-map.yaml": {"namespaces": view.spaces}}, [path]).get(path)
    except Exception:  # noqa: BLE001 - a path map the matcher refuses holds nothing
        return None


def _large_file(case, view, ev, built):
    """Kept out of the semantic index where the file now is: at its place, or at the target of a reviewed move."""
    path = ev["path"]
    if _missing_records(case, view, "A2"):
        return
    target = moved_to(view, path)
    where = target or path
    moved = f" (moved there from {path} by a reviewed action)" if target else ""
    if view.index is None:
        case.add(MISSED, STORE, None, f"the index is {view.index_why}")
    elif where in view.index["semantic"]:
        case.add(MISHANDLED, STORE, "semantic_vector", f"{where} is in the semantic index{moved}")
    if view.spaces is None:
        case.add(MISSED, PATH_MAP, None, f"the path map is {view.map_why}")
        return
    if target:  # the record of where it was no longer says where it is: the path map's patterns do
        name, field_read = namespace_by_patterns(view, target), "namespaces.paths"
    else:
        entry = view.entry("A2", path)
        name, field_read = (entry.get("namespace") if entry else None), "artefacts[].namespace"
    space = view.spaces.get(name) if isinstance(name, str) else None
    if not isinstance(space, dict):
        case.add(MISSED, PATH_MAP if target else record_name("A2"), field_read, f"{where} is not classed{moved}")
    elif space.get("embedding_policy") != NOT_EMBEDDED:
        case.add(MISHANDLED, PATH_MAP, "namespaces.embedding_policy", f"{where}'s namespace `{name}` is "
                 f"embedded{moved}")
    elif view.index is not None and where not in view.index["semantic"]:
        lexical = "in" if where in view.index["lexical"] else "not in"
        case.add(FOUND, PATH_MAP if target else record_name("A2"), field_read, f"{where} classed in a namespace not "
                 f"embedded, absent from the semantic vectors, {lexical} the lexical index{moved}")


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
    if view.ok("A2"):
        entry = view.entry("A2", path)
        space = entry.get("namespace") if entry else None
        if not isinstance(space, str) or view.spaces is None or space not in view.spaces:
            seen.append({"record": record.rel, "said": f"{path} is mapped to no namespace the path map holds"})
    if view.index is not None and path not in view.index["lexical"]:
        seen.append({"record": STORE, "said": f"{path} is left out of the index"})
    if view.built is not None and view.built.get(path) and view.exists(path) \
            and view.blob_of(path) != view.built[path]:
        seen.append({"record": path, "said": f"{path} was changed in place"})
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
    view = _View(root, beside, manifest["head"])
    verdict_record = view.records["VERDICT"]
    verdict = verdict_record.data.get("verdict") if verdict_record.state == "PRESENT" else None
    secrets = list(secrets)
    planted = []
    for entry in manifest["planted"]:
        case, ev = _Case(entry), entry["evidence"]
        for path, leave in places(entry):
            _in_place(case, view, path, leave)
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
            _secret(case, view, ev, built, own_value(manifest, entry, secrets), verdict)
        elif kind == "orphaned-test":
            _orphaned_test(case, view, ev, built)
        elif kind == "legacy-document":
            _legacy_document(case, view, ev, built)
        elif kind == "large-file":
            _large_file(case, view, ev, built)
        planted.append(_public(entry, case.result()))
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
            "not_measured": sorted({f"{e['kind']}: {NOT_MEASURED[e['kind']]}" for e in manifest["planted"]
                                    if e["kind"] in NOT_MEASURED}),
            "adoption_verdict": verdict}


def _public(entry, result):
    """A hidden variant's result names it by its number and id only: its kind, variant name, paths and texts are the
    hidden half's, so its evidence keeps each status (and a capability not built) and withholds the rest."""
    if not entry.get("hidden"):
        return result
    label = f"hidden variant #{entry.get('number', '?')} ({entry.get('hidden_id', '?')})"
    return {"id": label, "kind": "hidden", "variant": "hidden", "status": result["status"],
            "evidence": [{"status": s["status"], "record": None,
                          "field": s["field"] if s["status"] == NOT_BUILT else None,
                          "said": "withheld: a hidden variant"} for s in result["evidence"]]}


def own_value(manifest, entry, secrets):
    """The held value of this planted secret, among ``secrets``: each secret is checked against its own value only."""
    ev = entry["evidence"]
    mine = make_secret(ev["form"], manifest["seed"], ev.get("salt", manifest["repository"]))
    return next((held for held in secrets if held == mine), None)


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
