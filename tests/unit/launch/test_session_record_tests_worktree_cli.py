"""W2-60b S10 through the real command line (the CTO's path case P1 (a), DEC-1156 (7)): ``gov launch
independent-test-designer <ticket> --tests-worktree``, run in a ticket's worktree, goes through ``gov.cli.main``'s
parser and ``gov.launch.command`` to ``launcher.tests_worktree``.

Each case runs ``python3 -m gov.cli.main`` as its own process, in a scratch git repository under the test's
``tmp_path`` (the sandbox's ``$TMPDIR``), with ``PYTHONPATH`` set to this tree's ``src``."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TICKET = "TST-a001"


def _git(cwd: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *argv], capture_output=True, text=True, check=False)


def _repo(tmp_path: Path) -> Path:
    """A ticket worktree on ``w2/T-1`` with one commit and an ``in_progress`` engineer ticket."""
    main = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", "-b", "w2/T-1", str(main)], check=True)
    folder = main / ".tickets"
    folder.mkdir()
    (folder / f"{TICKET}.md").write_text(f"---\nid: {TICKET}\nstatus: in_progress\nrole: engineer\n"
                                         f"class: implementation\nallowed_paths:\n- src/app/**\n---\n# {TICKET}\n",
                                         encoding="utf-8")
    subprocess.run(["git", "-C", str(main), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(main), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"],
                   check=True)
    return Path(os.path.realpath(main))


def _gov(cwd: Path, *argv: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"))
    return subprocess.run([sys.executable, "-m", "gov.cli.main", *argv], cwd=str(cwd), env=env, capture_output=True,
                          text=True, check=False, timeout=120)


def test_the_cli_makes_the_tests_worktree_on_its_own_branch_at_head(tmp_path):
    main = _repo(tmp_path)
    head = _git(main, "rev-parse", "HEAD").stdout.strip()
    done = _gov(main, "launch", "independent-test-designer", TICKET, "--tests-worktree")
    tests = Path(f"{main}-tests")
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == str(tests)
    assert tests.is_dir()
    assert _git(tests, "symbolic-ref", "--short", "HEAD").stdout.strip() == "w2/T-1-tests"
    assert _git(tests, "rev-parse", "HEAD").stdout.strip() == head
    # it starts, records and gates nothing: no launch record, no session record in the ticket's tree
    assert not (main / ".gov-runtime" / "launches").exists() and not (main / ".gov-runtime" / "sessions").exists()


def test_the_cli_refuses_while_the_tests_branch_exists_and_makes_no_tree(tmp_path):
    main = _repo(tmp_path)
    assert _git(main, "branch", "w2/T-1-tests").returncode == 0
    done = _gov(main, "launch", "independent-test-designer", TICKET, "--tests-worktree")
    assert done.returncode == 1, (done.stdout, done.stderr)
    assert "LAUNCH_REFUSED" in done.stderr and "w2/T-1-tests" in done.stderr
    assert not Path(f"{main}-tests").exists()


def test_the_cli_refuses_another_role_and_makes_no_tree(tmp_path):
    main = _repo(tmp_path)
    done = _gov(main, "launch", "engineer", TICKET, "--tests-worktree")
    assert done.returncode == 1, (done.stdout, done.stderr)
    assert "LAUNCH_REFUSED" in done.stderr
    assert not Path(f"{main}-tests").exists()


def test_the_cli_refuses_a_tree_on_no_branch_and_makes_no_tree(tmp_path):
    main = _repo(tmp_path)
    assert _git(main, "checkout", "-q", "--detach").returncode == 0
    done = _gov(main, "launch", "independent-test-designer", TICKET, "--tests-worktree")
    assert done.returncode == 1, (done.stdout, done.stderr)
    assert "LAUNCH_REFUSED" in done.stderr and "no branch" in done.stderr
    assert not Path(f"{main}-tests").exists()
