"""Round 2 of the commits measured by a decision (DEC-923 item 2): ``gov.close.gates.decision_records`` counts a
decision-record commit of DEC-891's records under decisions each ever ACCEPTED, and a commit the owner-committed
lists name under an ACCEPTED owner decision; a ``Role: owner`` trailer alone measures nothing (DEC-906)."""
from __future__ import annotations

import pytest

from gov.close.gates import decision_records
from gov.close.repo import read_commits

REGISTER = "docs/DECISION_REGISTER.md"
OWNER = "ACCEPTED (owner, 2026-10-26)"


def _register(repo, statuses: dict[str, str], text: str = "") -> None:
    body = "".join(f"### {dec} — A decision\n- **Status:** {status}\n- **Decision:** {text}\n\n"
                   for dec, status in statuses.items())
    repo.commit("the register", "Role: owner", files={REGISTER: "# Register\n\n" + body})


def _measured(repo, sha: str, **lists) -> bool:
    settings = {"decision_register": REGISTER, **lists}
    return sha in decision_records(repo.root, read_commits(repo.root, "-1", sha), settings)


def _record(repo, message: str = "DEC-100: the record", files=None) -> str:
    return repo.commit(message, "Task: decision-record", "Role: orchestrator",
                       files=files or {"docs/plan/WAVE.md": "a plan\n"})


@pytest.mark.parametrize("status", [
    "ACCEPTED (delegated, orchestrator, 2026-10-26)",
    "ACCEPTED (orchestrator, delegated under the prompt §7)",
    "ACCEPTED (owner, 2026-10-20) · **Changed by:** DEC-101",
    "SUPERSEDED by DEC-101 (2026-10-21; it was ACCEPTED, owner, 2026-10-20)",
    "SUPERSEDED by DEC-101 (2026-10-21; it was ACCEPTED, delegated, orchestrator, 2026-10-20)",
])
def test_a_record_under_a_decision_ever_accepted_is_measured(repo, status):
    _register(repo, {"DEC-100": status})
    assert _measured(repo, _record(repo))


@pytest.mark.parametrize("status", ["PROPOSED", "REJECTED (owner, 2026-10-20)", "SUPERSEDED by DEC-101"])
def test_a_record_under_a_decision_never_accepted_is_not_measured(repo, status):
    _register(repo, {"DEC-100": status})
    assert not _measured(repo, _record(repo))


def test_a_record_of_dec_891s_records_with_the_tickets_own_file_is_measured(repo):
    _register(repo, {"DEC-100": OWNER})
    files = {".tickets/T-0001.md": "a ticket\n", "docs/checkpoints/T-0001/c.md": "x\n", "docs/close/c.md": "x\n",
             "docs/probes/p.md": "x\n", "governance/project/path-map.yaml": "a: 1\n"}
    assert _measured(repo, _record(repo, files=files))


def test_a_record_that_also_changes_an_assessment_report_is_not_measured(repo):
    _register(repo, {"DEC-100": OWNER})
    assert not _measured(repo, _record(repo, files={"docs/plan/WAVE.md": "x\n", "docs/assessment/H.md": "x\n"}))


def test_a_record_naming_one_decision_never_accepted_beside_an_accepted_one_is_not_measured(repo):
    _register(repo, {"DEC-100": OWNER, "DEC-101": "PROPOSED"})
    assert not _measured(repo, _record(repo, message="DEC-100 and DEC-101: the records"))


def test_a_code_commit_with_a_role_owner_trailer_alone_is_not_measured(repo):
    _register(repo, {"DEC-100": OWNER})
    sha = repo.commit("DEC-100: the owner's code", "Task: decision-record", "Role: owner",
                      files={"src/example/code.py": "x = 1\n"})
    assert not _measured(repo, sha)


def _listed_code(repo, status: str = OWNER) -> str:
    sha = repo.commit("work", "Role: owner", files={"src/example/code.py": "x = 1\n"})
    _register(repo, {"DEC-100": status}, text=f"the commit {sha} is accepted")
    return sha


def test_a_code_commit_accepted_history_names_under_an_owner_decision_is_measured(repo):
    sha = _listed_code(repo)
    assert _measured(repo, sha, accepted_history=[{"commit": sha[:12], "decision": "DEC-100"}])


def test_an_accepted_history_entry_under_a_superseded_owner_decision_measures_nothing(repo):
    sha = _listed_code(repo, "ACCEPTED (owner, 2026-10-20) · superseded by DEC-101")
    assert not _measured(repo, sha, accepted_history=[{"commit": sha, "decision": "DEC-100"}])


def test_a_code_commit_acceptance_exemptions_names_by_its_full_id_is_measured(repo):
    sha = _listed_code(repo)
    assert _measured(repo, sha, acceptance_exemptions=[{"commit": sha, "decision": "DEC-100"}])


@pytest.mark.parametrize("case", ["abbreviated", "delegated", "not-named"])
def test_an_acceptance_exemption_that_is_not_exact_or_not_the_owners_measures_nothing(repo, case):
    sha = _listed_code(repo, "ACCEPTED (delegated, orchestrator, 2026-10-26)" if case == "delegated" else OWNER)
    if case == "not-named":
        _register(repo, {"DEC-100": OWNER}, text="no commit")
    entry = {"commit": sha[:12] if case == "abbreviated" else sha, "decision": "DEC-100"}
    assert not _measured(repo, sha, acceptance_exemptions=[entry])
