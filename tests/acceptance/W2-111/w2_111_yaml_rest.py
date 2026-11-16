"""Support for P-W2-111-YAML-REST (a) as a described behaviour (DEC-136; brief td-8): the guard's other reads of YAML
answer as the pure-Python ``yaml.SafeLoader`` does; standard library and PyYAML only.

The behaviour: a ``role_paths:`` block of the path map, or a session ticket's front matter, that holds a tab inside or
after a plain value (or after ``key:``), a ``? `` inside a flow item, or a byte order mark after a line break is read as
the pure ``yaml.SafeLoader`` reads it. Where the pure loader refuses the text, the role-checked call decided from it is
refused (fail closed); where it reads it, the decision is the pure loader's. libyaml's ``CSafeLoader`` reads these texts
today, so a call is decided from data the pure parser would refuse.

The five reads (the CTO's count) and the interface each is reached by:

- ``gov.util.role_paths``: its ``role_paths:`` block read and its ticket front-matter read. The product's hook does not
  import this module: it is the role filter of ``gov retrieve`` and ``gov context`` (``role_paths.caller``, documented
  in the module as the caller's filter; a section or ticket that cannot be read raises ``RolePathsError`` and the
  search fails closed). The role-checked call is ``caller(root)`` with ``GOV_ROLE`` and ``GOV_TICKET`` set, run in a
  fresh interpreter on a planted repository; its answer is the refusal, or which probe paths it withholds.
- ``gov.util.parts``' ticket front-matter read: reached by the product's hook (W1-02's way of running it) when it works
  out an engineer's or a test designer's protected parts. The role-checked calls are an engineer's Read and a test
  designer's Read of an ordinary file of the planted project.
- the live hook's ``role_reads.py``, at both reads, in the patched copy (``w2_111_live_hook.make_copies``): run as
  settings.json's command runs it (the pinned interpreter, ``-E``) on a planted project. The applied copy uses libyaml
  at both reads, so it is not the oracle: the class texts must be refused by the patched copy, and the clean control
  decided alike by both.

The product's oracle is the same product code run with libyaml's binding absent (``sys.modules["yaml._yaml"] = None``
before PyYAML is imported: PyYAML then has no ``CSafeLoader`` and every loader is its pure-Python one). The case asserts
the product's answer equals the oracle's, and, for a class text, that it is a refusal.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

import yaml

import w2_111_live_hook as live
from w2_111_support import REPO_ROOT, guard

PATH_MAP_REL = "governance/project/path-map.yaml"
TICKET_ID = "DAEO-zz88"
WBS = "W2-988"
ORDINARY_REL = "docs/notes.md"
TESTS_REL = f"tests/acceptance/{WBS}/test_fixture.py"
IMPL_REL = "src/app/new.py"          # a file the ticket's allowed_paths name, new on the engineer's branch
ENG, TD = guard.ENGINEER, guard.TEST_DESIGNER

CLASSES = ("tab-inside-an-entry", "tab-after-an-entry", "tab-after-the-key", "question-in-a-flow-item",
           "bom-after-a-line-break")
CLEAN = "clean-control"
FRONT_IDS = CLASSES + (CLEAN,)
# A byte order mark after a line break stands at the start of its line, and the block reader ends the role_paths:
# block at the first line that does not start with a space, a tab, a # or a line break: neither parser ever sees it
# in the block. The class is placed in the front matter only.
BLOCK_IDS = tuple(c for c in FRONT_IDS if c != "bom-after-a-line-break")

# --------------------------------------------------------------------------------------------------------------------
# The texts
# --------------------------------------------------------------------------------------------------------------------

_TD_ENTRY = '  independent-test-designer:\n    reads_denied: ["{ticket_impl}"]\n'
BLOCKS = {
    # the repository's own form (governance/project/path-map.yaml), one more glob for the engineer
    CLEAN: 'role_paths:\n  engineer:\n    reads_denied: ["{ticket_tests}", docs/private/**]\n' + _TD_ENTRY,
    "tab-inside-an-entry":
        'role_paths:\n  engineer:\n    reads_denied:\n    - "{ticket_tests}"\n    - docs/private\tnotes/**\n'
        + _TD_ENTRY,
    "tab-after-an-entry":
        'role_paths:\n  engineer:\n    reads_denied:\n    - "{ticket_tests}"\n    - docs/private/**\t\n' + _TD_ENTRY,
    "tab-after-the-key":
        'role_paths:\n  engineer:\t\n    reads_denied: ["{ticket_tests}", docs/private/**]\n' + _TD_ENTRY,
    "question-in-a-flow-item":
        'role_paths:\n  engineer:\n    reads_denied: ["{ticket_tests}", docs/private? notes/**]\n' + _TD_ENTRY,
}

_TAGS = {
    CLEAN: "tags: [wave-2, guard]\n",
    "tab-inside-an-entry": "tags:\n- wave-2\n- guard\tfixture\n",
    "tab-after-an-entry": "tags:\n- wave-2\n- guard\t\n",
    "tab-after-the-key": "tags:\t[wave-2, guard]\n",
    "question-in-a-flow-item": "tags: [wave-2, guard? fixture]\n",
    "bom-after-a-line-break": "tags:\n﻿- guard\n",
}


def front_head(text_id, quoted_wbs=False):
    """The ticket's front matter (the YAML between its ``---`` lines), the class text on its ``tags`` line(s).
    ``quoted_wbs``: the WBS id quoted (a form the guard's own wbs_id pattern allows), so that the guard's line reader,
    taken when the YAML cannot be read, cannot read it: the pure loader's path then refuses (DEC-218's way)."""
    wbs = f"'{WBS}'" if quoted_wbs else WBS
    return (f"id: {TICKET_ID}\nstatus: in_progress\ndeps: []\nlinks: []\ntype: task\npriority: 1\n"
            f"assignee: engineer\nwbs_id: {wbs}\ntitle: YAML-REST fixture ticket\nclass: implementation\n"
            f"role: engineer\n{_TAGS[text_id]}allowed_paths:\n- src/app/**\n- docs/app/**\nprofile: FULL\n"
            f"acceptance_tests:\n  path: tests/acceptance/{WBS}/\n")


def ticket_file(head):
    return f"---\n{head}---\n# {WBS} YAML-REST fixture ticket\n"


def path_map(block):
    return f"# W2-111 planted path map (P-W2-111-YAML-REST)\nversion: 1\n{block}# the map goes on\n"


def pure_answer(text):
    """("data", value) or ("refused", the exception's type) from the pure-Python yaml.SafeLoader."""
    try:
        return ("data", yaml.load(text, Loader=yaml.SafeLoader))
    except yaml.YAMLError as exc:
        return ("refused", type(exc).__name__)


def libyaml_answer(text):
    """The same from libyaml's CSafeLoader; None when libyaml is not installed."""
    loader = getattr(yaml, "CSafeLoader", None)
    if loader is None:
        return None
    try:
        return ("data", yaml.load(text, Loader=loader))
    except yaml.YAMLError as exc:
        return ("refused", type(exc).__name__)


def write_exact(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))
    return path


# --------------------------------------------------------------------------------------------------------------------
# The planted repositories
# --------------------------------------------------------------------------------------------------------------------

def _commit_all(repo, message):
    guard.git(repo, "add", "-A")
    guard.git(repo, "commit", "-q", "-m", message)


def plant_repo(repo, block, head, extra=None):
    """A committed git repository holding the path map (``block``), the session ticket (``head``), an ordinary file,
    the ticket's acceptance test and ``extra`` files; on branch ``main``."""
    repo = Path(repo)
    files = {"README.md": "# W2-111 YAML-REST planted repository\n", ".gitignore": ".gov-runtime/\n__pycache__/\n",
             ORDINARY_REL: "notes\n", TESTS_REL: "VALUE = 1\n", "src/app/main.py": "VALUE = 1\n",
             **(extra or {})}
    for rel, text in files.items():
        write_exact(repo / rel, text)
    write_exact(repo / PATH_MAP_REL, path_map(block))
    write_exact(repo / ".tickets" / f"{TICKET_ID}.md", ticket_file(head))
    guard.git(repo, "init", "-q", "-b", "main")
    _commit_all(repo, "W2-111 YAML-REST planted repository")
    return repo


def plant_engineer_tree(home, block, head):
    """The engineer's tree, ``<home>/gov-os-worktrees/<WBS>``: a repository whose ``w2/integrate`` holds the base and
    whose branch ``w2/<WBS>`` adds ``IMPL_REL`` (inside the ticket's allowed_paths): the file the role filter withholds
    from the test designer searching that tree."""
    tree = Path(home) / "gov-os-worktrees" / WBS
    plant_repo(tree, block, head)
    guard.git(tree, "branch", "w2/integrate")
    guard.git(tree, "checkout", "-q", "-b", f"w2/{WBS}")
    write_exact(tree / IMPL_REL, "NEW = 1\n")
    _commit_all(tree, "the engineer's new code")
    return tree


# --------------------------------------------------------------------------------------------------------------------
# role_paths.caller, as gov retrieve calls it, in a fresh interpreter (the product, or the oracle)
# --------------------------------------------------------------------------------------------------------------------

NO_LIBYAML = 'import sys\nsys.modules["yaml._yaml"] = None  # libyaml\'s binding absent: PyYAML\'s pure loaders only\n'
CALLER = '''
import json, sys
from gov.util import role_paths
root, probes = sys.argv[1], json.loads(sys.argv[2])
try:
    f = role_paths.caller(root)
except role_paths.RolePathsError as exc:
    print(json.dumps(["refused", "RolePathsError", str(exc)]))
else:
    print(json.dumps(["filter", {p: (f is not None and f.denied(p) is not None) for p in probes}]))
'''


def caller_answer(root, role, home, scratch, probes, pure=False):
    """``role_paths.caller(root)`` for ``role`` on the planted ticket: ("refused", "RolePathsError", text), or
    ("filter", {probe: withheld}); ``pure``: with libyaml's binding absent (the oracle)."""
    scratch = Path(scratch)
    (scratch / "tmp").mkdir(parents=True, exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "HOME": str(home), "LANG": "C.UTF-8",
           "LC_ALL": "C.UTF-8", "TZ": "UTC", "TMPDIR": str(scratch / "tmp"), "PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONPATH": str(REPO_ROOT / "src"), "GOV_ROLE": role, "GOV_TICKET": TICKET_ID}
    code = (NO_LIBYAML if pure else "") + CALLER
    proc = subprocess.run([sys.executable, "-c", code, str(root), json.dumps(list(probes))], capture_output=True,
                          text=True, cwd=str(root), env=env, timeout=60, check=False)
    if proc.returncode != 0 or not proc.stdout.strip():
        return ("error", proc.returncode, (proc.stderr or proc.stdout).strip()[-400:])
    got = json.loads(proc.stdout.strip().splitlines()[-1])
    return tuple(got) if got[0] == "refused" else (got[0], got[1])


# --------------------------------------------------------------------------------------------------------------------
# The product's hook (W1-02's way), and its oracle: the same hook run with libyaml's binding absent
# --------------------------------------------------------------------------------------------------------------------

PURE_COPY = "w2_111_rest_product_pretooluse.py"
PURE_HOOK = '''#!/usr/bin/env python3
"""W2-111's oracle (P-W2-111-YAML-REST): the product hook, run from its copy beside this file with libyaml's binding
absent, so that PyYAML's loaders are its pure-Python ones (the hook's forked decision process inherits it)."""
import runpy
import sys

sys.modules["yaml._yaml"] = None
sys.argv[0] = {product!r}
runpy.run_path({product!r}, run_name="__main__")
'''


def product_project(base, head):
    """W1-02's fixture project with the session ticket ``head`` added (and the planted path map's clean block)."""
    project = guard.make_project(Path(base) / "project")
    write_exact(project / ".tickets" / f"{TICKET_ID}.md", ticket_file(head))
    write_exact(project / TESTS_REL, "VALUE = 1\n")
    _commit_all(project, "the YAML-REST ticket")
    return project


@contextmanager
def pure_hook(project):
    """Put the oracle in place of the product hook installed in ``project``; put it back after."""
    installed = Path(project) / guard.installed_hook_rel()
    product = installed.with_name(PURE_COPY)
    shutil.copy2(installed, product)
    original = installed.read_bytes()
    try:
        installed.write_text(PURE_HOOK.format(product=str(product)), encoding="utf-8")
        yield installed
    finally:
        installed.write_bytes(original)
        product.unlink()


def product_read(project, sandbox, role, rel):
    return guard.run_hook(project, "Read", {"file_path": str(Path(project) / rel)}, sandbox, role=role,
                          ticket=TICKET_ID)


# --------------------------------------------------------------------------------------------------------------------
# The live hook's copies, on a planted project
# --------------------------------------------------------------------------------------------------------------------

def run_live(interpreter, hook, project, home, scratch, role, file_path):
    """One Read of ``file_path`` by ``hook`` (a copy's pretooluse.py) as settings.json's command runs it, the role on
    the planted ticket; (decision, what the hook said)."""
    scratch = Path(scratch)
    for sub in ("tmp", "calls"):
        (scratch / sub).mkdir(parents=True, exist_ok=True)
    env = {"PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"), "HOME": str(home), "LANG": "C.UTF-8",
           "LC_ALL": "C.UTF-8", "TZ": "UTC", "TMPDIR": str(scratch / "tmp"), "CLAUDE_PROJECT_DIR": str(project),
           "PYTHONDONTWRITEBYTECODE": "1", "GOV_GUARD_CALLS_DIR": str(scratch / "calls"), "GOV_ROLE": role,
           "GOV_TICKET": TICKET_ID}
    payload = json.dumps({"session_id": "w2-111-yaml-rest", "cwd": str(project), "hook_event_name": "PreToolUse",
                          "tool_name": "Read", "tool_input": {"file_path": str(file_path)},
                          "permission_mode": "default", "tool_use_id": "toolu_w2_111_yaml_rest"})
    proc = subprocess.run(["sh", "-c", '"$0" -E "$1"', interpreter, str(hook)], input=payload, capture_output=True,
                          text=True, cwd=str(project), env=env, timeout=60, check=False)
    return guard.classify(proc.returncode, proc.stdout), (proc.stderr or proc.stdout).strip()[:300]


@dataclass
class LiveWorld:
    project: Path
    home: Path
    impl: Path       # a file under the engineer's tree that the ticket's allowed_paths name


def live_world(base, block, head):
    """A planted project (its path map's block and its session ticket) and a home whose ``gov-os-worktrees/<WBS>``
    holds a file the ticket's allowed_paths name (the test designer's {ticket_impl})."""
    base = Path(base)
    home = base / "home"
    project = plant_repo(base / "project", block, head)
    impl = write_exact(home / "gov-os-worktrees" / WBS / "src/app/main.py", "VALUE = 2\n")
    return LiveWorld(project, home, impl)


def make_live(base):
    """The applied and patched copies and the pinned interpreter; ``live.LiveHookUnavailable`` names what is
    missing."""
    return live.make_copies(Path(base) / "copies"), live.pinned_interpreter()
