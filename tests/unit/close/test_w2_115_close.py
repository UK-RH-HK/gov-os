"""W2-115 the scoped close end to end: S1 (scoped runs the selection only), S2/F2 (no full run, no list), S3 (the
record's selection is --select's), S5 (an unowned red named and opened), S7 (the record's keys), F1 (a caused red
never closes, an unowned red never refuses)."""
from __future__ import annotations

import argparse

import pytest
import yaml

from gov.cli.errors import GovError
from gov.close import attribution, command, gates, ratchet, select

from .test_w2_115_support import OTHER, OWN_SUITE, TICKET, change, project, ticket_text

CONFIG = {"path-map.yaml": {"close_workers": 1}}
FEATURE = "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x)  # changed\n"
BROKEN = "def test_broken():\n    assert 1 == 2\n"
KEYS = ("close", "commit", "selection", "runs", "review", "reds", "culprits", "clone", "nightly")


def _args(**more):
    base = {"ticket": TICKET, "select": False, "verify": False, "full": False, "timeout": None, "base": None,
            "disposition": None, "owner_decision": None, "out": None}
    base.update(more)
    return argparse.Namespace(**base)


def _record(repo):
    text = (repo.root / f"docs/close/{TICKET}/CL-{TICKET}.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---\n")[1])


@pytest.fixture
def no_lists(monkeypatch):
    """The scoped close reads and writes no accepted-reds or load-sensitive list: every reader of them fails."""
    def refuse(*a, **k):
        raise AssertionError("a list of the strict close was read")
    for name in [n for n in dir(ratchet) if not n.startswith("__") and callable(getattr(ratchet, n))]:
        monkeypatch.setattr(ratchet, name, refuse)
    monkeypatch.setattr(gates, "check_ratchet_lists", refuse)


@pytest.fixture
def runs(monkeypatch):
    seen = []
    real = attribution.run_pytest
    monkeypatch.setattr(attribution, "run_pytest", lambda tree, targets, *a, **k: seen.append(list(targets)) or real(
        tree, targets, *a, **k))
    return seen


def test_s7_a_clean_scoped_close_writes_every_key(tmp_path, no_lists, runs):
    repo = project(tmp_path)
    commit = change(repo, {"src/pkg/feature.py": FEATURE})
    result = command.run(repo.root, _args(), CONFIG)
    record = _record(repo)
    for key in KEYS:
        assert key in record, key
    assert record["close"] == "scoped" and record["commit"] == commit
    chosen = select.scoped(repo.root, TICKET)
    assert record["selection"] == {"suites": chosen["suites"], "pytest_options": chosen["pytest_options"]}  # S3
    assert record["selection"]["suites"] == [OWN_SUITE]
    assert [r["name"] for r in record["runs"]] == ["parallel", "serial"]
    assert record["runs"][0] == {"name": "parallel", "passed": 1, "failed": 0, "errors": 0, "skipped": 0}
    assert record["review"] == {"verdict": "READY", "record": None}
    assert record["reds"] == [] and record["culprits"] == []
    assert record["clone"] == {"path": ".gov-runtime/close/clone", "reused": False, "replaced": None}
    assert record["nightly"] == {"read": False, "record": None}
    assert result["close_record"] == f"docs/close/{TICKET}/CL-{TICKET}.md"
    from gov.tasks.tickets import frontmatter
    assert frontmatter(repo.root / f".tickets/{TICKET}.md")["status"] == "closed"
    assert runs == [[OWN_SUITE]]  # S1/F2: the selection only, no full-suite run
    assert all(t not in ("tests", "tests/") for targets in runs for t in targets)


def test_s5_an_unowned_red_is_named_opened_and_never_refuses(tmp_path, no_lists):
    repo = project(tmp_path, extra={f"{OWN_SUITE}test_broken.py": BROKEN})
    change(repo, {"src/pkg/feature.py": FEATURE})
    command.run(repo.root, _args(), CONFIG)  # F1: not refused
    record = _record(repo)
    [red] = record["reds"]
    assert red["test"] == f"{OWN_SUITE}test_broken.py::test_broken"
    assert red["caused"] is False and red["failure_type"] == "AssertionError" and red["reason"]
    repair = red["repair_ticket"]
    from gov.tasks.tickets import frontmatter
    front = frontmatter(repo.root / f".tickets/{repair}.md")
    assert front["assignee"] == "orchestrator" and front["status"] == "open"
    text = (repo.root / f".tickets/{repair}.md").read_text(encoding="utf-8")
    assert red["test"] in text and "AssertionError" in text


def test_f1_a_caused_red_never_closes(tmp_path, no_lists):
    repo = project(tmp_path)
    change(repo, {"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return add(x, x) + 1\n"})
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(), CONFIG)
    assert raised.value.code == "RED_CAUSED" and raised.value.exit_code == command.EXIT_CHECK_FAILED
    [red] = raised.value.details["reds"]
    assert red["caused"] is True and red["test"].startswith(OWN_SUITE)
    assert not (repo.root / f"docs/close/{TICKET}").exists()
    from gov.tasks.tickets import frontmatter
    assert frontmatter(repo.root / f".tickets/{TICKET}.md")["status"] == "in_progress"


def test_s4_a_test_that_times_out_on_both_heads_never_matches(tmp_path, no_lists):
    import importlib.util
    if importlib.util.find_spec("pytest_timeout") is None:
        pytest.skip("pytest-timeout is not installed: no per-test limit to reach")
    from .test_w2_115_support import map_data
    hangs = "import time\n\n\ndef test_hangs():\n    time.sleep(30)\n"
    repo = project(tmp_path, extra={f"{OWN_SUITE}test_hangs.py": hangs,
                                    "governance/project/test-map.yaml": yaml.safe_dump(map_data(per_test_timeout=1))})
    change(repo, {"src/pkg/feature.py": FEATURE})
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(), CONFIG)
    assert raised.value.code == "RED_CAUSED"
    [red] = raised.value.details["reds"]
    assert red["failure_type"] == "timeout" and red["caused"] is True


def test_s2_an_unmapped_change_refuses_the_close_and_runs_nothing(tmp_path, no_lists, runs):
    repo = project(tmp_path)
    change(repo, {"src/pkg/lonely.py": "VALUE = 9\n"})
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(), CONFIG)
    assert raised.value.code == "SELECTION_REFUSED" and "src/pkg/lonely.py" in raised.value.message
    assert runs == []


def test_a_ticket_without_its_acceptance_tests_is_never_closed(tmp_path, no_lists, runs):
    repo = project(tmp_path, extra={"tests/unit/test_feature.py": (
        "from pkg.feature import twice\n\n\ndef test_t():\n    assert twice(1) == 2\n")})
    repo.git("rm", "-q", "-r", OWN_SUITE)
    repo.commit("no acceptance tests yet")
    change(repo, {"src/pkg/feature.py": FEATURE})
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(), CONFIG)
    assert raised.value.code == "NO_ACCEPTANCE_TESTS" and runs == []


def test_s2_full_is_refused_in_the_scoped_close(tmp_path, no_lists, runs):
    repo = project(tmp_path)
    change(repo, {"src/pkg/feature.py": FEATURE})
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(full=True), CONFIG)
    assert raised.value.code == "SELECTION_REFUSED" and runs == []


def test_s11_a_blocking_verdict_refuses_the_close_before_any_run(tmp_path, no_lists, runs):
    import json
    repo = project(tmp_path, profile="FULL")
    change(repo, {"src/pkg/feature.py": FEATURE})
    block = {"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [
        {"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "loses work"}]},
        {"kpi": "F1", "verdict": "pass"}]}
    repo.commit("probe", f"Task: {TICKET}", "Role: independent-auditor",
                files={f"docs/probes/{TICKET}/PR-1.md": "```verdict\n" + json.dumps(block) + "\n```\n"})
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(), CONFIG)
    assert raised.value.code == "FINDING_BLOCKS" and runs == []


def test_s10_two_closes_in_a_row_reuse_the_clone(tmp_path, no_lists):
    repo = project(tmp_path, extra={f".tickets/{OTHER}.md": ticket_text(OTHER, "W-1")})
    change(repo, {"src/pkg/feature.py": FEATURE})
    command.run(repo.root, _args(), CONFIG)
    repo.git("add", "-A")
    repo.git("commit", "-q", "-m", "close the first", "--trailer", f"Task: {TICKET}")
    change(repo, {"src/pkg/feature.py": FEATURE + "# two\n"}, ticket=OTHER)
    command.run(repo.root, _args(ticket=OTHER), CONFIG)
    text = (repo.root / f"docs/close/{OTHER}/CL-{OTHER}.md").read_text(encoding="utf-8")
    second = yaml.safe_load(text.split("---\n")[1])
    assert second["clone"] == {"path": ".gov-runtime/close/clone", "reused": True, "replaced": None}
