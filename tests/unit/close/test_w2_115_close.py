"""W2-115 the scoped close end to end: S1 (scoped runs the selection only), S2/F2 (no full run, no list), S3 (the
record's selection is --select's), S5 (an unowned red named and opened), S7 (the record's keys), F1 (a caused red
never closes, an unowned red never refuses)."""
from __future__ import annotations

import argparse

import pytest
import yaml

from gov.cli.errors import GovError
from gov.close import attribution, command, gates, ratchet, select

from .test_w2_115_support import OTHER, OWN_SUITE, TICKET, change, green_night, project, ticket_text

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
    """The scoped close reads no load-sensitive list and writes no list; of the accepted reds it reads only the
    counted entries (W2-194 S3), none in these projects: every other reader of the lists fails."""
    def refuse(*a, **k):
        raise AssertionError("a list of the strict close was read")
    real = ratchet.counted_entries

    def counted(root, key, commit="HEAD"):
        assert key == ratchet.ACCEPTED_REDS, f"the scoped close read {key}"
        found = real(root, key, commit)
        assert found == ([], []), found
        return found
    for name in ("apply_accepted_reds", "covers"):
        monkeypatch.setattr(ratchet, name, refuse)
    monkeypatch.setattr(ratchet, "counted_entries", counted)
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


def test_s5_an_unowned_red_is_named_and_opens_no_repair_ticket_and_never_refuses(tmp_path, no_lists):
    """Rewrite-Reason: W2-193 S6 (EMERGENCY-2 4.2, CAP-31: a known bug is a fix, not a ticket); was
    ``test_s5_an_unowned_red_is_named_opened_and_never_refuses``, which asserted a repair ticket for the red."""
    repo = project(tmp_path, extra={f"{OWN_SUITE}test_broken.py": BROKEN})
    green_night(repo)  # P1-K (a): an unowned red needs a green base on HEAD's line to be judged against
    change(repo, {"src/pkg/feature.py": FEATURE})
    command.run(repo.root, _args(), CONFIG)  # F1: not refused
    record = _record(repo)
    [red] = record["reds"]
    assert red["test"] == f"{OWN_SUITE}test_broken.py::test_broken"
    assert red["caused"] is False and red["failure_type"] == "AssertionError" and "base" in red["reason"].lower()
    assert "repair_ticket" in red and red["repair_ticket"] is None
    assert sorted(p.name for p in (repo.root / ".tickets").glob("*.md")) == [f"{TICKET}.md"]


def test_s3_with_no_green_record_a_red_the_oldest_own_parent_has_is_not_the_changes(tmp_path, no_lists):
    """W2-193 S3 (supersedes DEC-1150 (2)): no green base on HEAD's line, so the red is judged at the parent of the
    ticket's oldest own commit; red there with the same failure type, it is not the change's: the close passes,
    names the base and where it came from, and opens no repair ticket for the red.

    Rewrite-Reason: W2-193 S6 (EMERGENCY-2 4.2, CAP-31): the record lists the base red with ``repair_ticket`` null."""
    repo = project(tmp_path, extra={f"{OWN_SUITE}test_broken.py": BROKEN})
    parent = repo.git("rev-parse", "HEAD").strip()
    change(repo, {"src/pkg/feature.py": FEATURE})
    command.run(repo.root, _args(), CONFIG)
    record = _record(repo)
    assert record["base"] == parent and record["base_from"] == "ticket" and record["base_run"] is None
    [red] = record["reds"]
    assert red["caused"] is False and "repair_ticket" in red and red["repair_ticket"] is None
    assert "base" in red["reason"].lower()
    assert sorted(p.name for p in (repo.root / ".tickets").glob("*.md")) == [f"{TICKET}.md"]


def test_f1_with_no_green_record_a_red_the_oldest_own_parent_lacks_is_caused(tmp_path, no_lists):
    """W2-193 F1: judged at the ticket's parent, a red green there is the change's: refused, no record, no repair
    ticket."""
    repo = project(tmp_path)
    change(repo, {f"{OWN_SUITE}test_broken.py": "from pkg.feature import twice\n\n\ndef test_broken():\n"
                                                "    assert twice(1) == 3\n"})
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(), CONFIG)
    assert raised.value.code == "RED_CAUSED"
    [red] = raised.value.details["reds"]
    assert red["caused"] is True and raised.value.details["base_from"] == "ticket"
    assert not red.get("repair_ticket")
    assert not (repo.root / f"docs/close/{TICKET}").exists()
    assert sorted(p.name for p in (repo.root / ".tickets").glob("*.md")) == [f"{TICKET}.md"]


@pytest.mark.parametrize("entry", ["test_broken.py::test_broken", "test_broken.py"])
def test_s4_a_latency_entry_red_gets_three_rounds_each_way_in_the_close(tmp_path, no_lists, runs, entry):
    """eng-3: end to end, a red that a ``latency`` entry of the serial-only list names (the node id, or its file) is
    run in the close's phase, then 3 rounds alone on the head and 3 on the head without the change."""
    test = f"{OWN_SUITE}test_broken.py::test_broken"
    repo = project(tmp_path, extra={f"{OWN_SUITE}test_broken.py": BROKEN,
                                    "tests/acceptance/serial-only.txt": f"# the list\n{OWN_SUITE}{entry}  # serial: "
                                                                        "latency: timed\n"})
    green_night(repo)  # P1-K (a): the head without the change is the green base
    change(repo, {"src/pkg/feature.py": FEATURE})
    command.run(repo.root, _args(), CONFIG)
    [red] = _record(repo)["reds"]
    assert red["test"] == test and red["caused"] is False
    assert runs[1] == [f"{OWN_SUITE}{entry}"]  # the serial phase ran it (its run)
    assert runs[2:] == [[test]] * 6, runs  # then 3 rounds alone on the head, 3 on the head without the change


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


def test_f1_an_untrailered_slip_after_the_green_base_is_caused_and_never_closes(tmp_path, no_lists):
    """F-1: a green test, then an untrailered commit that breaks it, then the ticket's trailered work: the red is
    judged against the green base, so it is the change's: RED_CAUSED, no record, no repair ticket."""
    repo = project(tmp_path)
    green_night(repo)
    repo.commit("slip", files={"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return 0\n"})
    change(repo, {"src/pkg/other.py": "def other():\n    return 1  # c\n"})
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(), CONFIG)
    assert raised.value.code == "RED_CAUSED"
    [red] = raised.value.details["reds"]
    assert red["caused"] is True and red["test"].startswith(OWN_SUITE)
    assert not red.get("repair_ticket")
    assert not (repo.root / f"docs/close/{TICKET}").exists()
    assert sorted(p.name for p in (repo.root / ".tickets").glob("*.md")) == [f"{TICKET}.md"]


def test_f1_a_red_is_run_on_the_green_base_even_where_a_full_green_night_names_it(tmp_path, no_lists, monkeypatch):
    """reds-6 (S4, F-1): the green base is a full green night's head. The night does not excuse the red, so the red
    is run once on the green base (green there) before it is judged the change's: RED_CAUSED."""
    import json
    repo = project(tmp_path)
    green = repo.git("rev-parse", "HEAD").strip()
    repo.commit("night", files={f"docs/close/nightly/NR-20261101T010000Z-{green[:12]}.json": json.dumps(
        {"verdict": "green", "head": green, "scope": "full", "failures": []}) + "\n"})
    repo.commit("slip", files={"src/pkg/feature.py": "from pkg.core import add\n\n\ndef twice(x):\n    return 0\n"})
    change(repo, {"src/pkg/other.py": "def other():\n    return 1  # c\n"})
    runs = []
    real = attribution.run_alone
    monkeypatch.setattr(attribution, "run_alone", lambda c, t, o, f, to, tag: runs.append(
        (tag, attribution._git(c, "rev-parse", "HEAD").stdout.strip())) or real(c, t, o, f, to, tag))
    with pytest.raises(GovError) as raised:
        command.run(repo.root, _args(), CONFIG)
    assert raised.value.code == "RED_CAUSED"
    [red] = raised.value.details["reds"]
    assert red["caused"] is True and "nightly record" not in red["reason"]
    assert [(tag, head) for tag, head in runs if tag.startswith("without")] == [("without-0", green)]
