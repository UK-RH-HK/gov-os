"""Round of DEC-595: the secrets-indexing scan runs its files in parallel (README, "Fourth batch").

DEC-595: "the secrets-indexing scan runs its files in parallel, as the module already does for the indexer
[...] No rule is loosened; every file is still scanned."

What the cases hold, through the check's declared command and ``gov.secrets.stores_with_secrets(root)``:

- **The same answer.** Every file under ``.gov-runtime/`` that holds a planted secret is reported, wherever it
  stands among many (the first, the last, a row of a SQLite store, a large file), each once, in the order of
  the paths, with all the processors of the machine and with one.
- **Nothing undecided.** One file that cannot be read, one folder that cannot be entered or one gitleaks run
  that fails, among many files that can be decided: the function gives no list and the check is not green.
- **Time.** On a stand-in runtime folder of a stated size the check ends within a bound the scan of one file
  after another misses (one case, declared in ``tests/acceptance/serial-only.txt``).

Every project is a temporary directory; every planted string is built at run time (``w1_15_support``).
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest

import w1_15_support as support

RUNTIME = support.RUNTIME_REL
WAIT_S = 180.0   # a wait under parallel load, not a time the ticket promises
MANY = 20        # the files without a secret that stand around the planted ones

# The stand-in runtime folder of the time case, and its bound (README, "The time case").
STAND_IN_FILES, STAND_IN_FILE_KIB, STAND_IN_DATABASE_MIB = 60, 4, 8
BOUND_S = 15.0

_LINE = "A chunk of ordinary prose about tokens, canaries and indexes; nothing in it is a secret.\n"

_STORES_CHILD = (
    "import json, sys\n"
    "from pathlib import Path\n"
    "from gov.secrets import stores_with_secrets\n"
    "result = stores_with_secrets(Path(sys.argv[1]))\n"
    f"print({support.RESULT_MARK!r} + json.dumps([str(item) for item in result]))\n"
)

ONE_PROCESSOR = ("taskset", "-c", "0")
PROCESSORS = {"every processor of the machine": (), "one processor": ONE_PROCESSOR}


def stores(project_root, sandbox, prefix=(), path=None):
    """``stores_with_secrets(root)`` in a child process: the list it returned (None when it raised), and the run."""
    done = subprocess.run([*prefix, sys.executable, "-c", _STORES_CHILD, str(project_root)],
                          cwd=str(sandbox.elsewhere), env=support.child_env(sandbox, path), capture_output=True,
                          text=True, timeout=WAIT_S, stdin=subprocess.DEVNULL)
    described = (f"gov.secrets.stores_with_secrets(root)\nexit code: {done.returncode}\n"
                 f"stdout:\n{done.stdout}\nstderr:\n{done.stderr}")
    lines = [line for line in done.stdout.splitlines() if line.startswith(support.RESULT_MARK)]
    if done.returncode != 0 or not lines:
        return None, described
    return json.loads(lines[-1][len(support.RESULT_MARK):]), described


def command(check, project_root, sandbox, prefix=(), path=None, wait=WAIT_S):
    """The declared command, by ``sh -c`` in the project's root (DEC-285). None when it did not end within ``wait``."""
    started = time.perf_counter()
    try:
        done = subprocess.run([*prefix, "sh", "-c", check["command"]], cwd=str(project_root),
                              env=support.child_env(sandbox, path), capture_output=True, text=True, timeout=wait,
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return None, time.perf_counter() - started
    return support.CheckRun(check["command"], done.returncode, done.stdout, done.stderr), time.perf_counter() - started


def fill(project, count=MANY, kib=1):
    """``count`` store files without a secret, in several folders of ``.gov-runtime/store/``."""
    text = _LINE * max(1, kib * 1024 // len(_LINE))
    return [project.write(f"{RUNTIME}/store/{number % 5:02d}/chunk-{number:04d}.md", text) for number in range(count)]


def database(project, rel, rows, last=None):
    """A SQLite store with ``rows`` rows of ordinary text and, where given, ``last`` as the text of its last row."""
    path = project.root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute("CREATE TABLE chunks (id INTEGER PRIMARY KEY, path TEXT, body TEXT)")
        connection.executemany("INSERT INTO chunks (path, body) VALUES (?, ?)",
                               ((f"notes/{number}.md", f"{number} " + _LINE * 40) for number in range(rows)))
        if last is not None:
            connection.execute("INSERT INTO chunks (path, body) VALUES (?, ?)", ("notes/last.md", last))
        connection.commit()
    finally:
        connection.close()
    return rel


def plant_among_many(project):
    """Six files with a planted secret among ``MANY`` without one. Returns the six, in the order of their paths."""
    fill(project)
    canary = support.in_prose(support.TIER_FORM)
    planted = [
        project.write(f"{RUNTIME}/aa/0000-first.md", canary),                       # the first file of the scan
        # two folders whose order differs when paths are compared as text and not name by name
        project.write(f"{RUNTIME}/pair/x.md", support.in_prose(support.KPI_FORM)),
        project.write(f"{RUNTIME}/pair-b/x.md", canary),
        project.write(f"{RUNTIME}/store/02/large.txt", _LINE * (2 * 1024 * 1024 // len(_LINE)) + canary),
        database(project, f"{RUNTIME}/store/03/lexical.sqlite", 50, last=support.in_prose(support.PRIVATE_KEY)),
        project.write(f"{RUNTIME}/zz/9999-last.md", canary),                        # the last file of the scan
    ]
    return sorted(planted, key=lambda rel: Path(rel).parts)


def processors(name):
    prefix = PROCESSORS[name]
    if prefix and shutil.which(prefix[0]) is None:
        pytest.skip(f"{prefix[0]} is not on PATH on this machine")
    return prefix


# --------------------------------------------------------------------------
# 1. The same answer
# --------------------------------------------------------------------------

@pytest.mark.parametrize("given", sorted(PROCESSORS))
def test_every_planted_file_among_many_is_reported_once_in_the_order_of_the_paths(given, store_project, sandbox):
    """The first, the last, a SQLite row and a large file: the list is those files and no other, in path order,
    whatever the machine gives the scan to run on."""
    planted = plant_among_many(store_project)
    found, described = stores(store_project.root, sandbox, processors(given))
    assert found is not None, f"the scan gave no list for stores it can read\n{described}"
    assert found == planted, \
        f"the scan's list is not the planted files in the order of their paths\nexpected: {planted}\n{described}"


def test_the_check_names_every_planted_file_among_many_in_that_order(family_check, store_project, sandbox):
    planted = plant_among_many(store_project)
    run, _ = command(family_check, store_project.root, sandbox)
    assert run is not None, f"the check did not end within {WAIT_S:.0f} s"
    assert run.returncode != 0, f"six stores hold a planted secret and the check passes\n{run.describe()}"
    lines = [line for line in run.stdout.splitlines() if line.strip()]
    named = [[rel for rel in planted if line.rstrip().endswith(rel)] for line in lines]
    assert named == [[rel] for rel in planted], \
        f"the check's output is not one line for each planted file, in the order of the paths\n{run.describe()}"
    for secret in (support.TIER_FORM, support.KPI_FORM):
        assert secret not in run.output, "the check printed a secret it found"


def test_a_canary_in_the_last_row_of_a_large_database_store_is_found(family_check, store_project, sandbox):
    rel = database(store_project, f"{RUNTIME}/store/lexical.sqlite", 2000, last=support.in_prose(support.TIER_FORM))
    assert (store_project.root / rel).stat().st_size > 6 * 1024 * 1024, "the premise: a store of several megabytes"
    run, _ = command(family_check, store_project.root, sandbox)
    assert run is not None and run.returncode != 0, \
        f"a canary in the last row of a large SQLite store and the check passes\n{run and run.describe()}"


# --------------------------------------------------------------------------
# 2. Nothing undecided: one file that cannot be decided fails the whole scan
# --------------------------------------------------------------------------

FAILS_ON = "W1-15: the stand-in scanner fails on this content."

# A stand-in for the scanner: it fails as a gitleaks that cannot scan does (an exit code that is neither "clean"
# nor "leaks") on the one content that holds the mark, and hands every other content to the real binary.
_FAILING_SCANNER = """#!{python}
import pathlib, subprocess, sys
data = sys.stdin.buffer.read()
with open({log!r}, "a") as log:
    log.write("run\\n")
if {mark!r}.encode() in data:
    sys.stderr.write("stand-in: the scan failed\\n")
    sys.exit(1)
sys.exit(subprocess.run([{real!r}, *sys.argv[1:]], input=data).returncode)
"""


def _no_access(path):
    path.chmod(0)
    if os.access(path, os.R_OK):
        path.chmod(0o755)
        pytest.skip("this user reads a file or folder of mode 0 (root): the obstacle cannot be built")


@pytest.fixture()
def obstacle(request, store_project, sandbox, gitleaks):
    """``MANY`` files that can be decided, one of them with a canary, and one thing that cannot be decided.

    Returns the ``PATH`` the scan is to run with (None: the session's).
    """
    fill(store_project)
    store_project.write(f"{RUNTIME}/aa/0000-first.md", support.in_prose(support.TIER_FORM))
    blocked, path = [], None
    if request.param == "a file that cannot be read":
        blocked.append(store_project.root / store_project.write(f"{RUNTIME}/store/02/unreadable.md", _LINE))
        _no_access(blocked[0])
    elif request.param == "a folder that cannot be entered":
        store_project.write(f"{RUNTIME}/store/closed/inside.md", _LINE)
        blocked.append(store_project.root / RUNTIME / "store" / "closed")
        _no_access(blocked[0])
    else:
        store_project.write(f"{RUNTIME}/store/02/the-scan-fails.md", _LINE + FAILS_ON + "\n")
        log = sandbox.tmpdir / "stand-in-scanner.log"
        stand_in = sandbox.empty_bin / "gitleaks"
        stand_in.write_text(_FAILING_SCANNER.format(python=sys.executable, log=str(log), mark=FAILS_ON, real=gitleaks),
                            encoding="utf-8")
        stand_in.chmod(0o755)
        path = f"{sandbox.empty_bin}{os.pathsep}{os.environ.get('PATH', '/usr/bin:/bin')}"
    yield path
    for each in blocked:
        each.chmod(0o755)


OBSTACLES = ("a file that cannot be read", "a folder that cannot be entered", "a gitleaks run that fails")


@pytest.mark.parametrize("obstacle", OBSTACLES, indirect=True)
def test_one_file_that_cannot_be_decided_among_many_gives_no_list_and_no_green_check(obstacle, family_check,
                                                                                    store_project, sandbox, request):
    """Not a list without the file, and not the list of what was found before it: the scan raises and the check
    is not green."""
    found, described = stores(store_project.root, sandbox, path=obstacle)
    assert found is None, \
        f"with {request.node.callspec.params['obstacle']} among the stores the scan still gave a list: {found}\n{described}"
    run, _ = command(family_check, store_project.root, sandbox, path=obstacle)
    assert run is not None and run.returncode != 0, \
        f"the check is green although one store could not be decided\n{run and run.describe()}"
    if obstacle is not None:
        assert (sandbox.tmpdir / "stand-in-scanner.log").is_file(), \
            "the premise: the scan ran the gitleaks binary found on PATH (the stand-in was never started)"


# --------------------------------------------------------------------------
# 3. Time
# --------------------------------------------------------------------------

def test_the_check_ends_within_the_bound_on_the_stand_in_runtime_folder(family_check, store_project, sandbox):
    """60 files of 4 KiB and one SQLite store of about 9 MB, none with a secret: green within the bound. One
    file after another takes about twice the bound on the machine the bound was set on (README)."""
    fill(store_project, STAND_IN_FILES, STAND_IN_FILE_KIB)
    rel = database(store_project, f"{RUNTIME}/store/lexical.sqlite",
                   STAND_IN_DATABASE_MIB * 1024 * 1024 // (len(_LINE) * 40))
    assert (store_project.root / rel).stat().st_size > STAND_IN_DATABASE_MIB * 1024 * 1024, "the stand-in's size"
    run, seconds = command(family_check, store_project.root, sandbox, wait=BOUND_S)
    assert run is not None, \
        f"the check did not end within {BOUND_S:.0f} s on {STAND_IN_FILES} small files and one large SQLite store"
    assert run.returncode == 0, f"the stand-in holds no secret and the check is not green\n{run.describe()}"
    assert seconds < BOUND_S
