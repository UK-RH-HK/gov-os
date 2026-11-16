"""Support code for the W2-192 acceptance tests: adoption stage AS, the spec audit (``gov adopt --lite --stage AS``).

Everything a case touches is planted under pytest's ``tmp_path``: a git repository of its own (W2-23's programme
repository without its loose ``lib/`` and ``scripts/`` code, plus the specs, the tickets and the code below), a path map,
and an empty ``HOME``. The tool is driven as an adopter drives it: ``python -m gov.cli.main adopt --lite --stage ... --json``
as a child process whose ``PYTHONPATH`` is the ``src/`` of the repository this file stands in. Nothing of the
implementation is imported (the ``STAGES`` case reads the command module in a child process too).

This file *reuses W2-23's support by import* (``w2_23_support``: the child's environment, the ``Adoption`` class, the
envelope readers, git), as W2-190's support does, and adds the W2-192 project and readers.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
_W2_23 = HERE.parent / "W2-23"
if str(_W2_23) not in sys.path:
    sys.path.insert(0, str(_W2_23))

import w2_23_support as base  # noqa: E402  (W2-23's support: reused by import)

AS_RECORD = f"{base.ADOPTION}/AS-spec-audit.md"
A3_RECORD = base.RECORD["A3"]
FOLDER = base.ADOPTION

# Codes the stage chain and A3 already give; the lite checks' refusal is none of these (the lead's brief: "not pinned").
NOT_THE_LITE_CHECKS = ("ADOPT_STAGE_MISSING", "ADOPT_CHAIN_BROKEN", "ADOPT_PROPOSAL_REFUSED", "ADOPT_TREE_NOT_CLEAN")

# --- the planted specs (Markdown under specs/, front matter type/title/wave/status) -------------------------------------
ALPHA, BETA, OMEGA = "specs/alpha.md", "specs/beta.md", "specs/omega.md"
SPECS = {   # path -> (id, title, wave, status, the code paths its text names, in backticks)
    ALPHA: ("SPEC-ALPHA", "Alpha harbour ledger", 1, "accepted", ("src/alpha.py",)),
    BETA: ("SPEC-BETA", "Beta berth planner", 2, "draft", ("src/beta.py", "src/beta_extra.py")),
    OMEGA: ("SPEC-OMEGA", "Omega tide forecaster", 3, "proposed", ("src/omega.py",)),
}
BUILT = {ALPHA: "built", BETA: "partly built", OMEGA: "not built"}

# --- the planted code: tracked modules directly under src/ (flat), and one test file ------------------------------------
ALPHA_PY, BETA_PY, GAMMA_PY = "src/alpha.py", "src/beta.py", "src/gamma.py"
BETA_EXTRA_PY, OMEGA_PY = "src/beta_extra.py", "src/omega.py"      # named by a spec, never created: not tracked
TEST_ALPHA = "tests/test_alpha.py"
MODULES = {ALPHA_PY, BETA_PY, GAMMA_PY}
CODE = {
    ALPHA_PY: "VALUE = 1\n\n\ndef ledger():\n    return VALUE\n",
    BETA_PY: "def plan():\n    return ['berth-1']\n",
    GAMMA_PY: "def idle():\n    return None\n",
    TEST_ALPHA: ('"""Tests of src/alpha.py."""\nimport sys\n\nsys.path.insert(0, "src")\nimport alpha\n\n\n'
                 "def test_ledger():\n    assert alpha.ledger() == 1\n"),
}

# --- the planted tickets ------------------------------------------------------------------------------------------------
TICKETS = {"FIX-aa01": ("closed", 1), "FIX-bb02": ("open", 2)}   # id -> (status, wave)

GAPS = {BETA: "partly built", OMEGA: "not built", GAMMA_PY: "module no spec names"}   # subject -> why (the fixture's)


def spec_text(path):
    ident, title, wave, status, code = SPECS[path]
    head = {"id": ident, "type": "spec", "title": title, "wave": wave, "status": status}
    names = "\n".join(f"- `{rel}`" for rel in code)
    return ("---\n" + yaml.safe_dump(head, sort_keys=False) + f"---\n\n# {title}\n\nThis spec is built in:\n\n{names}\n")


def ticket_text(ident, status, wave):
    head = {"id": ident, "status": status, "type": "task", "wave": wave, "tags": [f"wave-{wave}"]}
    return "---\n" + yaml.safe_dump(head, sort_keys=False, default_flow_style=None) + f"---\n\n# {ident}\n\nA ticket of wave {wave}.\n"


def path_map_text():
    """Every tracked file of the project is held by a namespace; each states ``embedding_policy`` exactly; one embeds."""
    document = base.path_map(base.NAMESPACE_PATHS)
    spaces = document["namespaces"]
    spaces["specs"] = base.namespace(("specs/**",))
    spaces["tickets"] = base.namespace((".tickets/**",))
    spaces["code"] = {**base.namespace(("src/**",)), "embedding_policy": "not embedded"}
    spaces["tests"] = {**base.namespace(("tests/**",)), "embedding_policy": "not embedded"}
    return yaml.safe_dump(document, sort_keys=False)


def first_files():
    files = {base.PATH_MAP_REL: path_map_text()}
    files.update({path: spec_text(path) for path in SPECS})
    files.update({f".tickets/{ident}.md": ticket_text(ident, status, wave) for ident, (status, wave) in TICKETS.items()})
    return files


def plant(root):
    """The project: a first commit (programme files, path map, specs, tickets) and a second that holds only the code."""
    root = Path(root)
    base.plant_project(root, extra=first_files(), without=("lib/__init__.py", "lib/util.py", "scripts/run.py"),
                       ignored=False)
    for rel, text in CODE.items():
        base.write(root, rel, text)
    base.commit_all(root, "the code: three modules and the test of one")
    return root


def prepare(base_dir):
    """The planted project with A0, A1 and A2 run: what every case copies. Returns the project's path."""
    box = base.make_box(Path(base_dir) / "prepare-box")
    project = plant(Path(base_dir) / "project")
    adoption = base.Adoption(project, box)
    for stage in ("A0", "A1", "A2"):
        adoption.ok(stage)
    assert adoption.results["A2"].get("unknown") == [], \
        f"planting fault: A2 found unknown files {adoption.results['A2'].get('unknown')}"
    assert not base.porcelain(project), "planting fault: the prepared project is not clean"
    return project


def copy_of(prepared, destination):
    import shutil
    shutil.copytree(prepared, destination, symlinks=True)
    return Path(destination)


def snapshot(root):
    """Everything outside ``.git/`` and outside ``governance/adoption/``: path -> sha256 of the bytes ('<dir>' for a
    folder, 'link:<target>' for a symlink), tracked or not, ignored or not. A byte comparison of two of these is F1's."""
    root, found = Path(root), {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if rel == ".git" or rel.startswith(".git/") or rel == FOLDER or rel.startswith(FOLDER + "/"):
            continue
        if path.is_symlink():
            found[rel] = "link:" + str(path.readlink())
        elif path.is_dir():
            found[rel] = "<dir>"
        else:
            found[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return found


def tracked_outside(root, rev="HEAD"):
    """Path -> blob id of every file of ``rev`` outside ``governance/adoption/``."""
    listed = {}
    for line in base.git(root, "ls-tree", "-r", "-z", rev).split("\0"):
        if line:
            meta, _, path = line.partition("\t")
            if not path.startswith(FOLDER + "/"):
                listed[path] = meta.split()[2]
    return listed


def drift(before, after):
    return sorted(rel for rel in set(before) | set(after) if before.get(rel) != after.get(rel))


# --- running the stages -------------------------------------------------------------------------------------------------

@dataclass
class Audited:
    """A copy of the prepared project on which ``--stage AS`` was run once (its outcome is not asserted here)."""
    root: Path
    box: object
    done: object
    head_before: str
    snapshot_before: dict
    tracked_before: dict


def run_as(prepared, base_dir):
    base_dir = Path(base_dir)
    root = copy_of(prepared, base_dir / "project")
    box = base.make_box(base_dir / "box")
    before = (base.head(root), snapshot(root), tracked_outside(root))
    done = base.Adoption(root, box).run("AS")
    return Audited(root, box, done, *before)


def audit_ok(audited):
    """The AS run succeeded; the stage's result."""
    return base.succeeded(audited.done)


def as_ran(adoption):
    """The AS run that ``after_as`` carries on succeeded; the stage's result."""
    return base.succeeded(adoption.as_done)


def a3_keep_all(adoption):
    """``--stage A3`` with the all-KEEP proposal (``artefacts: []``): the finished child run."""
    return adoption.run("A3", *adoption.map_argument([]))


def front_of(root, rel):
    """The committed record's front matter (None where HEAD holds none)."""
    data = base.at_head(root, rel)
    return None if data is None else base.frontmatter(data.decode("utf-8"), rel)


def as_front(root):
    """The committed AS record's front matter; the case fails here when HEAD holds none."""
    front = front_of(root, AS_RECORD)
    assert front is not None, f"HEAD holds no {AS_RECORD}"
    return front


def assert_no_record(root, rel, head_before, done=None):
    """A refusal writes and commits no record at ``rel``: not in the tree, not at HEAD, HEAD where it was."""
    shown = done.describe() if done is not None else ""
    assert not (Path(root) / rel).exists(), f"{rel} is in the working tree\n{shown}"
    assert base.at_head(root, rel) is None, f"{rel} is committed at HEAD\n{shown}"
    assert base.head(root) == head_before, f"HEAD moved after the refusal\n{shown}"


def said(error):
    """What a refusal says: its code, message and details, as one text."""
    return " ".join([str(error.get("code")), str(error.get("message")), json.dumps(error.get("details"), default=str)])


def names_stage(error, stage):
    """The refusal names ``stage`` (the word, in its message or its details)."""
    return re.search(rf"\b{re.escape(stage)}\b", said(error)) is not None


def rewrite_record(adoption, mutate, message="the owner's edit of the AS record"):
    """Read the committed AS record (AS must have run), let ``mutate`` change its front matter, commit it with a plain git
    commit. Returns the text written (the case checks its own planting against it)."""
    as_ran(adoption)
    root = adoption.root
    front = as_front(root)
    mutate(front)
    text = ("---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=120)
            + "---\n\n# ADOPT-AS: spec audit\n\nRewritten by the W2-192 tests.\n")
    base.write(root, AS_RECORD, text)
    base.commit_all(root, message)
    return text


def by_path(entries, key="path"):
    return {item[key]: item for item in entries if isinstance(item, dict) and key in item}


def stages_of_command(box, cwd):
    """``gov.adopt.command.STAGES`` as a child process of the adopter's environment reads it (the tree's own ``src``)."""
    done = subprocess.run([sys.executable, "-c", "import json; from gov.adopt.command import STAGES; "
                                                  "print(json.dumps(list(STAGES)))"],
                          cwd=str(cwd), env=base.environment(box), capture_output=True, text=True, timeout=120,
                          stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"reading gov.adopt.command.STAGES failed\n{done.stderr}"
    return json.loads(done.stdout.strip().splitlines()[-1])
