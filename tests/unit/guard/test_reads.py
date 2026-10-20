"""Builder tests for W2-58: Policy 2's read refusals in the guard (DEC-820,
DEC-821): (a) secrets, (c) the counterpart's work, (d) the hidden part of
an evaluation set.

Regression evidence only (DEC-136).  Every project is a temporary one; the
ticket's WBS id is a stand-in, W2-95.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard.decide import LONG_REFUSAL, decide  # noqa: E402
from gov.guard.reads import (CHANGED_REFUSAL, HIDDEN_REFUSAL, SECRET_REFUSAL,  # noqa: E402
                             TESTS_REFUSAL, PolicyError, check_sets, policy_refusal,
                             read_denials, set_fault)

TICKET = "DAEO-t95"
SETS = ("evaluation_sets:\n  m:\n    visible: [docs/q.md]\n"
        "    hidden: [eval/hidden/**, eval/answers-*.yaml]\n    measures:\n      roles: [research]\n")


def _put(root: Path, rel: str, text: str = "x\n") -> None:
    (root / rel).parent.mkdir(parents=True, exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8")


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                   check=True, capture_output=True)


@pytest.fixture()
def project(tmp_path, monkeypatch):
    home = tmp_path / "home"
    root = home / "proj"
    monkeypatch.setenv("HOME", str(home))
    _put(root, f".tickets/{TICKET}.md", f"---\nid: {TICKET}\nwbs_id: W2-95\nstatus: in_progress\n"
                                        "role: engineer\nallowed_paths:\n- src/**\n---\n")
    for rel in ("tests/acceptance/W2-95/test_feature.py", "tests/acceptance/W2-96/test_other.py",
                "src/app/main.py", ".env", "services/api/.env.local", "certs/s.pem",
                "config/secrets.yaml", "eval/hidden/a.yaml", "eval/answers-x.yaml", "docs/q.md"):
        _put(root, rel)
    _put(root, "governance/project/held-out.yaml", "held_out_paths:\n  - /nowhere/held\n")
    _put(root, ".claude/settings.json", "{}\n")
    _put(root, "governance/project/path-map.yaml", "namespaces: {}\n" + SETS)
    _put(home, ".ssh/id_ed25519")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "base")
    _git(root, "branch", "w2/integrate")
    _put(root, "src/app/main.py", "changed\n")
    _put(root, "src/app/added.py")
    _put(root, "tests/acceptance/W2-95/test_more.py")
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "work")
    return root


def _why(root, role, tool, tool_input, ticket=TICKET, agent=None):
    return policy_refusal(tool, tool_input, str(root), str(root), role, ticket, agent)


def _bash(command):
    return "Bash", {"command": command}


CASES = [
    # (a) secrets, every role, by name only
    ("independent-auditor", *_bash("cat .env"), SECRET_REFUSAL),
    ("orchestrator", *_bash("head -n 1 services/api/.env.local"), SECRET_REFUSAL),
    ("orchestrator", *_bash("git show HEAD:.env"), SECRET_REFUSAL),
    ("orchestrator", *_bash("cat ~/.ssh/id_ed25519"), SECRET_REFUSAL),
    ("orchestrator", *_bash("cat $HOME/.ssh/id_ed25519"), SECRET_REFUSAL),
    ("orchestrator", *_bash("cp certs/s.pem /tmp/copy"), SECRET_REFUSAL),
    ("orchestrator", *_bash("grep k config/secrets.yaml"), SECRET_REFUSAL),
    ("orchestrator", *_bash("cat .env*"), SECRET_REFUSAL),
    ("orchestrator", "Read", {"file_path": "config/secrets.yaml"}, SECRET_REFUSAL),
    ("orchestrator", "Grep", {"pattern": "k", "path": ".env"}, SECRET_REFUSAL),
    ("orchestrator", *_bash("grep -rn k ."), ""),  # a search from above is not refused for them
    ("orchestrator", "Grep", {"pattern": "k"}, ""),
    ("orchestrator", "Glob", {"pattern": "**/.env*"}, ""),  # names only
    # the two files' reads open; another ticket's tests readable
    ("engineer", "Read", {"file_path": "governance/project/held-out.yaml"}, ""),
    ("engineer", *_bash("grep -n hooks .claude/settings.json"), ""),
    ("engineer", *_bash("ls governance/project/"), ""),
    ("engineer", "Read", {"file_path": "tests/acceptance/W2-96/test_other.py"}, ""),
    # (c) the engineer
    ("engineer", "Read", {"file_path": "tests/acceptance/W2-95/test_feature.py"}, TESTS_REFUSAL),
    ("engineer", "Read", {"file_path": "tests/acceptance/W2-95/missing.py"}, TESTS_REFUSAL),
    ("engineer", *_bash("sed -n 1,5p tests/acceptance/W2-95/test_feature.py"), TESTS_REFUSAL),
    ("engineer", *_bash("python3 -c \"open('tests/acceptance/W2-95/test_feature.py')\""), TESTS_REFUSAL),
    ("engineer", *_bash("wc -l < tests/acceptance/W2-95/test_feature.py"), TESTS_REFUSAL),
    ("engineer", *_bash("cd tests/acceptance && cat W2-95/test_feature.py"), TESTS_REFUSAL),
    ("engineer", *_bash("timeout 5 cat tests/acceptance/W2-95/test_feature.py"), TESTS_REFUSAL),
    ("engineer", *_bash("echo $(cat tests/acceptance/W2-95/test_feature.py)"), TESTS_REFUSAL),
    ("engineer", *_bash("cp -r tests/acceptance /tmp/t"), TESTS_REFUSAL),
    ("engineer", *_bash("ls tests/acceptance/W2-95"), TESTS_REFUSAL),
    ("engineer", *_bash("ls tests/acceptance"), ""),
    ("engineer", "Glob", {"pattern": "tests/acceptance/W2-95/*"}, TESTS_REFUSAL),
    ("engineer", "Glob", {"pattern": "tests/acceptance/*"}, ""),
    ("engineer", "Grep", {"pattern": "z", "path": "tests"}, TESTS_REFUSAL),
    ("engineer", "Grep", {"pattern": "z"}, TESTS_REFUSAL),
    ("engineer", "Grep", {"pattern": "z", "glob": "*.md"}, ""),
    ("engineer", "Grep", {"pattern": "z", "path": "src"}, ""),
    ("engineer", *_bash("grep -rn z tests/"), TESTS_REFUSAL),
    ("engineer", *_bash("grep -rn z --include='*.md' ."), ""),
    ("engineer", *_bash("rg z"), TESTS_REFUSAL),
    ("engineer", *_bash("rg z -g '*.md'"), ""),
    # a listing from above shows names: refused only aimed inside
    ("engineer", *_bash("find . -name '*.py'"), ""),
    ("engineer", *_bash("find . -name '*.py' -exec cat {} +"), TESTS_REFUSAL),
    ("engineer", *_bash("find . -type f -exec grep -l z {} +"), TESTS_REFUSAL),
    ("engineer", *_bash("find . -name x"), ""),
    ("engineer", *_bash("ls -R tests"), ""),
    ("engineer", *_bash("rg --files"), ""),
    ("engineer", "Glob", {"pattern": "**/*.py"}, ""),
    ("engineer", *_bash("grep -rn z . 2>&1 | head"), TESTS_REFUSAL),
    # an rg fed by a pipe or an input redirect searches what feeds it
    ("engineer", *_bash("git log --oneline | rg -g '!*.md' z 2>/dev/null"), ""),
    ("engineer", *_bash("rg z < docs/q.md"), ""),
    ("engineer", *_bash("ls | rg z ."), TESTS_REFUSAL),
    ("engineer", *_bash("ls | rg z &"), TESTS_REFUSAL),
    ("engineer", *_bash("ls | grep -r z"), TESTS_REFUSAL),
    ("engineer", *_bash("git show HEAD:src/app/main.py 2>&1"), ""),
    ("engineer", *_bash("git grep -n z"), TESTS_REFUSAL),
    ("engineer", *_bash("git grep -n z -- src"), ""),
    ("engineer", *_bash("git log -p"), TESTS_REFUSAL),
    ("engineer", *_bash("git log -p -- src/"), ""),
    ("engineer", *_bash("git log --oneline"), ""),
    ("engineer", *_bash("git show HEAD"), TESTS_REFUSAL),
    ("engineer", *_bash("git show --stat HEAD"), ""),
    ("engineer", *_bash("git show HEAD:src/app/main.py"), ""),
    ("engineer", *_bash("git show HEAD:tests/acceptance/W2-95/test_feature.py"), TESTS_REFUSAL),
    ("engineer", *_bash("git diff HEAD~1"), TESTS_REFUSAL),
    ("engineer", *_bash("git diff --name-only HEAD~1"), ""),
    ("engineer", *_bash("git diff HEAD~1 -- src"), ""),
    ("engineer", *_bash("python3 -m pytest tests/acceptance/W2-95/ -q"), ""),
    ("engineer", *_bash("PYTHONPATH=src timeout 600 pytest tests/acceptance/W2-95 -rs"), ""),
    ("independent-auditor", *_bash("cat tests/acceptance/W2-95/test_feature.py"), ""),
    ("independent-auditor", *_bash("git log -p"), ""),
    ("orchestrator", "Read", {"file_path": "tests/acceptance/W2-95/test_feature.py"}, ""),
    # (c) the test designer: the changed files but its own tests
    ("independent-test-designer", "Read", {"file_path": "src/app/main.py"}, CHANGED_REFUSAL),
    ("independent-test-designer", "Read", {"file_path": "src/app/added.py"}, CHANGED_REFUSAL),
    ("independent-test-designer", "Read", {"file_path": "tests/acceptance/W2-95/test_more.py"}, ""),
    ("independent-test-designer", *_bash("git show w2/integrate:src/app/main.py"), ""),
    ("independent-test-designer", *_bash("git show HEAD:src/app/main.py"), CHANGED_REFUSAL),
    ("independent-test-designer", *_bash("git diff w2/integrate...HEAD"), CHANGED_REFUSAL),
    ("independent-test-designer", *_bash("git diff --stat w2/integrate...HEAD"), ""),
    ("independent-test-designer", *_bash("ls src/app"), CHANGED_REFUSAL),
    ("independent-test-designer", *_bash("ls src"), ""),
    ("independent-test-designer", "Glob", {"pattern": "src/app/*"}, CHANGED_REFUSAL),
    ("independent-test-designer", *_bash("cat docs/q.md"), ""),
    # (d) a measured session, and one the set does not measure
    ("research", "Read", {"file_path": "eval/hidden/a.yaml"}, HIDDEN_REFUSAL),
    ("research", "Read", {"file_path": "eval/answers-x.yaml"}, HIDDEN_REFUSAL),
    ("research", *_bash("ls eval/hidden"), HIDDEN_REFUSAL),
    ("research", *_bash("grep -rn q eval/"), HIDDEN_REFUSAL),
    ("research", *_bash("python3 score.py --set m"), ""),
    ("research", "Read", {"file_path": "docs/q.md"}, ""),
    ("orchestrator", "Read", {"file_path": "eval/hidden/a.yaml"}, ""),
]


@pytest.mark.parametrize("role, tool, tool_input, why", CASES)
def test_each_route_is_decided_as_policy_2_says(project, role, tool, tool_input, why):
    assert _why(project, role, tool, tool_input) == why


def test_the_acting_role_is_the_subagent_s(project):
    read = {"file_path": "tests/acceptance/W2-95/test_feature.py"}
    assert _why(project, "orchestrator", "Read", read, agent="engineer") == TESTS_REFUSAL
    assert _why(project, "engineer", "Read", read, agent="independent-auditor") == ""
    assert _why(project, "engineer", "Read", read, agent="Explore") == TESTS_REFUSAL


def test_a_part_that_does_not_exist_is_refused_only_where_a_call_aims_at_it(project, tmp_path):
    _put(project, "governance/project/path-map.yaml",
         "evaluation_sets:\n  m:\n    hidden: [fixtures/eval/hidden/**]\n"
         "    measures: {roles: [research]}\n")
    assert _why(project, "research", "Read", {"file_path": "fixtures/eval/hidden/x"}) == HIDDEN_REFUSAL
    assert _why(project, "research", *_bash("ls fixtures/eval/hidden")) == HIDDEN_REFUSAL
    for tool, tool_input in (_bash("grep -rn q ."), ("Grep", {"pattern": "q"}), _bash("git log -p")):
        assert _why(project, "research", tool, tool_input) == "", tool_input


def test_what_cannot_be_worked_out_refuses(project):
    read = ("Read", {"file_path": "src/app/main.py"})
    # A ticket file that is not YAML; a ticket with no WBS id names no folder.
    _put(project, f".tickets/{TICKET}.md", "---\nwbs_id: [W2-95\n---\n")
    assert "fail closed" in _why(project, "engineer", *read)
    _put(project, f".tickets/{TICKET}.md", "---\nid: x\nstatus: in_progress\n---\n")
    assert _why(project, "engineer", *read) == ""
    # A malformed set refuses the sessions it could concern.
    _put(project, "governance/project/path-map.yaml",
         "evaluation_sets:\n  m:\n    hidden: x\n    measures: {roles: [research]}\n")
    assert "fail closed" in _why(project, "research", *read)
    assert _why(project, "orchestrator", *read) == ""
    _put(project, "governance/project/path-map.yaml", "evaluation_sets: [a]\n")
    assert "fail closed" in _why(project, "orchestrator", *read)
    with pytest.raises(PolicyError):
        check_sets(str(project))
    # w2/integrate present, but git finds no base.
    _put(project, "governance/project/path-map.yaml", "namespaces: {}\n")
    _git(project, "checkout", "-q", "--orphan", "lone")
    _git(project, "commit", "-qm", "lone")
    assert "fail closed" in _why(project, "independent-test-designer", *read)


def test_no_w2_integrate_refuses_the_test_designer_nothing(project):
    _git(project, "branch", "-D", "w2/integrate")
    assert _why(project, "independent-test-designer", "Read", {"file_path": "src/app/main.py"}) == ""


@pytest.mark.parametrize("entry, fault", [
    ({"visible": ["a"], "hidden": ["b/**"], "measures": {"roles": ["engineer"]}}, False),
    ({"hidden": ["b"], "measures": {"tickets": ["W2-61"]}}, False),
    ({"visible": ["a"], "measures": {"roles": ["engineer"]}}, True),
    ({"hidden": [], "measures": {"roles": ["engineer"]}}, True),
    ({"hidden": [3], "measures": {"roles": ["engineer"]}}, True),
    ({"visible": [3], "hidden": ["b"], "measures": {"roles": ["engineer"]}}, True),
    ({"hidden": ["/abs"], "measures": {"roles": ["engineer"]}}, True),
    ({"hidden": ["b"], "measures": {"roles": []}}, True),
    ({"hidden": ["b"]}, True), ("x", True),
])
def test_a_set_s_shape_is_checked(entry, fault):
    assert bool(set_fault(entry)) == fault


def test_the_sandbox_rules_hold_a_wildcard_and_cover_the_parts(project):
    root = os.path.realpath(project)
    assert read_denials(project, "engineer", TICKET) == [f"Read(/{root}/tests/acceptance/W2-95/**)"]
    assert read_denials(project, "independent-test-designer", TICKET) == [
        f"Read(/{root}/src/app/added.py*)", f"Read(/{root}/src/app/main.py*)"]
    assert read_denials(project, "research", TICKET) == [
        f"Read(/{root}/eval/hidden/**)", f"Read(/{root}/eval/answers-*.yaml)"]
    assert read_denials(project, "independent-auditor", TICKET) == []


def test_the_rules_answer_within_the_bound(project):
    wide, deep = "{a,b}" * 8, "a/" * 16000
    for role in ("engineer", "orchestrator"):
        assert _why(project, role, *_bash(f"cat {wide}/{deep}")) == LONG_REFUSAL
        assert _why(project, role, *_bash("echo " + " ".join(f"w{i}" for i in range(5000)))) == ""


def test_the_decision_refuses_through_the_read_rules_and_leaves_writes_to_the_allow_list(project):
    assert decide("Read", {"file_path": "tests/acceptance/W2-95/test_feature.py"}, str(project),
                  "engineer", TICKET, cwd=str(project), flag="absent") == ("deny", TESTS_REFUSAL)
    assert decide("Edit", {"file_path": str(project / "src/app/main.py"), "old_string": "c",
                           "new_string": "d"}, str(project), "engineer", TICKET,
                  cwd=str(project), flag="absent") == ("allow", "")
    for reason in (SECRET_REFUSAL, TESTS_REFUSAL, CHANGED_REFUSAL, HIDDEN_REFUSAL):
        assert "DEC-820" in reason and "W2-95" not in reason and ".py" not in reason
