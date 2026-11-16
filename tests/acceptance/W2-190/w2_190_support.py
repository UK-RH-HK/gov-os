"""Support code for the W2-190 acceptance tests: A3 refusing DELETE_FROM_ACTIVE_TREE of a referenced or superseded file.

Everything a case touches is planted under pytest's ``tmp_path``: a git repository of its own (the programme's repository
of W2-23's support, plus the documents below), a path map, and an empty ``HOME``. The tool is driven as an adopter drives
it: ``python -m gov.cli.main adopt --lite --stage A<n> ... --json`` as a child process whose ``PYTHONPATH`` is the
``src/`` of the repository this file stands in. Nothing of the implementation is imported.

This file *reuses W2-23's support by import* (``w2_23_support``: the planted project, the child's environment, the
``Adoption`` class, the envelope readers); it adds the W2-190 documents and a few readers of its own.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_W2_23 = HERE.parent / "W2-23"
if str(_W2_23) not in sys.path:
    sys.path.insert(0, str(_W2_23))

import w2_23_support as base  # noqa: E402  (W2-23's support: reused by import)

# What a refused proposal's envelope says. Every refusal of ``gov adopt`` carries the prefix ``ADOPT_`` (``refuse`` in
# ``gov.adopt.project``); the ticket writes the code without it, as it is written for A3's other refusals.
REFUSED = "ADOPT_PROPOSAL_REFUSED"
A3_RECORD = base.RECORD["A3"]
DELETE = "DELETE_FROM_ACTIVE_TREE"
REFERENCED_CODE, SUPERSEDED_CODE = "DELETE_REFERENCED", "DELETE_SUPERSEDED"

# --- S1 / S3 / F1: the plan of record 0003, named by 0007 and by an overview ------------------------------------------
OLD_PLAN = "docs/plans/0003-storage-migration.md"
NEW_PLAN = "docs/plans/0007-storage-migration.md"
OVERVIEW = "docs/specs/storage-overview.md"
UNREFERENCED = "docs/drop-1.txt"   # from W2-23's base project: no other tracked file names it, no record says superseded

# --- S2: records classed superseded (each is named by no other file's text, by path) ----------------------------------
SUPERSEDED_STATUS = "docs/records/old-rule.md"          # front matter status: SUPERSEDED
SUPERSEDED_LOWER = "docs/records/lower-rule.md"         # front matter status: superseded (any case)
EDGE_TARGET = "docs/records/active-rule.md"             # ACTIVE; a successor's ``supersedes: [<id>]`` names its id
EDGE_BY_TARGET = "docs/records/active-held-rule.md"     # ACTIVE; its own ``superseded_by: [<id>]`` names a successor

# --- F2: the scope of a mention ---------------------------------------------------------------------------------------
SELF = "docs/self-naming.md"                            # its own text names its own path
ADOPTION_ONLY = "docs/adoption-only.md"                 # named only by a file under governance/adoption/
MUTUAL_A, MUTUAL_B = "docs/mutual-a.md", "docs/mutual-b.md"
ROOT_X, DEEP_X = "x.md", "docs/a/x.md"                  # a root file, and one whose path ends in the same name
DEEP_X_HOLDER = "docs/a/readme-for-x.md"                # names DEEP_X only

NOTE_IN_ADOPTION = "governance/adoption/notes.md"


def record(record_id, status, body, **keys):
    """A Markdown record: front matter with the string keys ``id``, ``type`` and ``status`` the store requires."""
    head = {"id": record_id, "type": "note", "status": status, **keys}
    lines = ["---"] + [f"{key}: {json.dumps(value)}" for key, value in head.items()] + ["---", "", f"# {record_id}", "",
                                                                                         body, ""]
    return "\n".join(lines)


def documents():
    """The files the cases plant on top of W2-23's project. No file names a deletion target by path except where a
    line of the ticket says it does."""
    return {
        # S1: the successor names the old plan by its repository-relative path (the ticket's own sentence)
        OLD_PLAN: "# Plan 0003: storage migration\n\nMove the blobs of the upload bucket to the new store.\n",
        NEW_PLAN: ("# Plan 0007: storage migration\n\nThis plan supersedes plan 0003 (`docs/plans/0003-storage-migration.md`)."
                   "\nThe move runs in two steps.\n"),
        OVERVIEW: "# Storage overview\n\nThe first attempt is written down in docs/plans/0003-storage-migration.md.\n",
        # S2: records the store classes superseded; none is named by path, the successors name ids
        SUPERSEDED_STATUS: record("REC-OLD-1", "SUPERSEDED", "The amber quota rule, replaced long ago."),
        SUPERSEDED_LOWER: record("REC-LOW-4", "superseded", "The teal retention rule, replaced long ago."),
        EDGE_TARGET: record("REC-ACT-2", "ACTIVE", "The coral naming rule, still marked active."),
        "docs/records/active-rule-v2.md": record("REC-ACT-3", "ACTIVE", "The coral naming rule, second edition.",
                                                 supersedes=["REC-ACT-2"]),
        EDGE_BY_TARGET: record("REC-ACT-5", "ACTIVE", "The jade review rule, still marked active.",
                               superseded_by=["REC-ACT-6"]),
        "docs/records/active-held-rule-v2.md": record("REC-ACT-6", "ACTIVE", "The jade review rule, second edition."),
        # F2
        SELF: f"# Self-naming\n\nThis file is {SELF} and says so.\n",
        ADOPTION_ONLY: "# Adoption only\n\nA page nothing in the project mentions.\n",
        MUTUAL_A: f"# Mutual A\n\nSee {MUTUAL_B} for the other half.\n",
        MUTUAL_B: f"# Mutual B\n\nSee {MUTUAL_A} for the other half.\n",
        ROOT_X: "# x\n\nA file at the root.\n",
        DEEP_X: "# x, deeper\n\nA file of the same name, in a folder.\n",
        DEEP_X_HOLDER: f"# For x\n\nRead {DEEP_X} first.\n",
    }


PATTERNS = base.NAMESPACE_PATHS + ("*.md",)   # holds the root file by a glob: the path map must not spell ``x.md`` out


def assert_planted(root):
    """The planting's own check (a fault here is the case's, not the tool's): each deletion target is named by no other
    tracked file's text, except the ones S1 names on purpose; the suffix pair is named only as ``docs/a/x.md``."""
    root = Path(root)
    files = {rel: (root / rel).read_text(encoding="utf-8", errors="replace")
             for rel in base.git(root, "ls-files", "-z").split("\0") if rel and (root / rel).is_file()}
    deleted_targets = (SUPERSEDED_STATUS, SUPERSEDED_LOWER, EDGE_TARGET, EDGE_BY_TARGET, UNREFERENCED, ADOPTION_ONLY)
    for target in deleted_targets:
        named_by = [rel for rel, text in files.items() if rel != target and target in text]
        assert not named_by, f"planting fault: {target} is named by {named_by}"
    assert [rel for rel, text in files.items() if rel != SELF and SELF in text] == [], "planting fault: SELF"
    for target, only in ((MUTUAL_A, MUTUAL_B), (MUTUAL_B, MUTUAL_A)):
        named_by = [rel for rel, text in files.items() if rel != target and target in text]
        assert named_by == [only], f"planting fault: {target} is named by {named_by}"
    named_by = [rel for rel, text in files.items() if rel != OLD_PLAN and OLD_PLAN in text]
    assert sorted(named_by) == sorted([NEW_PLAN, OVERVIEW]), f"planting fault: {OLD_PLAN} is named by {named_by}"
    for rel, text in files.items():
        if rel != ROOT_X:
            assert ROOT_X not in text.replace(DEEP_X, ""), f"planting fault: {rel} names {ROOT_X} on its own"
    assert [rel for rel, text in files.items() if DEEP_X in text and rel != DEEP_X] == [DEEP_X_HOLDER], \
        "planting fault: the suffix pair"


def prepare(base_dir):
    """The planted project, committed, with A0, A1 and A2 run: what every case copies. Returns the project's path."""
    box = base.make_box(Path(base_dir) / "prepare-box")
    project = base.plant_project(Path(base_dir) / "project", extra=documents(), patterns=PATTERNS, ignored=False)
    assert_planted(project)
    adoption = base.Adoption(project, box)
    for stage in ("A0", "A1", "A2"):
        adoption.ok(stage)
    assert adoption.results["A2"].get("unknown") == [], \
        f"planting fault: A2 found unknown files {adoption.results['A2'].get('unknown')}"
    return project


def copy_of(prepared, destination):
    """A copy of the prepared repository (its git directory included) at ``destination``; the tool runs on the copy."""
    shutil.copytree(prepared, destination, symlinks=True)
    return Path(destination)


# --- running A3 and reading what it says ------------------------------------------------------------------------------

def propose(adoption, entries):
    """``gov adopt --lite --stage A3 --map <proposal>``: the finished child run (a refusal or a success)."""
    return adoption.run("A3", *adoption.map_argument(entries))


def problems_of(done):
    """The refusal's ``problems`` (one per refused path); the run must be PROPOSAL_REFUSED."""
    error = base.refusal(done, REFUSED)
    details = error.get("details")
    assert isinstance(details, dict) and isinstance(details.get("problems"), list) and details["problems"], \
        f"the refusal carries no list of problems in its details\n{done.describe()}"
    return details["problems"]


def problem_for(done, path):
    """The one problem whose ``path`` is ``path``, as text (``json.dumps``): no key name is assumed beyond ``path``."""
    found = [problem for problem in problems_of(done) if isinstance(problem, dict) and problem.get("path") == path]
    assert found, f"no problem for {path} among {problems_of(done)}\n{done.describe()}"
    return json.dumps(found, sort_keys=True)


def a3_record(root):
    """The committed A3 record's front matter (None where HEAD holds none)."""
    data = base.at_head(root, A3_RECORD)
    return None if data is None else base.frontmatter(data.decode("utf-8"), A3_RECORD)


def assert_no_a3_record(root, before_head, done=None):
    """A refused proposal writes and commits no A3 record: not in the folder, not at HEAD, HEAD where it was."""
    shown = done.describe() if done is not None else ""
    assert not (Path(root) / A3_RECORD).exists(), f"{A3_RECORD} is in the working tree\n{shown}"
    assert base.at_head(root, A3_RECORD) is None, f"{A3_RECORD} is committed at HEAD\n{shown}"
    assert base.head(root) == before_head, f"HEAD moved after the refusal\n{shown}"


def recorded(root, path):
    """The A3 record's entry for ``path`` (asserting the record exists and holds it)."""
    front = a3_record(root)
    assert front is not None, f"HEAD holds no {A3_RECORD}"
    held = [item for item in front["artefacts"] if item.get("path") == path]
    assert len(held) == 1, f"{A3_RECORD} holds {len(held)} entries for {path}"
    return held[0]


def accepted(done):
    """The run succeeded (exit 0, ``ok: true``): the stage's result."""
    return base.succeeded(done)
