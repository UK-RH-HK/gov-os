"""W2-94, failure line 1 (F1) -- a hidden question or answer must not be readable by a measured session by a route an
honest agent takes in ordinary work.

F1: "A hidden question or answer readable by a measured session by a route an honest agent takes in ordinary work.
Verify: a planted stand-in hidden file: a read, a grep and a `git log` from a measured session's sandbox (the guard's
path map) are refused or find it 0 times".

A temporary repository holds this tree's path map (its ``evaluation_sets.examin`` entry and its ``sets_root_hidden``
block), a committed stand-in hidden file ``fixtures/evaluation/examin/hidden/q01.yaml``, a stand-in development-half file
under ``hidden/visible/`` and a stand-in released file under ``visible/``; a planted HOME holds the same three under
``~/gov-os-eval`` (the sets root the path map names). Each call is put to the live guard hook (``.claude/hooks/
pretooluse.py``) the way W2-149's cases put theirs, as a session of each role the ``examin`` entry says it measures
(read from the path map). A call passes when the guard refuses it, or (a Bash line only) when running it for real in the
planted repository finds the stand-in's planted word 0 times. Controls: the released ``visible/`` file and an ordinary
``git log --oneline`` stay open to the same roles, so the refusals are not blanket.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_94_support as s  # noqa: E402

ENTRY = s.real_set_entry()
ROLES = list(ENTRY["measures"]["roles"])
REL = s.HIDDEN_QUESTION_REL
DEV_REL = f"{s.SET_REL}/hidden/visible/q02.yaml"
VISIBLE_REL = f"{s.SET_REL}/visible/q02.yaml"
HIDDEN_FOLDER = f"{s.SET_REL}/hidden"


@pytest.fixture(scope="module")
def planted(tmp_path_factory):
    return s.plant_guarded_repo(tmp_path_factory.mktemp("w2-94-guarded"))


def _tree_routes(repo):
    def bash(command):
        return ("Bash", {"command": command})

    return {
        "Read-the-file": ("Read", {"file_path": str(repo / REL)}),
        "Read-the-file-by-a-relative-path": ("Read", {"file_path": REL}),
        "Read-the-development-half-file": ("Read", {"file_path": str(repo / DEV_REL)}),
        "Grep-the-file": ("Grep", {"pattern": "question", "path": str(repo / REL), "output_mode": "content"}),
        "Grep-the-folder": ("Grep", {"pattern": "question", "path": str(repo / HIDDEN_FOLDER), "output_mode": "content"}),
        "Grep-above-the-folder": ("Grep", {"pattern": s.HIDDEN_WORD, "path": str(repo / "fixtures"),
                                           "output_mode": "content"}),
        "Grep-with-no-path": ("Grep", {"pattern": s.HIDDEN_WORD, "output_mode": "content"}),
        "Glob-the-folder": ("Glob", {"pattern": f"{HIDDEN_FOLDER}/*"}),
        "cat": bash(f"cat {REL}"),
        "head": bash(f"head -n 2 {REL}"),
        "grep-the-file": bash(f"grep -n question {REL}"),
        "grep-r-above": bash("grep -rn question fixtures/evaluation/"),
        "grep-r-dot": bash(f"grep -r {s.HIDDEN_WORD} ."),
        "git-log-p": bash("git log -p"),
        "git-log-p-of-the-path": bash(f"git log -p -- {REL}"),
        "git-log-all-p": bash("git log --all -p"),
        "git-grep": bash(f"git grep -n {s.HIDDEN_WORD}"),
        "git-grep-of-the-folder": bash(f"git grep -n question -- {HIDDEN_FOLDER}"),
        "git-show-the-path-at-HEAD": bash(f"git show HEAD:{REL}"),
        "git-show-HEAD": bash("git show HEAD"),
        "git-cat-file": bash(f"git cat-file -p HEAD:{REL}"),
    }


def _root_routes(sets_root):
    def bash(command):
        return ("Bash", {"command": command})

    path = sets_root / REL
    return {
        "Read-the-file": ("Read", {"file_path": str(path)}),
        "Read-the-development-half-file": ("Read", {"file_path": str(sets_root / DEV_REL)}),
        "Grep-the-file": ("Grep", {"pattern": "question", "path": str(path), "output_mode": "content"}),
        "Grep-the-folder": ("Grep", {"pattern": "question", "path": str(sets_root / HIDDEN_FOLDER),
                                     "output_mode": "content"}),
        "Glob-the-folder": ("Glob", {"pattern": "*", "path": str(sets_root / HIDDEN_FOLDER)}),
        "cat": bash(f"cat {path}"),
        "head": bash(f"head -n 2 {path}"),
        "grep-the-file": bash(f"grep -n question {path}"),
        "grep-r-the-set": bash(f"grep -rn question {sets_root / s.SET_REL}"),
    }


def _refused_or_zero(repo, home, call, role):
    """True when the guard refuses the call, or when the Bash line, run for real, finds the planted word 0 times."""
    tool, data = call
    decision, why = s.ask_guard(repo, home, tool, data, role)
    if decision == "deny":
        assert why, "a refusal carries its reason"
        return True
    assert decision in ("allow", "ask"), f"the guard failed: {decision} {why[:300]!r}"
    if tool != "Bash":
        return False
    done = subprocess.run(["bash", "-c", data["command"]], cwd=str(repo), capture_output=True, text=True,
                          timeout=s.TIMEOUT_S)
    return s.HIDDEN_WORD not in done.stdout + done.stderr


def test_the_path_map_declares_the_examin_hidden_half_to_the_roles_it_measures():
    assert ENTRY["hidden"] == [f"{s.SET_REL}/hidden/**"], ENTRY
    assert ENTRY["visible"] == [f"{s.SET_REL}/visible/**"], ENTRY
    assert ROLES, "the examin entry measures no role"
    assert {"engineer", "independent-test-designer", "independent-auditor"} <= set(ROLES), ROLES
    assert not any(role in ROLES for role in ("orchestrator",)), "the orchestrator runs the set and is not measured"


@pytest.mark.parametrize("route", sorted(_tree_routes(Path("/x"))))
@pytest.mark.parametrize("role", ROLES)
def test_f1_a_measured_session_cannot_read_a_planted_hidden_file_in_a_tree(planted, role, route):
    repo, home, _ = planted
    call = _tree_routes(repo)[route]
    assert _refused_or_zero(repo, home, call, role), f"{role}: {route} reads the planted hidden file: {call}"


@pytest.mark.parametrize("route", sorted(_root_routes(Path("/x"))))
@pytest.mark.parametrize("role", ROLES)
def test_f1_a_measured_session_cannot_read_a_planted_hidden_file_under_the_sets_root(planted, role, route):
    repo, home, sets_root = planted
    call = _root_routes(sets_root)[route]
    assert _refused_or_zero(repo, home, call, role), f"{role}: {route} reads the planted hidden file: {call}"


@pytest.mark.parametrize("role", ROLES)
def test_f1_the_released_visible_half_and_ordinary_work_stay_open_to_a_measured_session(planted, role):
    repo, home, sets_root = planted
    for call in (("Read", {"file_path": str(repo / VISIBLE_REL)}),
                 ("Read", {"file_path": str(sets_root / VISIBLE_REL)}),
                 ("Bash", {"command": f"cat {VISIBLE_REL}"}),
                 ("Bash", {"command": "git log --oneline"}),
                 ("Bash", {"command": "cat README.md"})):
        decision, why = s.ask_guard(repo, home, *call, role)
        assert decision == "allow", f"{role}: {call} was not allowed: {decision} {why[:300]!r}"


def test_f1_the_planted_hidden_file_is_in_the_planted_repository_history(planted):
    """The premise of the git routes: the stand-in is committed, so an unguarded ``git log -p`` would show it."""
    repo, _, _ = planted
    shown = subprocess.run(["git", "-C", str(repo), "log", "-p"], capture_output=True, text=True,
                           timeout=s.TIMEOUT_S).stdout
    assert s.HIDDEN_WORD in shown
    found = subprocess.run(["git", "-C", str(repo), "grep", "-n", s.HIDDEN_WORD], capture_output=True, text=True,
                           timeout=s.TIMEOUT_S).stdout
    assert REL in found
