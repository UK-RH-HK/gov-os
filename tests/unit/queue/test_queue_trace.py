"""W2-206 IT-1, IT-2: which record files a change holds, and the trace that never refuses."""
from __future__ import annotations

import pytest

from gov.queue import trace
from queue_support import Repo

REGISTER = "docs/REGISTER.md"


def _entry(number: str, text: str) -> str:
    return f"### DEC-{number} — A decision\n- **Status:** ACCEPTED (owner)\n- **Decision:** {text}\n\n"


def _record(record_id: str, text: str = "body") -> str:
    return f"---\nid: {record_id}\ntype: specification\nstatus: ACTIVE\n---\n{text}\n"


@pytest.fixture
def repo(tmp_path) -> Repo:
    made = Repo(tmp_path / "project")
    made.commit("base", files={
        "governance/project/path-map.yaml": f"decision_register: {REGISTER}\n",
        REGISTER: _entry("001", "one") + _entry("002", "two") + _entry("003", "three"),
        "docs/spec.md": _record("SPEC-001"),
        "docs/gone.md": _record("SPEC-003"),
        "src/widget.py": "VALUE = 1\n",
    })
    return made


def test_the_records_of_a_change_are_its_record_files_and_its_register_entries(repo):
    repo.git("checkout", "-q", "-b", "work")
    (repo.root / "docs" / "gone.md").unlink()
    tip = repo.commit("work", files={
        REGISTER: _entry("001", "changed") + _entry("002", "two") + _entry("004", "four"),
        "docs/spec.md": _record("SPEC-001", "changed"),
        "docs/new.md": _record("SPEC-002"),
        "docs/plain.md": "no front matter\n",
        "docs/no-id.md": "---\ntype: specification\nstatus: ACTIVE\n---\n",
        "docs/broken.md": "---\n: [\n---\n",
        "src/widget.py": "VALUE = 2\n",
    })
    assert trace.records(repo.root, tip, "main", tip) == {
        "DEC-001": REGISTER, "DEC-003": REGISTER, "DEC-004": REGISTER, "SPEC-001": "docs/spec.md",
        "SPEC-002": "docs/new.md", "SPEC-003": "docs/gone.md"}


def test_a_record_that_moved_is_named_at_its_new_path(repo):
    repo.git("checkout", "-q", "-b", "work")
    repo.git("mv", "docs/gone.md", "docs/zz-moved.md")
    tip = repo.commit("moved")
    assert trace.records(repo.root, tip, "main", tip) == {"SPEC-003": "docs/zz-moved.md"}


def test_only_the_change_s_own_entries_count_not_the_base_s(repo):
    repo.branch("work", {"docs/new.md": _record("SPEC-002")})
    base = repo.commit("base moves", files={REGISTER: _entry("001", "the base's own edit")})
    repo.git("merge", "-q", "--no-ff", "--no-gpg-sign", "work", "-m", "merged")
    assert trace.records(repo.root, repo.sha(), base, repo.sha("work")) == {"SPEC-002": "docs/new.md"}


def test_a_change_with_no_record_is_an_empty_complete_entry(repo):
    repo.branch("work", {"src/widget.py": "VALUE = 2\n"})
    tip = repo.sha("work")
    assert trace.landing(repo.root, tip, [{"ticket": "T-a", "since": repo.sha("main"), "tip": tip}]) == {
        "T-a": {"records": [], "complete": True}}


@pytest.mark.parametrize("limit", ["0.001", "no number", "0", "inf"])
def test_a_trace_that_overruns_or_has_no_usable_limit_is_unavailable(repo, monkeypatch, limit):
    monkeypatch.setenv(trace.LIMIT_VARIABLE, limit)
    tip = repo.sha()
    said = trace.landing(repo.root, tip, [{"ticket": "T-a", "since": tip, "tip": tip},
                                          {"ticket": "T-b", "since": tip, "tip": tip}])
    assert set(said) == {"T-a", "T-b"}
    assert all(entry.startswith("unavailable (") and entry.endswith(")") for entry in said.values())


def test_a_trace_that_fails_is_unavailable_with_its_reason(repo):
    tip = repo.sha()
    said = trace.landing(repo.root, tip, [{"ticket": "T-a", "since": "no-such-commit", "tip": tip}])
    assert said["T-a"].startswith("unavailable (") and "no-such-commit" in said["T-a"]
