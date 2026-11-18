"""Support code for W2-193's and W2-194's acceptance tests: gov close in an adopted repository (README, "How the
suite runs").

- **Public interfaces only:** ``gov close <ticket> --json [--base <rev>]`` (W1-07's console-script stand-in, this
  worktree's ``src/``, with no model: W2-115's ``quiet_env``), the close record ``docs/close/<ticket>/CL-<ticket>.md``,
  the ticket's status, the repair tickets in ``.tickets/``, and the refusal's text.
- **Planted projects under pytest's tmp_path**, W2-115's ``Smart`` projects (its ``w2_115_support``) with what an
  adopted repository adds: a legacy suite and its kit copy (same module names, a ``conftest.py`` each that the
  modules import by name, no ``__init__.py``), a ticket suite with its own ``conftest.py``, a test that exists only
  when its folder is collected whole, the path map's ``accepted_reds`` and the register they name.
- **Telling tests:** every planted test appends one JSON line per run (and, where it is planted so, one per import)
  to a file of its own outside the project: the widget's text it saw (``CHANGED`` on the change's side), whether it
  passed, its own process id and its pytest run's (the controller's when it runs in an xdist worker).
- Deterministic, no network, no model.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
_W2_115 = str(_HERE.parent / "W2-115")
if _W2_115 not in sys.path:
    sys.path.insert(0, _W2_115)

import w2_115_support as smart  # noqa: E402

close_support = smart.close_support
cli_support = smart.cli_support

# --------------------------------------------------------------------------
# The interface (README, "Interface")
# --------------------------------------------------------------------------

RED_CAUSED = "RED_CAUSED"
BASELINE_MISSING = "BASELINE_MISSING"
BASE_UNKNOWN = "BASE_UNKNOWN"
BASE_AMBIGUOUS = "BASE_AMBIGUOUS"
FROM_GIVEN, FROM_GREEN, FROM_TICKET = "given", "green_record", "ticket"
BASE_RUN_KEYS = ("ran", "commit", "passed", "failed", "errors", "skipped", "complete")

TICKET, WBS = smart.TICKET, smart.WBS
WIDGET = smart.WIDGET
OWN = smart.suite_of(WBS)                                   # the ticket's own suite
LEGACY = "governance/scripts/tests"                         # EXAMIN's legacy suite
KIT = "governance/framework/kit/governance/scripts/tests"   # its kit copy
BB = smart.suite_of("W2-bb")                                # reached by the widget change (allowed paths overlap)
REGISTER_REL = smart.REGISTER_REL
PATH_MAP_REL = smart.PATH_MAP_REL

# --------------------------------------------------------------------------
# Telling tests
# --------------------------------------------------------------------------

PASS = "    _tell(True)\n"
KNOWN_RED = "    _tell(False)\n    assert False, 'a known red'\n"
NOT_BROKEN = "    ok = 'BROKEN' not in widget\n    _tell(ok)\n    assert ok, 'the widget is broken'\n"
FIXED_BY_CHANGE = "    ok = 'FIXED' in widget\n    _tell(ok)\n    assert ok, 'the widget is not fixed yet'\n"
TYPE_FLIP = ("    _tell(False)\n    if 'CHANGED' in widget:\n"
             "        raise ZeroDivisionError('another failure on the changed widget')\n"
             "    assert False, 'a known red'\n")
TYPE_FLIP_TO_KEY = ("    _tell(False)\n    if 'CHANGED' in widget:\n"
                    "        raise KeyError('another failure on the changed widget')\n"
                    "    assert False, 'a known red'\n")
USES_BUILD_TREE = "    tree = build_tree({label!r})\n    _tell(tree.get('name') == {label!r})\n"
USES_BUILD_TREE_RED = ("    tree = build_tree({label!r})\n    _tell(False)\n"
                       "    assert tree is None, 'a known red of the suite'\n")

# An import that fails always, or only on the widget the change broke.
FAILS_TO_IMPORT = "import a_module_that_does_not_exist_w2_193  # noqa: F401\n"
FAILS_TO_IMPORT_WHEN_BROKEN = ("if 'BROKEN' in _widget():\n"
                               "    import a_module_that_does_not_exist_w2_193  # noqa: F401\n")


REACHED_BY_THE_WIDGET = ("try:\n    import gov.widget.thing  # noqa: F401  (the widget change reaches this test)\n"
                         "except ImportError:\n    pass\n")


def telling(rel, label, told, body=PASS, *, name=None, before="", args="", at_import=None, reached=False):
    """The text of a test file at ``rel`` with one test ``name`` (default ``test_<label>``) whose runs append a JSON
    line to ``told/<label>``. ``before`` is put first (``from conftest import build_tree``); ``args`` are the test's
    arguments; ``at_import`` is module-level code run after one line is told with ``phase: import``; ``reached``
    makes the module import the widget, so the scoped selection reaches it (its import rule)."""
    depth = rel.count("/")
    name = name or "test_" + re.sub(r"\W", "_", label)
    text = (
        f"{before}"
        f"{REACHED_BY_THE_WIDGET if reached else ''}"
        "import json\nimport os\nfrom pathlib import Path\n\n"
        f"ROOT = Path(__file__).resolve().parents[{depth}]\n"
        f"WIDGET = ROOT / {WIDGET!r}\n\n\n"
        "def _widget():\n"
        "    return WIDGET.read_text(encoding='utf-8') if WIDGET.is_file() else ''\n\n\n"
        "def _tell(ok, phase='call'):\n"
        "    run = os.getppid() if os.environ.get('PYTEST_XDIST_WORKER') else os.getpid()\n"
        f"    with open(os.path.join({str(told)!r}, {label!r}), 'a', encoding='utf-8') as out:\n"
        "        out.write(json.dumps({'root': str(ROOT), 'widget': _widget(), 'ok': ok, 'phase': phase,\n"
        "                              'pid': os.getpid(), 'run_pid': run}) + '\\n')\n\n\n"
    )
    if at_import is not None:
        text += f"_tell(False, 'import')\n{at_import}\n\n"
    return text + f"def {name}({args}):\n    widget = _widget()\n{body}"


def told_runs(told, label):
    path = Path(told) / label
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def head_side(runs):
    """Runs on a tree that holds the ticket's change (the widget says CHANGED)."""
    return [r for r in runs if "CHANGED" in (r.get("widget") or "")]


def base_side(runs):
    return [r for r in runs if "CHANGED" not in (r.get("widget") or "")]


def calls(runs):
    return [r for r in runs if r.get("phase") == "call"]


# --------------------------------------------------------------------------
# The adopted repository's suites
# --------------------------------------------------------------------------

def conftest_text(suite):
    """A suite's ``conftest.py`` with the helper its modules import by name (EXAMIN's ``build_tree``)."""
    return ("def build_tree(name):\n"
            f"    return {{'name': name, 'suite': {suite!r}}}\n")


OWN_CONFTEST = ("import pytest\n\n\n@pytest.fixture()\ndef ticket_fixture():\n"
                "    return 'the ticket suite\\'s own conftest, without build_tree'\n")


def suite_files(folder, prefix, told, modules, conftest=True, imports_conftest=True):
    """The files of a suite folder (no ``__init__.py``): its ``conftest.py`` (when ``conftest``) and one test module
    per ``{stem: body}`` (``test_<stem>.py``, test ``test_<stem>``, told as ``<prefix>-<stem>``); each module imports
    ``build_tree`` from ``conftest`` by name when ``imports_conftest``. A body ``("import", code)`` is a module that
    runs ``code`` at import (a collection error when it raises), with a passing test. Each module imports the
    widget: the scoped selection reaches the suites outside ``tests/`` by its import rule (a coupling may name only a
    target under ``tests/``, the test map's schema)."""
    files = {}
    if conftest:
        files[f"{folder}/conftest.py"] = conftest_text(prefix)
    for stem, body in modules.items():
        rel = f"{folder}/test_{stem}.py"
        before = "from conftest import build_tree  # noqa: E402  (EXAMIN's form)\n" if imports_conftest else ""
        label = f"{prefix}-{stem}"
        if isinstance(body, tuple):
            files[rel] = telling(rel, label, told, PASS, name=f"test_{stem}", before=before, at_import=body[1],
                                 reached=True)
        else:
            files[rel] = telling(rel, label, told, body.format(label=label), name=f"test_{stem}", before=before,
                                 reached=True)
    return files


def node(folder, stem, name=None):
    return f"{folder}/test_{stem}.py::{name or 'test_' + stem}"


def module_file(folder, stem):
    return f"{folder}/test_{stem}.py"


# A test that exists only when its folder is collected whole: its parameter's id is ``whole`` when a target of the
# pytest run is its folder or a folder above it, ``part`` otherwise (its file, or its node id, alone). Run alone by
# the node id the full run gave (``...[whole]``), pytest finds nothing (exit 4): the alone run is ``absent``.
WHOLE_CONFTEST = (
    "from pathlib import Path\n\n"
    "HERE = Path(__file__).resolve().parent\n\n\n"
    "def _whole(config):\n"
    "    for arg in config.args:\n"
    "        path = Path(config.invocation_params.dir, str(arg).split('::')[0]).resolve()\n"
    "        if path.is_dir() and (path == HERE or path in HERE.parents):\n"
    "            return True\n"
    "    return False\n\n\n"
    "def pytest_generate_tests(metafunc):\n"
    "    if 'collected_whole' in metafunc.fixturenames:\n"
    "        metafunc.parametrize('collected_whole', ['whole' if _whole(metafunc.config) else 'part'])\n"
)
WHOLE_FOLDER = "tests/acceptance/W2-bb/whole"


def whole_files(told, tests, folder=WHOLE_FOLDER):
    """The folder ``folder`` with ``WHOLE_CONFTEST`` and one test per ``{stem: body}`` taking ``collected_whole``."""
    files = {f"{folder}/conftest.py": WHOLE_CONFTEST}
    for stem, body in tests.items():
        rel = f"{folder}/test_{stem}.py"
        files[rel] = telling(rel, stem, told, body, name=f"test_{stem}", args="collected_whole")
    return files


def whole_node(stem, folder=WHOLE_FOLDER):
    return f"{folder}/test_{stem}.py::test_{stem}[whole]"


# --------------------------------------------------------------------------
# The planted project
# --------------------------------------------------------------------------

def test_map(*couplings, **keys):
    """W2-115's test map, with more couplings ``(paths, suites)``."""
    data = json.loads(json.dumps(smart.DEFAULT_TEST_MAP))
    for paths, suites in couplings:
        data["couplings"].append({"paths": list(paths), "suites": list(suites), "why": "planted by W2-193's tests"})
    data.update(keys)
    return data


ADOPTED_MAP = test_map()


def project(base, name="project", *, files=None, nightly=None, test_map=ADOPTED_MAP, workers=2, path_map=None):
    """A planted project (W2-115's ``Smart``): ``close: scoped``, every file of ``files`` in its initial commit,
    no nightly record unless ``nightly`` says so, ``close_workers`` set to ``workers``."""
    told = Path(base) / f"{name}-told"
    keys = {"close_workers": workers, **(path_map or {})}
    made = smart.Smart(Path(base) / name, told, nightly=nightly, test_map=test_map, files=files or {}, path_map=keys)
    return made


def own_suite_files(told, conftest=True):
    """The ticket's own suite as an adopted ticket's: its telling test, and its own ``conftest.py``."""
    rel = smart.file_of(WBS)
    files = {rel: telling(rel, "own-aa", told, PASS, name=smart.case_of(WBS))}
    if conftest:
        files[f"{OWN}/conftest.py"] = OWN_CONFTEST
    return files


def work(made, files=None, text="# the widget, CHANGED\n"):
    """The ticket's own trailered commit: the widget changed (``text``) and ``files``."""
    return made.work({WIDGET: text, **(files or {})})


def remove(made, *rels):
    for rel in rels:
        (made.root / rel).unlink()


def owner_commit(made, files, message="the owner's commit"):
    for rel, text in files.items():
        made.write(rel, text)
    return made._commit(message, close_support.OWNER, ("Task: setup", "Role: owner"))


def orchestrator_commit(made, files, message="the orchestrator's commit"):
    for rel, text in files.items():
        made.write(rel, text)
    return made._commit(message, close_support.ORCHESTRATOR, ("Task: setup", "Role: orchestrator"))


def close(made, sandbox, *args):
    """``gov close <ticket> --json [args]``, after loading the record store (W2-115's ``Smart.close``)."""
    close_support.load_store(made, sandbox, check=False)
    return made.gov(sandbox, "close", TICKET, "--json", *args)


def sandbox_at(base):
    return cli_support.make_sandbox(Path(base) / "sandbox")


def tickets(made):
    return made.tickets()


def parent(made, commit):
    return made.git("rev-parse", f"{commit}^").strip()


# --------------------------------------------------------------------------
# Reading what the close says
# --------------------------------------------------------------------------

passed = smart.passed
assert_refused = smart.assert_refused
refusal_text = smart.refusal_text


def record(made):
    return made.record()


def has_record(made):
    return (made.root / "docs" / "close" / TICKET / f"CL-{TICKET}.md").is_file()


def reds_of(front):
    reds = front.get("reds")
    assert isinstance(reds, list), f"the close record holds no reds list: {sorted(front)}"
    return reds


def red_entry(front, test):
    """The record's one ``reds`` entry whose test is ``test``."""
    found = [r for r in reds_of(front) if isinstance(r, dict) and r.get("test") == test]
    assert len(found) == 1, f"the close record does not name the red {test} once: {reds_of(front)}"
    return found[0]


def red_entry_of_module(front, rel):
    """The record's one ``reds`` entry for the module file ``rel`` (a collection error: its file, or a node of it)."""
    found = [r for r in reds_of(front) if isinstance(r, dict)
             and str(r.get("test") or "").split("::")[0] == rel]
    assert len(found) == 1, f"the close record does not name the module {rel} once: {reds_of(front)}"
    return found[0]


def repair_tickets_naming(made, before, text):
    return [p.name for p in (made.root / ".tickets").glob("*.md")
            if p.stem not in before and text in p.read_text(encoding="utf-8")]


def assert_caused(made, run, before, test):
    """Refused with RED_CAUSED naming ``test``; the ticket stays open; no repair ticket names it; a close record,
    when one is written, marks it caused."""
    said = assert_refused(run, RED_CAUSED)
    assert test in said, f"the refusal does not name the caused red {test}\n{run.describe()}"
    assert made.ticket_status() == "in_progress", "the ticket closed with a red its change caused"
    if has_record(made):
        entry = red_entry(record(made), test)
        assert entry.get("caused") is True, f"the close record does not mark the red as the change's: {entry}"
    repairs = repair_tickets_naming(made, before, test)
    assert not repairs, f"a repair ticket was opened for a red the change caused: {repairs}"
    return said


def assert_closed(made, run):
    result = passed(run)
    assert made.ticket_status() == "closed", f"the ticket did not close\n{run.describe()}"
    assert has_record(made), "the close passed but wrote no close record"
    return result


# --------------------------------------------------------------------------
# Commits sharing a prefix (W2-194 S2's ambiguous --base)
# --------------------------------------------------------------------------

def ambiguous_prefix(made, length=9):
    """Two commits of the project whose ids share their first ``length`` digits, each on a branch of its own
    (``ambiguous-1``, ``ambiguous-2``): commit objects on HEAD's tree and parent, found by their messages (a birthday
    search, about 2^(2*length) ids), written with ``git hash-object``. Returns the shared prefix."""
    head = made.head()
    tree = made.git("rev-parse", "HEAD^{tree}").strip()
    who = "The Owner <owner@example.invalid> 1790000000 +0000"
    seen = {}
    number = 0
    while True:
        number += 1
        body = (f"tree {tree}\nparent {head}\nauthor {who}\ncommitter {who}\n\n"
                f"a commit for the ambiguous prefix, number {number}\n").encode()
        sha = hashlib.sha1(b"commit %d\0" % len(body) + body).hexdigest()
        key = sha[:length]
        if key in seen and seen[key][0] != sha:
            break
        seen[key] = (sha, body)
    for n, (sha, body) in enumerate((seen[key], (sha, body)), start=1):
        written = subprocess.run(["git", "-C", str(made.root), "hash-object", "-t", "commit", "-w", "--stdin"],
                                 input=body, capture_output=True, check=True).stdout.decode().strip()
        assert written == sha, f"git wrote {written}, not {sha}"
        made.git("update-ref", f"refs/heads/ambiguous-{n}", sha)
    return key


def unknown_prefix(made, length=9):
    """A prefix of ``length`` hex digits that names no object of the project."""
    for n in range(1, 10000):
        candidate = hashlib.sha1(f"unknown {n}".encode()).hexdigest()[:length]
        done = subprocess.run(["git", "-C", str(made.root), "rev-parse", f"--disambiguate={candidate}"],
                              capture_output=True, text=True)
        if not done.stdout.strip():
            return candidate
    raise AssertionError("no unknown prefix found")


# --------------------------------------------------------------------------
# accepted_reds (W2-194 S3; DEC-757's rule, as the strict close's cases plant it)
# --------------------------------------------------------------------------

def register_entry(decision, status, test):
    """A register entry ``decision`` with its own status line whose text names ``test`` (its function and file)."""
    file, name = test.split("::", 1)
    return (f"\n### {decision} — a known red of the project, accepted\n"
            f"- **Status:** {status}\n"
            f"- **Decision:** the path map lists `{name}`, in `{file}`, as an owner-accepted red; fixed by W2-zz.\n")


def path_map_with(made, **keys):
    data = yaml.safe_load((made.root / PATH_MAP_REL).read_text(encoding="utf-8")) or {}
    data.update(keys)
    return yaml.safe_dump(data, sort_keys=False)


def accepted_entry(test, decision):
    return {"test": test, "decision": decision, "reason": "red at the project's base; the owner accepts it",
            "fixed_by": "W2-zz"}
