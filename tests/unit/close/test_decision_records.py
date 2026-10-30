"""Decision-record commits measured by their decision (DEC-896 item 1): ``gov.close.gates.decision_records``."""
from __future__ import annotations

from gov.close.gates import decision_records
from gov.close.repo import read_commits

REGISTER = "docs/DECISION_REGISTER.md"
SETTINGS = {"decision_register": REGISTER}


def _register(status: str) -> str:
    return f"# Register\n\n### DEC-100 — A decision\n- **Status:** {status}\n- **Decision:** something\n"


def _measured(repo, *trailers, files=None, message="DEC-100: the record of the owner's decision"):
    repo.commit("the register", "Role: owner", files={REGISTER: _register("ACCEPTED (owner, 2026-10-22)")})
    sha = repo.commit(message, *trailers, files=files or {"docs/plan/WAVE.md": "a plan\n"})
    commits = read_commits(repo.root, "-1", sha)
    return sha in decision_records(repo.root, commits, SETTINGS)


def test_a_decision_record_commit_of_governance_records_under_an_accepted_decision_is_measured(repo):
    assert _measured(repo, "Task: decision-record", "Role: orchestrator")


def test_a_commit_naming_no_task_is_not_measured_by_the_decision_it_names(repo):
    assert not _measured(repo, "Role: orchestrator")


def test_a_commit_whose_task_is_another_word_is_not_measured_by_its_decision(repo):
    assert not _measured(repo, "Task: housekeeping", "Role: orchestrator")


def test_a_decision_record_commit_that_also_changes_code_is_not_measured(repo):
    assert not _measured(repo, "Task: decision-record", "Role: orchestrator",
                         files={"docs/plan/WAVE.md": "a plan\n", "src/example/code.py": "x = 1\n"})


def test_a_decision_record_commit_naming_a_decision_not_accepted_is_not_measured(repo):
    repo.commit("the register", "Role: owner", files={REGISTER: _register("PROPOSED")})
    sha = repo.commit("DEC-100: proposed", "Task: decision-record", files={"docs/plan/WAVE.md": "a plan\n"})
    assert sha not in decision_records(repo.root, read_commits(repo.root, "-1", sha), SETTINGS)
