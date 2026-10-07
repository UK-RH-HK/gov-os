"""A close closes what it measured (DEC-487, DEC-490): the tree is its commit, the store is of that commit, the
argument is a time limit, every commit of the range is somebody's, the probe record is the orchestrator's, the
test runs are the suite's own, and a close that fails at its last step leaves nothing that says it closed."""
from __future__ import annotations

import json
import os
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import yaml

from gov.cli.errors import GovError
from gov.close import command
from gov.close.command import (DEFAULT_TIMEOUT, EXIT_CHECK_FAILED, _GOVERNANCE_PREFIXES, _check_probe, _check_store,
                               _check_trailers, _check_tree, _check_unmeasured, _commits_since, _count_path,
                               _Finding, _record_and_close, _run_tests, _ticket_commits, _time_limit, _work_of, run)
from gov.store import load
from gov.tasks.tickets import frontmatter

TICKET = "T-0001"
TICKETS = frozenset({TICKET, "T-0002"})
WBS = "W1-01"
TRAILERS = (f"Task: {TICKET}", "Role: engineer", "Implements: CAP-01")
TICKET_FILE = f".tickets/{TICKET}.md"


def _args(**keys):
    return SimpleNamespace(**{"ticket": TICKET, "disposition": None, "owner_decision": None, "timeout": None, **keys})


def _nothing_counted(root):
    assert not _count_path(root, TICKET).exists(), "the refusal was counted"
    assert len(list((root / ".tickets").glob("*.md"))) == 1, "a repair ticket was opened"


# ---- the time limit ----

@pytest.mark.parametrize("given", [0, -5, 0.0, float("nan"), float("inf"), True, "60"])
def test_a_time_limit_that_is_not_a_positive_number_is_an_invalid_argument(given):
    with pytest.raises(GovError) as raised:
        _time_limit(given, {})
    assert (raised.value.code, raised.value.exit_code) == ("INVALID_TIMEOUT", 1)
    assert "--timeout" in raised.value.message
    with pytest.raises(GovError) as raised:
        _time_limit(None, {"close_timeout": given})
    assert raised.value.code == "INVALID_TIMEOUT" and "close_timeout" in raised.value.message


def test_the_time_limit_is_the_arguments_then_the_projects_then_the_default():
    assert _time_limit(5, {"close_timeout": 9}) == 5
    assert _time_limit(None, {"close_timeout": 9}) == 9
    assert _time_limit(None, {}) == DEFAULT_TIMEOUT


def test_an_invalid_time_limit_is_refused_before_anything_is_read(tmp_path):
    with pytest.raises(GovError) as raised:   # no project at all: nothing was looked for
        run(tmp_path / "nowhere", _args(timeout=0), {})
    assert raised.value.code == "INVALID_TIMEOUT"


# ---- the tree is the commit ----

def test_a_committed_tree_passes(root):
    _check_tree(root, TICKET)


def test_a_tree_that_is_not_its_commit_refuses_with_the_paths_and_is_no_finding(root):
    (root / "conftest.py").write_text("# makes every test pass\n", encoding="utf-8")
    (root / TICKET_FILE).write_text((root / TICKET_FILE).read_text(encoding="utf-8") + "\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        run(root, _args(), {})
    assert (raised.value.code, raised.value.exit_code) == ("TREE_NOT_COMMITTED", 1)
    assert raised.value.details["paths"] == [TICKET_FILE, "conftest.py"]
    assert "conftest.py" in raised.value.message and TICKET_FILE in raised.value.message
    _nothing_counted(root)


def _untracked_ticket(root, name, **keys):
    front = {"id": name, "status": "open", **keys}
    (root / ".tickets" / f"{name}.md").write_text("---\n" + yaml.safe_dump(front) + "---\n# A ticket\n",
                                                  encoding="utf-8")


def test_the_repair_ticket_a_refusal_left_refuses_no_later_close(root):
    _untracked_ticket(root, "T-0002", parent=TICKET)
    _check_tree(root, TICKET)


@pytest.mark.parametrize("keys", [{"parent": "T-0009"}, {}, {"parent": [TICKET]}])
def test_an_untracked_ticket_file_of_another_parent_or_of_none_refuses(root, keys):
    _untracked_ticket(root, "T-0002", **keys)
    with pytest.raises(GovError) as raised:
        _check_tree(root, TICKET)
    assert raised.value.details["paths"] == [".tickets/T-0002.md"]


def test_only_an_untracked_file_directly_in_the_tickets_folder_is_exempt(project):
    root = project.root
    project.commit("a tracked repair ticket", "Role: orchestrator",
                   files={".tickets/T-0005.md": f"---\nid: T-0005\nparent: {TICKET}\n---\n"})
    for rel in (".tickets/sub/T-0002.md", "docs/T-0003.md", ".tickets/T-0004.txt"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(f"---\nid: x\nparent: {TICKET}\n---\n", encoding="utf-8")
    (root / ".tickets" / "T-0005.md").write_text(f"---\nid: T-0005\nparent: {TICKET}\nstatus: closed\n---\n",
                                                 encoding="utf-8")
    with pytest.raises(GovError) as raised:
        _check_tree(root, TICKET)
    assert raised.value.details["paths"] == [".tickets/T-0004.txt", ".tickets/T-0005.md", ".tickets/sub/T-0002.md",
                                             "docs/T-0003.md"]


# ---- the store is of the commit ----

def test_a_store_older_than_the_commit_refuses_names_the_rebuild_and_is_no_finding(project):
    load(project.root)
    _check_store(project.root)
    head = project.commit("the owner supersedes a decision", "Role: owner")
    with pytest.raises(GovError) as raised:
        run(project.root, _args(), {})
    assert (raised.value.code, raised.value.exit_code) == ("STORE_STALE", 1)
    assert "gov rebuild" in raised.value.message and raised.value.details["head"] == head
    _nothing_counted(project.root)


def test_a_project_without_a_store_is_left_to_the_context(root):
    _check_store(root)   # refused where the context is built (DEC-470), with the context's reason


# ---- every commit since the ticket's first is somebody's ----

def _ways(**front):
    return _work_of({"allowed_paths": ["src/example/**", "docs/one.md"], **front}, TICKET, WBS)


def test_the_tickets_work_is_its_paths_its_acceptance_tests_and_its_own_file():
    inside, own = _ways()
    assert [inside(p) for p in ("src/example/a.py", "src/example/deep/b.py", "docs/one.md")] == [True] * 3
    assert not any(inside(p) for p in ("src/other/a.py", "src/example", "docs/one.md.bak", TICKET_FILE,
                                       f"tests/acceptance/{WBS}/test_a.py"))
    assert own("src/example/a.py") and own(TICKET_FILE) and own(f"tests/acceptance/{WBS}/test_a.py")
    assert not any(own(p) for p in (".tickets/T-0002.md", f"tests/acceptance/{WBS}0/test_a.py", "tests/unit/test_a.py",
                                    "docs/checkpoints/T-0001/CP.md", "governance/project/n.yaml"))


def test_a_ticket_without_allowed_paths_has_none_and_another_shape_is_an_error():
    inside, own = _work_of({}, TICKET, WBS)
    assert not inside("src/example/a.py") and own(TICKET_FILE)
    for paths in ("src/**", [1], {"a": 1}):
        with pytest.raises(GovError) as raised:
            _work_of({"allowed_paths": paths}, TICKET, WBS)
        assert raised.value.code == "TICKET_INVALID"


def _other(sha, *paths, **trailers):
    return {"sha": sha * 40, "parents": [], "trailers": {k: [v] for k, v in trailers.items()}, "paths": list(paths)}


@pytest.mark.parametrize("path", ["src/example/more.py", TICKET_FILE, f"tests/acceptance/{WBS}/test_a.py"])
@pytest.mark.parametrize("trailers", [{}, {"Role": "engineer"}, {"Role": "orchestrator"}, {"Role": "owner"}])
def test_a_commit_that_names_no_task_and_changes_the_tickets_work_refuses_whatever_its_role(path, trailers):
    with pytest.raises(_Finding) as raised:
        _check_unmeasured(TICKET, [_other("a", "docs/notes.md"), _other("b", "README.md", path, **trailers)],
                          _ways()[1], TICKETS)
    assert raised.value.code == "WORK_WITHOUT_TASK"
    assert "b" * 12 in raised.value.message and "task" in raised.value.message and path in raised.value.message
    assert raised.value.details["paths"] == [path]


def test_any_other_commit_refuses_nothing():
    _check_unmeasured(TICKET, [
        _other("a", "docs/adr/DEC-1.md", "docs/checkpoints/T-0001/CP.md", "docs/probes/T-0001/PR.md", "src/other/x.py",
               "notes/meeting.txt", ".tickets/T-0002.md", "governance/project/n.yaml"),
        _other("b", "src/example/theirs.py", TICKET_FILE, Task="T-0002", Role="engineer"),   # that ticket's
    ], _ways()[1], TICKETS)
    _check_unmeasured(TICKET, [], _ways()[1], TICKETS)


def test_a_commit_of_the_ticket_without_a_role_refuses_like_one_without_implements():
    whole = {"Task": [TICKET], "Role": ["engineer"], "Implements": ["CAP-01"]}
    _check_trailers([{"sha": "a" * 40, "trailers": whole}], TICKET)
    for key in ("Role", "Implements"):
        with pytest.raises(_Finding) as raised:
            _check_trailers([{"sha": "a" * 40, "trailers": {k: v for k, v in whole.items() if k != key}}], TICKET)
        assert raised.value.code == "TRAILER_MISSING" and f"{key}:" in raised.value.message
        assert "a" * 12 in raised.value.message


def test_the_installed_kernel_is_among_the_governance_files():
    assert "governance/kernel/" in _GOVERNANCE_PREFIXES and len(_GOVERNANCE_PREFIXES) == 8


def test_a_commit_without_a_task_that_changes_a_governance_file_has_the_checks_run(root):
    """``run`` gives the runner's trigger the commits of the range that name no task, beside the ticket's."""
    mine = {"sha": "a" * 40, "parents": [], "trailers": {}, "paths": ["src/example/a.py"]}
    others = [_other("b", "governance/kernel/hooks/h.sh"), _other("c", "governance/project/n.yaml", Task="T-0002")]
    (root / "tests" / "acceptance" / TICKET).mkdir(parents=True)
    (root / "tests" / "acceptance" / TICKET / "test_a.py").write_text("", encoding="utf-8")
    seen = []

    def judged(root, commits):
        seen.extend(commits)
        raise GovError("STOP", "enough")

    with patch.object(command, "_ticket_commits", return_value=[mine]), patch.object(command, "_check_tree"), \
            patch.object(command, "_tickets_of_head", return_value=TICKETS), \
            patch.object(command, "_commits_since", return_value=others), patch.object(command, "_check_trailers"), \
            patch.object(command, "_check_containment"), patch.object(command, "_check_governance", judged), \
            patch.object(command, "_run_tests", return_value=([], {"passed": 1, "failed": 0, "errors": 0})):
        with pytest.raises(GovError):
            run(root, _args(), {})
    assert [c["sha"][0] for c in seen] == ["a", "b"]


# ---- the probe record ----

def _inside(path):
    return path.startswith("src/")


def _probe(repo, probed, *trailers, commit=True, **keys):
    front = {"id": f"PR-{TICKET}", "type": "probe", "task": TICKET, "reviewer_session": "reviewer-001",
             "implementer_session": "impl-001", "reviewer_wrote_nothing": True, "commissioned_by": "orchestrator",
             "judged_by": "orchestrator", "judgement": "pass", "probed_commit": probed, **keys}
    files = {f"docs/probes/{TICKET}/PR.md": "---\n" + yaml.safe_dump(front) + "---\n\n# Probe\n"}
    if commit:
        return repo.commit("the probe record", *(trailers or ("Role: orchestrator",)), files=files)
    for rel, text in files.items():
        (repo.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo.root / rel).write_text(text, encoding="utf-8")


def _gate(repo):
    commits = _ticket_commits(repo.root, TICKET)
    _check_probe(repo.root, TICKET, commits, _commits_since(repo.root, commits), _inside, TICKETS)


def _refused(repo):
    with pytest.raises(_Finding) as raised:
        _gate(repo)
    assert raised.value.code == "PROBE_INVALID"
    return raised.value.message


def _work(repo):
    return repo.commit("work", *TRAILERS, files={"src/a.py": "a\n"})


@pytest.mark.parametrize("judgement", ["pass", "passed", " passed "])
def test_a_judgement_of_pass_or_passed_is_accepted(repo, judgement):
    _probe(repo, _work(repo), judgement=judgement)
    _gate(repo)


@pytest.mark.parametrize("judgement", ["fail", "failed", "inconclusive", "PASS", "not passed", "pass, with findings",
                                       True, 1])
def test_any_other_judgement_refuses_and_is_named(repo, judgement):
    _probe(repo, _work(repo), judgement=judgement)
    assert "judgement" in _refused(repo)


def _records(repo, probed, **judgements):
    """One commit of the orchestrator with a probe record of the probed commit per file name, each with its
    judgement."""
    files = {}
    for name, judgement in judgements.items():
        front = {"id": name, "type": "probe", "task": TICKET, "reviewer_session": "reviewer-001",
                 "implementer_session": "impl-001", "reviewer_wrote_nothing": True, "judgement": judgement,
                 "commissioned_by": "orchestrator", "judged_by": "orchestrator", "probed_commit": probed}
        files[f"docs/probes/{TICKET}/{name}.md"] = "---\n" + yaml.safe_dump(front) + "---\n\n# Probe\n"
    return repo.commit("the probe records", "Role: orchestrator", files=files)


@pytest.mark.parametrize("judgements", [{"PR": "pass", "PR-2": "fail"}, {"PR": "fail", "PR-2": "pass"},
                                        {"A": "passed", "B": "pass", "C": "fail"}, {"PR": "fail", "PR-2": "fail"}])
def test_a_failing_probe_record_refuses_whatever_another_says(repo, judgements):
    """Every record of the ticket is read (DEC-500): neither the first file nor the last decides."""
    _records(repo, _work(repo), **judgements)
    assert "judgement is 'fail'" in _refused(repo)


def test_every_probe_record_of_the_ticket_is_asked_everything(repo):
    probed = _work(repo)
    _records(repo, probed, **{"PR": "pass", "PR-2": "passed"})
    _gate(repo)
    later = repo.commit("more work", *TRAILERS, files={"src/b.py": "b\n"})
    _records(repo, later, **{"PR-2": "pass"})  # the first record is now of an earlier round
    assert "after the probed commit" in _refused(repo)


def test_a_record_of_another_ticket_or_another_type_in_the_folder_is_none_of_the_tickets(repo):
    probed = _work(repo)
    repo.commit("other records", "Role: engineer", files={
        f"docs/probes/{TICKET}/other.md": f"---\ntype: probe\ntask: T-0002\njudgement: fail\n---\n",
        f"docs/probes/{TICKET}/note.md": f"---\ntype: note\ntask: {TICKET}\njudgement: fail\n---\n"})
    with pytest.raises(_Finding) as raised:
        _gate(repo)
    assert raised.value.code == "PROBE_MISSING"
    _records(repo, probed, **{"PR-2": "pass"})
    _gate(repo)


@pytest.mark.parametrize("named", ["T-0009", "DEC-000", "T-000"])
def test_a_commit_whose_task_names_no_ticket_is_judged_as_one_without_a_task(repo, named):
    """DEC-500: on the ticket's work it refuses, and after the probed commit it makes the probe stale."""
    other = _other("b", "README.md", "src/example/more.py", Task=named, Role="engineer", Implements="CAP-01")
    with pytest.raises(_Finding) as raised:
        _check_unmeasured(TICKET, [other], _ways()[1], TICKETS)
    assert raised.value.code == "WORK_WITHOUT_TASK" and "b" * 12 in raised.value.message
    _check_unmeasured(TICKET, [_other("c", "notes/meeting.txt", Task=named)], _ways()[1], TICKETS)

    _probe(repo, _work(repo))
    _gate(repo)
    after = repo.commit("under a task that is none", f"Task: {named}", "Role: engineer", files={"src/c.py": "c\n"})
    assert "the probe is stale" in _refused(repo) and after[:12] in _refused(repo)


def test_a_commit_whose_task_names_no_ticket_and_changes_a_governance_file_has_the_checks_run(root):
    """``run`` asks the commit being closed for the project's tickets: ``T-0002`` is none of them here."""
    mine = {"sha": "a" * 40, "parents": [], "trailers": {}, "paths": ["src/example/a.py"]}
    others = [_other("b", "docs/notes.md", Task="T-0002"), _other("c", "governance/project/n.yaml", Task="T-0002"),
              _other("d", "governance/project/m.yaml", Task=TICKET)]
    (root / "tests" / "acceptance" / TICKET).mkdir(parents=True)
    (root / "tests" / "acceptance" / TICKET / "test_a.py").write_text("", encoding="utf-8")
    seen = []

    def judged(root, commits):
        seen.extend(commits)
        raise GovError("STOP", "enough")

    with patch.object(command, "_ticket_commits", return_value=[mine]), patch.object(command, "_check_tree"), \
            patch.object(command, "_commits_since", return_value=others), patch.object(command, "_check_trailers"), \
            patch.object(command, "_check_containment"), patch.object(command, "_check_governance", judged), \
            patch.object(command, "_run_tests", return_value=([], {"passed": 1, "failed": 0, "errors": 0})):
        with pytest.raises(GovError):
            run(root, _args(), {})
    assert [c["sha"][0] for c in seen] == ["a", "b", "c"]


def test_a_probe_record_no_commit_holds_refuses(repo):
    _probe(repo, _work(repo), commit=False)
    said = _refused(repo)
    assert "not committed" in said and f"docs/probes/{TICKET}/PR.md" in said


@pytest.mark.parametrize("trailers", [TRAILERS, ("Role: engineer",), (f"Task: {TICKET}",),
                                      ("Role: orchestrator", "Role: engineer")])
def test_a_probe_record_committed_without_the_orchestrators_role_alone_refuses(repo, trailers):
    committed = _probe(repo, _work(repo), *trailers)
    said = _refused(repo)
    assert "orchestrator" in said and committed[:12] in said


def test_a_probe_record_the_orchestrator_committed_and_another_changed_refuses(repo):
    probed = _work(repo)
    _probe(repo, probed)
    _gate(repo)
    changed = _probe(repo, probed, "Role: independent-test-designer", judgement="passed")
    assert changed[:12] in _refused(repo)


@pytest.mark.parametrize("name", ["HEAD", "main", "HEAD~0", "a-tag", "abbreviated"])
def test_a_probed_commit_given_as_a_name_refuses(repo, name):
    probed = _work(repo)
    repo.git("tag", "a-tag")
    _probe(repo, probed[:10] if name == "abbreviated" else name)
    assert "not as a full commit id" in _refused(repo)


def test_a_commit_with_the_reviewers_role_refuses_wherever_it_lies_in_the_range(repo):
    _work(repo)
    reviewers = repo.commit("found while probing", "Role: independent-auditor", files={"docs/notes.md": "n\n"})
    _probe(repo, repo.commit("more work", *TRAILERS, files={"src/b.py": "b\n"}))
    said = _refused(repo)
    assert "reviewer's role" in said and reviewers[:12] in said


def test_a_reviewers_commit_before_the_tickets_first_is_outside_its_range(repo):
    repo.commit("an audit of another ticket", "Role: independent-auditor", "Task: T-0002")
    _probe(repo, _work(repo))
    _gate(repo)


def test_a_commit_without_a_task_inside_the_tickets_paths_after_the_probed_commit_makes_the_probe_stale(repo):
    _probe(repo, _work(repo))
    repo.commit("elsewhere, no task", files={"docs/notes.md": "n\n"})
    repo.commit("another ticket's", "Task: T-0002", "Role: engineer", files={"src/theirs.py": "t\n"})
    _gate(repo)
    rewrite = repo.commit("rewrite, no task", files={"src/a.py": "rewritten\n"})
    said = _refused(repo)
    assert "stale" in said and rewrite[:12] in said and "src/a.py" in said


def test_a_merge_of_the_ticket_is_judged_with_the_paths_it_brings_after_the_probed_commit(repo):
    _probe(repo, _work(repo))
    repo.git("checkout", "-q", "-b", "side")
    repo.commit("another ticket's work on the side", "Task: T-0002", "Role: engineer", files={"src/side.py": "s\n"})
    repo.git("checkout", "-q", "main")
    repo.git("merge", "-q", "--no-ff", "--no-gpg-sign", "-m", "merge\n\n" + "\n".join(TRAILERS) + "\n", "side")
    merge = repo.git("rev-parse", "HEAD").strip()
    said = _refused(repo)
    assert merge[:12] in said and "src/side.py" in said


# ---- the test runs ----

def _tests(root, **files):
    for name, text in files.items():
        path = root / "tests" / "acceptance" / WBS / f"{name}.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root / "tests" / "acceptance" / WBS


FAILS = "def test_fail():\n    assert False\n"
PLACES = ("PYTHONUSERBASE", "PYTHONPYCACHEPREFIX", "PYTHONDONTWRITEBYTECODE")  # no switches: where things are
SKIPPED ="import pytest\n\n\n@pytest.mark.skip(reason='not now')\ndef test_skipped():\n    assert False\n"


@pytest.mark.parametrize("options", ["--collect-only", "--deselect tests/acceptance/W1-01/test_a.py::test_fail",
                                     "-k nothing_of_that_name", "--co -q"])
def test_options_of_the_callers_environment_do_not_reach_the_run(tmp_path, monkeypatch, options):
    monkeypatch.setenv("PYTEST_ADDOPTS", options)
    monkeypatch.setenv("PYTEST_PLUGINS", "a_plugin_that_is_not_installed")
    findings, counts = _run_tests(tmp_path, _tests(tmp_path, test_a=FAILS), 60)
    assert counts["failed"] == 1 and any("test_fail" in finding for finding in findings)
    assert os.environ["PYTEST_ADDOPTS"] == options, "the caller's own environment was changed"


def test_nothing_else_of_the_callers_environment_is_taken_away(tmp_path, monkeypatch):
    seen = {}

    def fake_run(cmd, **keys):
        seen.update(keys["env"])
        return SimpleNamespace(returncode=0, stdout="1 passed in 0.01s\n", stderr="")

    monkeypatch.setenv("PYTEST_ADDOPTS", "--collect-only")
    monkeypatch.setenv("PYTHONPATH", "/elsewhere")
    monkeypatch.setattr("gov.close.command.subprocess.run", fake_run)
    before = {key: value for key, value in os.environ.items()
              if key != "PYTEST_ADDOPTS" and (not key.startswith("PYTHON") or key in PLACES)}
    _run_tests(tmp_path, _tests(tmp_path, test_a=""), 60)
    assert seen == before | {"PYTHONPATH": str(tmp_path / "src")}


@pytest.mark.parametrize("files", [{"test_a": SKIPPED}, {"test_a": SKIPPED, "test_b": SKIPPED},
                                   {"test_a": "import pytest\n\n\n@pytest.mark.xfail\ndef test_x():\n    assert False\n"}])
def test_an_acceptance_run_in_which_no_test_passed_is_a_finding(tmp_path, files):
    findings, counts = _run_tests(tmp_path, _tests(tmp_path, **files), 60)
    assert counts["passed"] == 0 and len(findings) == 1 and "no test passed" in findings[0]


def test_one_passing_test_beside_a_skipped_one_is_measured_and_a_regression_run_may_pass_none(tmp_path):
    tests = _tests(tmp_path, test_a=SKIPPED, test_b="def test_b():\n    assert True\n")
    assert _run_tests(tmp_path, tests, 60) == ([], {"passed": 1, "failed": 0, "errors": 0, "skipped": 1})
    skipped = _tests(tmp_path / "other", test_a=SKIPPED)
    assert _run_tests(tmp_path / "other", skipped, 60, none_collected_ok=True)[0] == []


# ---- the last step ----

def _says_closed(root):
    """What in the project says the ticket closed: its status, a close record, a checkpoint "ticket closed"."""
    said = [str(path.relative_to(root)) for folder in ("docs/close", "docs/checkpoints")
            for path in sorted((root / folder).rglob("*.md"))]
    if frontmatter(root / TICKET_FILE)["status"] == "closed":
        said.append("the ticket's status")
    return said


def _tool_that_fails_on_closing(root):
    tool = root / "governance" / "kernel" / "bin" / "tk"
    real = tool.with_name("tk-as-it-was")
    tool.rename(real)
    tool.write_text('#!/bin/sh\nif [ "$1" = "close" ]; then echo "planted" >&2; exit 7; fi\n'
                    f'exec "{real}" "$@"\n', encoding="utf-8")
    tool.chmod(0o755)


def test_a_close_records_and_closes(root):
    close_record, checkpoint = _record_and_close(root, TICKET, {"packet_hash": "ab"}, ["src/a.py"])
    assert close_record == f"docs/close/{TICKET}/CL-{TICKET}.md" and (root / checkpoint).is_file()
    assert frontmatter(root / close_record)["outputs"] == ["src/a.py", close_record, checkpoint]
    assert _says_closed(root) == [close_record, checkpoint, "the ticket's status"]


def test_a_ticket_tool_that_fails_on_closing_leaves_nothing_that_says_the_ticket_closed(root):
    _tool_that_fails_on_closing(root)
    with pytest.raises(GovError) as raised:
        _record_and_close(root, TICKET, {}, [])
    assert raised.value.code == "TICKET_TOOL_FAILED" and "not_taken_back" not in raised.value.details
    assert _says_closed(root) == []


def test_an_absent_ticket_tool_leaves_nothing_that_says_the_ticket_closed(root, monkeypatch):
    (root / "governance" / "kernel" / "bin" / "tk").unlink()
    monkeypatch.setattr("gov.close.tool.shutil.which", lambda name: None)
    with pytest.raises(GovError) as raised:
        _record_and_close(root, TICKET, {}, [])
    assert raised.value.code == "TICKET_TOOL_ABSENT" and _says_closed(root) == []


def test_a_close_record_that_cannot_be_written_leaves_no_checkpoint_and_the_ticket_open(root):
    (root / "docs").mkdir()
    (root / "docs" / "close").write_text("a file where the folder goes\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        _record_and_close(root, TICKET, {}, [])
    assert (raised.value.code, raised.value.exit_code) == ("CLOSE_RECORD_FAILED", 1)
    assert not list((root / "docs" / "checkpoints").rglob("*.md"))
    assert frontmatter(root / TICKET_FILE)["status"] == "in_progress"


def test_the_record_of_an_earlier_close_is_put_back_as_it_was(root):
    earlier = root / "docs" / "close" / TICKET / f"CL-{TICKET}.md"
    earlier.parent.mkdir(parents=True)
    earlier.write_bytes(b"---\r\nid: CL\r\nstatus: ACTIVE\r\n---\r\nthe first close\r\n")
    _tool_that_fails_on_closing(root)
    with pytest.raises(GovError):
        _record_and_close(root, TICKET, {"packet_hash": "new"}, [])
    assert earlier.read_bytes() == b"---\r\nid: CL\r\nstatus: ACTIVE\r\n---\r\nthe first close\r\n"
    assert not list((root / "docs" / "checkpoints").rglob("*.md"))


def test_a_record_that_cannot_be_taken_back_is_named_in_the_error(root, monkeypatch):
    _tool_that_fails_on_closing(root)
    real = type(root).unlink

    def unlink(self, **keys):   # the records stay; what a whole write leaves beside a file goes as ever
        if self.suffix == ".md":
            raise OSError("planted unlink")
        real(self, **keys)

    monkeypatch.setattr(type(root), "unlink", unlink)
    with pytest.raises(GovError) as raised:
        _record_and_close(root, TICKET, {}, [])
    assert raised.value.code == "TICKET_TOOL_FAILED"
    assert len(raised.value.details["not_taken_back"]) == 2 and "could not be taken back" in raised.value.message


def test_a_finding_and_could_not_measure_are_two_ways_out(root):
    """A finding is counted with a repair ticket (exit code 3); what precedes the measuring is neither."""
    with patch.object(command, "_ticket_commits", return_value=[]), patch.object(command, "_commits_since",
                                                                               return_value=[]):
        with pytest.raises(GovError) as raised:
            run(root, _args(), {})
    # every gate was asked (DEC-492): the one refusal holds each gate's finding, counted once
    assert (raised.value.code, raised.value.exit_code) == ("CHECK_FAILED", EXIT_CHECK_FAILED)
    assert [part["code"] for part in raised.value.details["parts"]] == [
        "TRAILER_MISSING", "NO_ACCEPTANCE_TESTS", "CHECKPOINT_MISSING", "CONTEXT_FAILED"]
    assert len(raised.value.details["findings"]) == 4
    assert [part.split(":")[0] for part in raised.value.details["not_measured"]] == [
        f"the containment of the commits of {TICKET}", f"the acceptance run of {TICKET}"]
    assert json.loads(_count_path(root, TICKET).read_text(encoding="utf-8"))["count"] == 1
    assert len(list((root / ".tickets").glob("*.md"))) == 2
