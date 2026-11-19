"""Support code for W2-206's acceptance tests: ``gov queue`` as the landing-and-close, part 2 (README).

It stands on W2-202's support (``tests/acceptance/W2-202/w2_202_support.py``, imported as ``base``), which stands on
W2-115b's (``kit``): the planted project, its git helpers, the answer and refusal readers, the fixtures' own checks.
What is added here is what W2-206's lines need:

- ``gov queue`` with more in its environment, with or without ``--json``; ``gov wait``, ``gov close --select``,
  ``gov check --structural``, ``gov rebuild --integration`` and ``gov retrieve``, each through
  ``python3 -m gov.cli.main``;
- planted tests outside every selection (one the candidate breaks, one red on the base, one red the first time it
  runs, one that never ends), and a ``tests/conftest.py`` that tells each pytest the run starts (its command line,
  its pool) and each test's worker;
- a planted check declaration whose command tells where and when the structural pass ran it;
- the integration store's stand-ins, from W2-116's support (``stores``).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "W2-202"))
sys.path.insert(0, str(HERE.parent / "W2-116"))

import w2_202_support as base  # noqa: E402
import w2_116_support as stores  # noqa: E402,F401
from w2_202_support import A, B, BROKEN, C, CHANGED, kit, module_rel  # noqa: E402,F401

SELF_CHECK = kit.SELF_CHECK
REBUILD_REL = "governance/project/rebuild.yaml"
NIGHTLY_REL = "docs/close/nightly"
DRY_REL = ".gov-runtime/queue/dry"
WORKERS_KEY = "close_workers"   # the path map's key for a run's workers (``gov.close.command.WORKERS_KEY``)
OUT_NAMES = ("select.json", "summary.txt", "verify.exit")
EXIT_REFUSED_SELECTION = 2
UNMAPPED = "tools/extra.txt"   # no coupling, no ticket's paths, no test's import: the selection refuses it

# --------------------------------------------------------------------------
# Planted tests outside every selection (each imports the gizmo, which no case changes)
# --------------------------------------------------------------------------

FAR = "tests/unit/test_far.py"                # reads the widget's file without importing it: red when it says CHANGED
KNOWN_FAR = "tests/unit/test_known_far.py"    # red on the base too (a bare assert)
ONCE = "tests/unit/test_once.py"              # red the first time it runs in a landing, green after
SLOW = "tests/unit/test_slow.py"              # never ends inside a run's time limit
FAR_NODE, KNOWN_FAR_NODE, ONCE_NODE, SLOW_NODE = (kit.node(rel) for rel in (FAR, KNOWN_FAR, ONCE, SLOW))
GIZMO_NODE = kit.node(kit.GIZMO[0])
USES_HELPER_NODE = kit.node(kit.USES_HELPER[0])
CONFTEST = "tests/conftest.py"
STARTS, TEST_RUNS, STRUCTURAL_TOLD = "pytest-starts.jsonl", "test-runs.jsonl", "structural.jsonl"

FAR_BODY = (f"    ok = 'CHANGED' not in (_seen()[{module_rel('widget')!r}] or '')\n"
            "    _tell(ok)\n    assert ok, 'the widget changed'\n")


def far(told):
    return kit.telling(FAR, told, ["gizmo"], FAR_BODY, also_watch=["widget"])


def known_far(told):
    return kit.telling(KNOWN_FAR, told, ["gizmo"], kit.RED_ALWAYS)


def once(told):
    marker = str(Path(told) / "once.marker")
    body = (f"    if os.environ.get({SELF_CHECK!r}):\n        return\n"
            f"    first = not os.path.exists({marker!r})\n    open({marker!r}, 'a').close()\n"
            "    _tell(not first)\n    assert not first, 'red the first time it runs'\n")
    return kit.telling(ONCE, told, ["gizmo"], body)


def slow(told):
    body = (f"    _tell(True)\n    if os.environ.get({SELF_CHECK!r}):\n        return\n"
            "    import time\n    parent = os.getppid()\n    for _ in range(900):\n        time.sleep(1)\n"
            "        if os.getppid() != parent:\n            os._exit(1)\n")
    return kit.telling(SLOW, told, ["gizmo"], body)


def recorder(told):
    """``tests/conftest.py`` of a planted project: every pytest process that loads it tells its command line, whether
    it is an xdist worker and the pool it resolved; every test tells the worker it ran in and the pool's size."""
    return (
        "import json\nimport os\nimport sys\n\nimport pytest\n\n"
        f"TOLD = {str(told)!r}\nQUIET = os.environ.get({SELF_CHECK!r})\n\n\n"
        "def _tell(name, row):\n"
        "    if QUIET:\n        return\n"
        "    with open(os.path.join(TOLD, name), 'a', encoding='utf-8') as out:\n"
        "        out.write(json.dumps(row) + '\\n')\n\n\n"
        "def pytest_configure(config):\n"
        f"    _tell({STARTS!r}, {{'argv': list(sys.argv), 'args': [str(a) for a in config.invocation_params.args],\n"
        "                    'worker': os.environ.get('PYTEST_XDIST_WORKER'),\n"
        "                    'pool': getattr(config.option, 'numprocesses', None),\n"
        "                    'auto': os.environ.get('PYTEST_XDIST_AUTO_NUM_WORKERS'),\n"
        "                    'cpus': os.environ.get('GOV_HEAVY_CPUS')})\n\n\n"
        "@pytest.fixture(autouse=True)\n"
        "def _told_where(request):\n"
        f"    _tell({TEST_RUNS!r}, {{'test': request.node.nodeid, 'worker': os.environ.get('PYTEST_XDIST_WORKER'),\n"
        "                       'count': os.environ.get('PYTEST_XDIST_WORKER_COUNT')})\n"
    )


def rows(told, name):
    path = Path(told) / name
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def pools(starts):
    """Of the pytest processes a run started (xdist's own workers aside): each ``-n`` value on its command line."""
    found = []
    for row in starts:
        if row.get("worker"):
            continue
        words = [str(w) for w in row.get("args") or []]
        for at, word in enumerate(words):
            if word in ("-n", "--numprocesses") and at + 1 < len(words):
                found.append(words[at + 1])
            elif word.startswith("--numprocesses="):
                found.append(word.split("=", 1)[1])
            elif re.fullmatch(r"-n(\d+|auto|logical)", word):
                found.append(word[2:])
    return found


def path_map(workers=None):
    """The planted path map, naming ``workers`` for a run where given."""
    return yaml.safe_dump({**kit.PATH_MAP, **({WORKERS_KEY: workers} if workers is not None else {})},
                          sort_keys=False)


# --------------------------------------------------------------------------
# Tickets whose acceptance run fails without naming a failing test
# --------------------------------------------------------------------------

P = kit.Ticket("PROJ-pppp", "F-pp", ["mod_pp"])   # its README maps a line to a test that does not exist
Q = kit.Ticket("PROJ-qqqq", "F-qq", ["mod_qq"])   # its suite crashes at collection
USES_MOD_PP = ("tests/unit/test_uses_mod_pp.py", "mod_pp")
USES_MOD_QQ = ("tests/unit/test_uses_mod_qq.py", "mod_qq")
CRASHING = "raise RuntimeError('this suite crashes at collection')\n\n\ndef test_qq():\n    pass\n"


def readme_with_a_missing_test(ticket):
    case = f"`test_{ticket.slug}.py::test_{ticket.slug}`"
    return (f"# {ticket.wbs}\n\n| KPI | tests |\n|---|---|\n| success-1 | {case} |\n"
            f"| failure-1 | `test_{ticket.slug}.py::test_no_such_test` |\n")


# --------------------------------------------------------------------------
# gov, beside what W2-202's support runs
# --------------------------------------------------------------------------

def env_of(project, more=None):
    return {**kit.base_env(base.env_folder(project)), **(more or {})}


def queue(project, *args, plain=False, env=None):
    """``python3 -m gov.cli.main queue <args> --root <project> [--json]``: the run, as ``kit.run_queue`` gives it
    (``plain``: without ``--json``, the command's own output)."""
    cmd = [sys.executable, "-m", "gov.cli.main", "queue", *args, "--root", str(project.root)]
    cmd += [] if plain else ["--json"]
    try:
        done = subprocess.run(cmd, cwd=str(project.root), env=env or env_of(project), capture_output=True, text=True,
                              timeout=kit.GOV_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov queue {' '.join(args)} did not end within {kit.GOV_TIMEOUT_S} s") from None
    return {"args": list(args), "code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}


def gov(where, *args, env, timeout=600):
    """``python3 -m gov.cli.main <args>`` in ``where``: ``{"args", "code", "stdout", "stderr"}``."""
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args], cwd=str(where), env=env,
                          capture_output=True, text=True, timeout=timeout, stdin=subprocess.DEVNULL)
    return {"args": list(args), "code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}


def said(run):
    return base.said(run)


def snap(project):
    """What a command that moves nothing must leave as it was: W2-115b's state (every ref, what HEAD is, the status,
    the tracked files' bytes), every commit ``git log --all`` names, the files under ``.tickets/`` and ``docs/``, how
    often each planted test has told a run, and where the queue's warm clone stands."""
    root = project.root
    clone = root / kit.CLONE_REL
    places = sorted(str(path.relative_to(root)) for top in (".tickets", "docs") if (root / top).is_dir()
                    for path in (root / top).rglob("*"))
    told = {path.name: len(path.read_text(encoding="utf-8").splitlines())
            for path in sorted(Path(project.told).glob("*.jsonl"))}
    has_clone = (clone / ".git").exists()
    return {**kit.Planted.state(project),
            "log": sorted(kit.git(root, "log", "--all", "--format=%H").split()),
            "places": places, "told": told,
            "clone_head": kit.rev(clone, "HEAD") if has_clone else None,
            "clone_status": kit.git(clone, "status", "--porcelain") if has_clone else None,
            "clone_closes": kit.git(clone, "log", "--all", "--format=%H", "--", "docs/close").split()
            if has_clone else []}


def step(project, *args, plain=False, env=None):
    """One ``gov queue`` in the project: the snapshot before it, the run, the snapshot after it."""
    before = snap(project)
    run = queue(project, *args, plain=plain, env=env)
    return {"before": before, "run": run, "after": snap(project)}


def out_listing(out):
    """What a dry run left under its ``--out`` folder: each file's path below it, its modification time and, for the
    small text files, its text."""
    out = Path(out)
    files = []
    for path in sorted(out.rglob("*")) if out.is_dir() else []:
        if path.is_file():
            entry = {"rel": str(path.relative_to(out)), "mtime_ns": path.stat().st_mtime_ns, "path": str(path)}
            if path.name in OUT_NAMES:
                entry["text"] = path.read_text(encoding="utf-8", errors="replace")
            files.append(entry)
    return files


def wait(project, exit_file):
    """``gov wait <exit-file> 5``: its run."""
    env = env_of(project, {"GOV_WAIT_EVERY": "1"})
    return gov(project.root, "wait", str(exit_file), "5", env=env, timeout=120)


def close_select(project, revision, tid):
    """``gov close --select <tid>`` in a scratch clone of the project at ``revision``: its run."""
    scratch = base.scratch_at(project, revision, "select")
    done = gov(scratch, "close", "--select", tid, "--root", str(scratch),
               env=kit.base_env(scratch.parent / f"{scratch.name}-env"))
    shutil.rmtree(scratch, ignore_errors=True)
    return done


def one_object(text):
    """The one JSON object ``text`` is (None where it is anything else)."""
    try:
        value = json.loads(text)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


ONE_SLOT = '''import json, os
from gov.dispatch import admission, limits
from gov.resources import config, slots
sized = admission.sized()
count = slots.slot_count(config.load(), lambda line: None)
print(json.dumps({"sized": sized.get("workers_per_slot"),
                  "for_count": limits.workers_for(sized["load_limit"], sized["start_below"], sized["margin"], count),
                  "cpus": os.cpu_count()}))
'''


def one_slot(project, env=None):
    """One slot's workers by the product's rules, read in the queue's own environment: ``{"sized"`` (the machine's
    derived ``workers_per_slot``), ``"for_count"`` (``limits.workers_for`` for the slot count in force, as a slot's
    run sizes itself), ``"cpus"`` (the machine's CPU count)``}``."""
    done = subprocess.run([sys.executable, "-c", ONE_SLOT], env=env or env_of(project), capture_output=True,
                          text=True, timeout=120)
    try:
        found = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"fixture: one slot's workers cannot be read:\n{done.stdout}\n{done.stderr}") from None
    assert isinstance(found.get("sized"), int) and isinstance(found.get("for_count"), int), f"fixture: {found}"
    return found


# --------------------------------------------------------------------------
# The structural pass
# --------------------------------------------------------------------------

CHECK_DECL_REL = "governance/kernel/checks/core-schema.yaml"
CHECK_SCRIPT_REL = "governance/kernel/checks/tell_schema.py"
CHECK_DECL = f"id: core-schema\nfamily: schema\ncommand: python3 {CHECK_SCRIPT_REL}\n"
NOTICED = "the widget is changed"


def check_script(root, told):
    """The planted schema check: it notices a changed widget (one finding, exit 1) and tells the tree it ran in, that
    tree's head and where ``main`` stood at the planted root at that moment."""
    return (
        "import json\nimport os\nimport subprocess\nimport sys\nfrom pathlib import Path\n\n"
        f"ROOT, TOLD = {str(root)!r}, {str(Path(told) / STRUCTURAL_TOLD)!r}\nTREE = Path.cwd()\n\n\n"
        "def git(where, *args):\n"
        "    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}\n"
        "    done = subprocess.run(['git', '-C', str(where), *args], capture_output=True, text=True, env=env)\n"
        "    return done.stdout.strip()\n\n\n"
        f"changed = 'CHANGED' in (TREE / {module_rel('widget')!r}).read_text(encoding='utf-8')\n"
        f"if not os.environ.get({SELF_CHECK!r}):\n"
        "    with open(TOLD, 'a', encoding='utf-8') as out:\n"
        "        out.write(json.dumps({'tree': str(TREE), 'head': git(TREE, 'rev-parse', 'HEAD'),\n"
        "                              'main_at_root': git(ROOT, 'rev-parse', 'refs/heads/main'),\n"
        "                              'changed': changed}) + '\\n')\n"
        "if changed:\n"
        f"    print(json.dumps([{{'message': {NOTICED!r}}}]))\n    sys.exit(1)\n"
    )


def structural(where, base_commit, env):
    """``gov check --structural <base>`` in ``where`` (the planted check keeps quiet): its run."""
    return gov(where, "check", "--structural", base_commit, "--root", str(where), env={**env, SELF_CHECK: "1"})


def unstamped(lines):
    """The pass's lines with its seconds masked (the last line names how long it took)."""
    return [re.sub(r"\d+(\.\d+)? s\b", "N s", str(line)).rstrip() for line in lines if str(line).strip()]


def lines_of(value):
    return value if isinstance(value, list) else str(value or "").splitlines()


GIT_WRAPPER = ('#!/bin/sh\n# the structural pass asks git where the tree\'s top is (with --no-optional-locks): '
               'here git cannot answer\ncase " $* " in\n  *" --no-optional-locks "*" --show-toplevel "*)\n'
               '    echo "fatal: planted: git cannot be asked" >&2\n    exit 128;;\nesac\nexec {git} "$@"\n')


def failing_git(folder):
    """A folder holding a ``git`` that fails only the structural pass's first question, to put first on ``PATH``."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    real = shutil.which("git")
    assert real, "fixture: no git on PATH"
    (folder / "git").write_text(GIT_WRAPPER.format(git=real), encoding="utf-8")
    (folder / "git").chmod(0o755)
    return folder


# --------------------------------------------------------------------------
# Reading what a run left
# --------------------------------------------------------------------------

def queue_record(landing, result):
    return base.queue_record(landing, result)


def after_of(landing, result):
    """``queue.json``'s ``after`` of a landing (it must be there)."""
    held = queue_record(landing, result)
    after = held.get("after")
    assert isinstance(after, dict), f"queue.json holds no after-step: its keys are {sorted(held)}"
    return after


def not_configured(value):
    return value == "not_configured" or (isinstance(value, dict) and "not_configured" in map(str, value.values()))


def says_full(selection):
    """Whether a close record's ``selection`` says ``full``."""
    if isinstance(selection, str):
        return selection == "full"
    if isinstance(selection, dict):
        return selection.get("full") is True or "full" in [v for v in selection.values() if isinstance(v, str)]
    return False


def named(run, word):
    return word in run["stdout"] or word in run["stderr"]


def moved_nothing(taken):
    """A step that must move, commit and write nothing in the project: every ref, what HEAD is, the status (empty),
    the tracked files, every commit, and the files under ``.tickets/`` and ``docs/`` as before."""
    before, after = taken["before"], taken["after"]
    assert after["status"] == "", f"git status --porcelain at the root is not empty:\n{after['status']}"
    assert after["refs"] == before["refs"], f"the refs changed:\n{before['refs']}\n->\n{after['refs']}"
    for key, what in (("head", "what HEAD is"), ("log", "the commits git log --all names"),
                      ("places", "the files under .tickets/ and docs/"), ("files", "a tracked file")):
        assert after[key] == before[key], f"{what} changed"
