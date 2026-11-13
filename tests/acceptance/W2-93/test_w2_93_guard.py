"""W2-93's acceptance tests for failure line F1: a hidden question or answer readable by a measured session by a route an
honest agent takes in ordinary work.

A planted stand-in hidden file sits under a stand-in project's `fixtures/evaluation/adoption-proving-ground/hidden/`;
the project's path map carries the **actual** map's `adoption-proving-ground` entry (read from
`governance/project/path-map.yaml`'s `evaluation_sets`). For each role the entry measures, the guard's decision on a
Read, a Grep from a folder above and a Bash `git log -p` / `grep -r` is a refusal, or the equivalent command finds the
planted word 0 times. The guard is called as `tests/unit/guard/test_reads.py` calls it (`policy_refusal`, on a temporary
project, HOME in the temporary folder). Nothing is read from, or written to, the evaluation sets' root.

These cases pass on the integrated guard today (W2-84 and W2-58 are merged): they hold the path map's entry to its job.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.reads import HIDDEN_REFUSAL, policy_refusal  # noqa: E402

import w2_93_standin as s  # noqa: E402

TICKET = "DAEO-t93"
ENTRY = yaml.safe_load((REPO / "governance" / "project" / "path-map.yaml").read_text(encoding="utf-8"))[
    "evaluation_sets"]["adoption-proving-ground"]
MEASURED = list(ENTRY["measures"]["roles"])
HIDDEN_FILE = f"{s.HIDDEN_REL}/python-app.yaml"
VISIBLE_FILE = "tests/acceptance/W2-81/questions/python-app.yaml"


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                   capture_output=True)


def _put(root, rel, text):
    path = Path(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture(scope="module")
def project(tmp_path_factory):
    """A stand-in project with the actual map's entry and one planted hidden file, committed."""
    base = tmp_path_factory.mktemp("w2-93-guard")
    home = base / "home"
    root = home / "proj"
    patch = pytest.MonkeyPatch()
    patch.setenv("HOME", str(home))
    _put(root, f".tickets/{TICKET}.md", f"---\nid: {TICKET}\nwbs_id: W2-97\nstatus: in_progress\nrole: engineer\n"
                                        "allowed_paths:\n- src/**\n---\n")
    _put(root, HIDDEN_FILE, f"form: w2-81-questions/1\nquestions:\n  - question: {s.WORD} planted question\n"
                            f"    gold_answer: {s.WORD} planted answer\n")
    _put(root, f"{s.HIDDEN_REL}/variants.yaml", f"variants: []  # {s.WORD}\n")
    _put(root, VISIBLE_FILE, "form: w2-81-questions/1\nquestions: []\n")
    _put(root, "src/app/main.py", "x\n")
    _put(root, "governance/project/held-out.yaml", "held_out_paths:\n  - /nowhere/held\n")
    _put(root, ".claude/settings.json", "{}\n")
    _put(root, "governance/project/path-map.yaml",
         "namespaces: {}\n" + yaml.safe_dump({"evaluation_sets": {"adoption-proving-ground": ENTRY}}))
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    _git(root, "branch", "w2/integrate")
    yield root
    patch.undo()


def _routes(root):
    """Route name -> (tool, tool input, the command that finds what the route would show, run from ``root``)."""
    word = s.WORD
    return {
        "read-by-absolute-path": ("Read", {"file_path": str(root / HIDDEN_FILE)}, ["cat", HIDDEN_FILE]),
        "read-by-relative-path": ("Read", {"file_path": HIDDEN_FILE}, ["cat", HIDDEN_FILE]),
        "grep-tool-from-a-folder-above": ("Grep", {"pattern": word, "path": str(root / "fixtures")},
                                          ["grep", "-rn", word, "fixtures"]),
        "grep-tool-from-the-root": ("Grep", {"pattern": word}, ["grep", "-rn", word, "."]),
        "bash-grep-r-from-a-folder-above": ("Bash", {"command": f"grep -rn {word} fixtures"},
                                            ["grep", "-rn", word, "fixtures"]),
        "bash-grep-r-from-the-root": ("Bash", {"command": f"grep -rn {word} ."}, ["grep", "-rn", word, "."]),
        "bash-git-log-p": ("Bash", {"command": "git log -p"}, ["git", "log", "-p"]),
        "bash-git-log-p-all": ("Bash", {"command": "git log -p --all"}, ["git", "log", "-p", "--all"]),
    }


ROUTES = list(_routes(Path("/x")))


def _finds(root, command):
    """How many times the planted word is in what the command prints, run from the project's root."""
    done = subprocess.run(command, cwd=root, capture_output=True, text=True, errors="replace")
    return done.stdout.count(s.WORD)


def _why(root, role, tool, tool_input):
    return policy_refusal(tool, tool_input, str(root), str(root), role, TICKET)


def test_f1_the_map_entry_measures_the_roles_the_ticket_names():
    """F1's premise: the actual map's entry names the measured roles and the hidden glob the stand-in sits under."""
    assert ENTRY["hidden"] == ["fixtures/evaluation/adoption-proving-ground/hidden/**"]
    assert MEASURED and set(MEASURED) >= {"engineer", "independent-test-designer", "independent-auditor"}


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("role", MEASURED)
def test_f1_a_measured_session_is_refused_the_hidden_file_or_finds_the_planted_word_0_times(project, role, route):
    """F1: for each measured role and each route (a read, a grep from a folder above, a Bash `git log -p` or
    `grep -r`): the guard refuses, or the equivalent command finds the planted word 0 times."""
    tool, tool_input, command = _routes(project)[route]
    why = _why(project, role, tool, tool_input)
    if why:
        assert "fail closed" not in why, f"the guard could not decide, so the stand-in proves nothing: {why}"
        return
    assert _finds(project, command) == 0, f"{role} was not refused {route}, and it finds the planted word"


@pytest.mark.parametrize("role", MEASURED)
def test_f1_the_guard_names_the_hidden_half_when_a_measured_session_reads_it(project, role):
    """F1: a direct Read of the hidden file is refused with the hidden half's own reason (not a fault, not another
    part's reason), for each measured role."""
    assert _why(project, role, "Read", {"file_path": str(project / HIDDEN_FILE)}) == HIDDEN_REFUSAL


@pytest.mark.parametrize("role", MEASURED)
def test_f1_the_visible_half_stays_readable_to_a_measured_session(project, role):
    """F1 (the entry's reach): the visible half of the set is not refused, so the refusals above come from the hidden
    glob and nothing wider."""
    assert _why(project, role, "Read", {"file_path": str(project / VISIBLE_FILE)}) == ""


def test_f1_a_session_the_set_does_not_measure_may_read_the_hidden_file(project):
    """F1 (the control): the orchestrator is not measured, so the same Read is allowed: the stand-in is where the entry
    says, and the refusals for the measured roles are the entry's."""
    assert "orchestrator" not in MEASURED
    assert _why(project, "orchestrator", "Read", {"file_path": str(project / HIDDEN_FILE)}) == ""
