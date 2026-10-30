"""W2-58, DEC-873 -- a session launched through ``gov launch`` works with what the guard refuses it.

KPI success 2 (DEC-873): "The launcher adds no OS-level Read deny rule for (c)
or (d), because running a test means reading it; the held-out material's Read
rules (b) stay in the sandbox; a launch under a malformed evaluation_sets block
is refused". KPI success 1 (restated): the engineer "can still run those tests
with pytest and see their names, results and failure messages".

Why (P-W2-58-1, measured on Claude Code 2.1.292): the CLI turns every ``Read``
deny rule that matches existing files into a read denial of the session's own
commands. Under each rule form tried, the engineer's pytest collected nothing,
the test designer could not import the code it tests, and ``git status`` showed
the refused test files as deleted (`` D``), so a ``commit -a`` would lose them.

Two kinds of case:

- **Cases that start nothing** read the ``--settings`` value ``gov launch``
  hands the stand-in CLI: no read denial covers a tracked file of the project
  (the condition under which ``git status`` shows no phantom deletion), and the
  held-out material keeps its Read rules in every launched role's settings. The
  conditions "pytest collects T's tests" and "the test designer imports the
  changed code" are asserted on the settings by the rewritten launcher cases of
  ``test_w2_58_engineer.py`` and ``test_w2_58_test_designer.py``; they are not
  repeated here. The malformed block's case is in ``test_w2_58_fails_closed.py``.
- **Live cases** (``local_only``, as W1-46 marks its own): a real engineer
  session and a real test-designer session on T, each started once through
  ``gov launch`` in a fixture project built from scratch, run one probe script
  and leave its output in ``.gov-runtime/scratch/w2-58/``. They need the CLI at
  ``~/.local/bin/claude`` with the caller's credentials, ``bwrap``, ``socat``
  and the network to the model's API; they are skipped when one of the first
  three is missing (W1-46's conditions). A launched test designer cannot run
  them: the ticket lead runs them from an unsandboxed session (README).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

import w2_58_support as s

ACC = s.T.acceptance
TD = s.TEST_DESIGNER
CLI_REL = ".local/bin/claude"


# --------------------------------------------------------------------------
# Cases that start nothing: the settings handed to the stand-in CLI
# --------------------------------------------------------------------------

LAUNCHED = {
    "engineer": (s.ENGINEER, s.T),
    "independent-test-designer": (TD, s.T),
    "independent-auditor": (s.AUDITOR, s.T),
    "product-spec": (s.PRODUCT_SPEC, s.SPEC),
    "research": (s.RESEARCH, s.EXPERIMENT),
}


def _project(sandbox):
    """The branch project, with the one named file a research launch reads."""
    return s.make_project(sandbox, base=True,
                          extra={s.ALLOWLIST_TEMPLATE_REL: s.ALLOWLIST_TEMPLATE.read_text(encoding="utf-8")})


@pytest.mark.parametrize("session", ("engineer", "independent-test-designer"))
def test_the_launch_denies_no_tracked_file_of_the_project_by_a_read_rule(sandbox, cli, session):
    """The twin of the live cases' "no phantom deletion": no Read deny rule and no sandbox read denial covers a file
    git tracks in the project, so the session's ``git status`` cannot show one as deleted (DEC-873 item 2)."""
    project = _project(sandbox)
    role, ticket = LAUNCHED[session]
    settings = s.launch(sandbox, cli, role, ticket).settings()
    faults = s.read_denial_faults(settings, project, sandbox.home, s.tracked_files(project))
    assert not faults, (f"the launched {session}'s settings deny reads of tracked files, which its git status would "
                        f"show as deleted (DEC-873 item 2, P-W2-58-1): {faults}")


@pytest.mark.parametrize("session", sorted(LAUNCHED))
def test_the_held_out_rules_stay_in_every_launched_role_s_settings(sandbox, cli, session):
    """DEC-873 item 2: "The held-out material's rules (b) stay in the sandbox as well"."""
    project = _project(sandbox)
    role, ticket = LAUNCHED[session]
    settings = s.launch(sandbox, cli, role, ticket).settings()
    lost = s.held_out_faults(settings, sandbox, project)
    assert not lost, (f"the launched {session}'s settings lost the held-out material's Read deny rule for {lost}: "
                      f"{s.read_deny_specs(settings)}")


# --------------------------------------------------------------------------
# Live cases: a real session started through gov launch
# --------------------------------------------------------------------------

SCRATCH = ".gov-runtime/scratch/w2-58"
SESSION_TIMEOUT_S = 420.0
NOT_INHERITED = ("GOV_ROLE", "GOV_TICKET")
NOT_INHERITED_PREFIX = "CLAUDE"   # DEC-784, as W1-46's live sessions launch

_HEAD = f"""#!/bin/bash
# W2-58 acceptance probe (DEC-873). It reads and runs; it writes nothing outside {SCRATCH}.
export PYTHONDONTWRITEBYTECODE=1
D={SCRATCH}
OUT=$D/results.txt
: > "$OUT"
"""
_TAIL = """git status --short > $D/status.txt 2>&1; echo "status=$?" >> "$OUT"
git update-index --refresh > $D/refresh.txt 2>&1; echo "refresh=$?" >> "$OUT"
echo "end=1" >> "$OUT"
"""
ENGINEER_PROBE = _HEAD + f"""python3 -m pytest {ACC}/ --collect-only -q -p no:cacheprovider > $D/collect.txt 2>&1; \
echo "collect=$?" >> "$OUT"
python3 -m pytest {ACC}/ -q -p no:cacheprovider > $D/run.txt 2>&1; echo "run=$?" >> "$OUT"
""" + _TAIL
TEST_DESIGNER_PROBE = _HEAD + """PYTHONPATH=src python3 -c "import app.main, app.added; \
print('value=%s added=%s' % (app.main.value(), app.added.ADDED))" > $D/import.txt 2>&1; echo "import=$?" >> "$OUT"
""" + _TAIL
PROMPT = ("Do exactly this one step, once, and nothing else. If it is refused or fails, do not retry it and do not "
          f"work around it. Run this Bash command as written: bash {SCRATCH}/probe.sh  Then run "
          f"cat {SCRATCH}/results.txt and answer with its output.")


@dataclass(frozen=True)
class Session:
    project: Path
    results: dict
    run: object

    def output(self, name):
        path = self.project / SCRATCH / name
        return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else f"<no {name}>"

    def describe(self, *names):
        shown = "\n".join(f"--- {name}:\n{self.output(name)[-1500:]}" for name in names)
        return f"results: {self.results}\n{shown}"


def _prerequisites():
    """W1-46's conditions for a live session: bwrap, socat and the CLI at ~/.local/bin/claude."""
    missing = [name for name in ("bwrap", "socat") if shutil.which(name) is None]
    if not (Path.home() / CLI_REL).is_file():
        missing.append("~/.local/bin/claude")
    if missing:
        pytest.skip(f"a launched session needs {missing} on this machine")


def _start(tmp, role, probe):
    """Build the fixture project, start one real session through ``gov launch`` and return what its probe left."""
    _prerequisites()
    sandbox = s.make_sandbox(tmp)
    project = s.make_project(sandbox, base=True)
    s.write(project / SCRATCH / "probe.sh", probe)
    env = {key: value for key, value in os.environ.items()
           if key not in NOT_INHERITED and not key.startswith(NOT_INHERITED_PREFIX)}
    env.update({"PYTHONPATH": s.python_path(), "PYTHONPYCACHEPREFIX": str(sandbox.pycache)})
    argv = s.gov_argv("launch", role, s.T.tk, "--", "-p", PROMPT, "--permission-mode", "acceptEdits",
                      "--model", "haiku", "--max-turns", "6", "--allowedTools", "Bash")
    try:
        done = subprocess.run(argv, cwd=str(project), env=env, capture_output=True, text=True,
                              timeout=SESSION_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        pytest.fail(f"the launched {role} session did not end within {SESSION_TIMEOUT_S:.0f} s", pytrace=False)
    run = s.Run(("gov", "launch", role, s.T.tk), done.returncode, done.stdout, done.stderr)
    results_path = project / SCRATCH / "results.txt"
    if not results_path.is_file() or "end=1" not in results_path.read_text(encoding="utf-8"):
        pytest.fail(f"the launched {role} session did not run the probe to its end (no complete "
                    f"{SCRATCH}/results.txt)\n{run.describe()[-1500:]}", pytrace=False)
    results = dict(line.split("=", 1) for line in results_path.read_text(encoding="utf-8").splitlines() if "=" in line)
    return Session(project, results, run)


@pytest.fixture(scope="module")
def engineer_session(tmp_path_factory):
    return _start(tmp_path_factory.mktemp("w2-58-live-engineer"), s.ENGINEER, ENGINEER_PROBE)


@pytest.fixture(scope="module")
def test_designer_session(tmp_path_factory):
    return _start(tmp_path_factory.mktemp("w2-58-live-test-designer"), TD, TEST_DESIGNER_PROBE)


@pytest.mark.local_only
def test_a_launched_engineer_collects_its_own_acceptance_tests(engineer_session):
    """``pytest --collect-only -q`` in the engineer's own session: a non-zero count, the test names visible."""
    collected = engineer_session.output("collect.txt")
    why = engineer_session.describe("collect.txt")
    assert engineer_session.results.get("collect") == "0", f"the collection failed\n{why}"
    assert re.search(r"\b2 tests? collected", collected), f"the engineer's pytest did not collect T's 2 tests\n{why}"
    for name in ("test_the_feature_passes", "test_the_feature_fails_with_a_message"):
        assert name in collected, f"the collection does not show {name}\n{why}"


@pytest.mark.local_only
def test_a_launched_engineer_runs_its_tests_and_sees_their_results(engineer_session):
    """A plain run: the counts, the failing test's name and its failure message."""
    ran = engineer_session.output("run.txt")
    why = engineer_session.describe("run.txt")
    assert "1 failed, 1 passed" in ran, f"the engineer's pytest run does not show T's results\n{why}"
    assert "test_the_feature_fails_with_a_message" in ran and s.FAILURE_WORD in ran, (
        f"the run does not show the failing test's name and message\n{why}")


@pytest.mark.local_only
def test_a_launched_test_designer_imports_the_branch_s_changed_code(test_designer_session):
    """``import`` of the module T's branch changes and of the one it adds, with the branch's version (``value()``
    returns 2 on the branch, 1 on the base)."""
    why = test_designer_session.describe("import.txt")
    assert test_designer_session.results.get("import") == "0", f"the test designer could not import the code\n{why}"
    assert "value=2 added=True" in test_designer_session.output("import.txt"), (
        f"the import did not give the branch's version\n{why}")


@pytest.mark.local_only
@pytest.mark.parametrize("which", ("engineer", "independent-test-designer"))
def test_a_launched_session_shows_no_phantom_deletion(request, which):
    """``git status --short`` shows no tracked file as deleted, and ``git update-index --refresh`` succeeds."""
    session = request.getfixturevalue("engineer_session" if which == "engineer" else "test_designer_session")
    why = session.describe("status.txt", "refresh.txt")
    deleted = [line for line in session.output("status.txt").splitlines() if line[:2] in (" D", "D ")]
    assert session.results.get("status") == "0" and not deleted, (
        f"the launched {which}'s git status shows tracked files as deleted: {deleted}\n{why}")
    assert session.results.get("refresh") == "0", f"the launched {which}'s git update-index --refresh failed\n{why}"
