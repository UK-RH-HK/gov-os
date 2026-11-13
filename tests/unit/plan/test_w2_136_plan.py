"""W2-136 unit tests: gov plan's batches, waits, findings and ready list, on planted ticket stores (S1-S8, S10)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from gov.cli.main import main
from gov.plan.derive import make_plan
from gov.plan.tickets import wait_id

from .w2_136_store import plant, run, run_json, ticket, tree_hash

SRC = Path(__file__).resolve().parents[3] / "src" / "gov"


def batches(out: str) -> list[list[str]]:
    return [line.split(": ", 1)[1].split(", ") for line in out.splitlines() if re.match(r"batch \d+: ", line)]


# -- S1: the command, its lines, --json and exit codes -------------------------------------------------------------

def test_the_first_line_the_batches_and_the_waits(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", writes=["src/a.py"]), ticket("T-2", writes=["src/a.py"]),
          ticket("T-3", writes=["src/c.py"]))
    code, out = run(tmp_path, capsys, "--open")
    lines = out.splitlines()
    assert code == 0
    assert lines[0] == "gov plan: 3 tickets, 2 batches, 1 waits (WRITES_OVERLAP)"
    assert lines[1] == "batch 1: T-1, T-3"
    assert lines[2] == "batch 2: T-2"
    assert lines[3] == "T-2 waits for T-1 (WRITES_OVERLAP src/a.py)"


def test_only_open_and_in_progress_tickets_are_planned(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", status="in_progress"), ticket("T-2", status="closed"), ticket("T-3"))
    code, out = run(tmp_path, capsys)
    assert out.splitlines()[0].startswith("gov plan: 2 tickets, 1 batches, 0 waits (none)")
    assert batches(out) == [["T-1", "T-3"]]


def test_json_gives_the_same_plan_in_the_shared_envelope(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", writes=["src/**"]), ticket("T-2", writes=["src/x/y.py"]))
    code, envelope = run_json(tmp_path, capsys, "--open")
    assert code == 0
    assert set(envelope) == {"ok", "command", "result", "session"}
    assert envelope["ok"] is True and envelope["command"] == "plan"
    result = envelope["result"]
    assert result["batches"] == [["T-1"], ["T-2"]]
    assert result["waits"] == [{"ticket": "T-2", "waits_for": "T-1", "code": "WRITES_OVERLAP", "what": "src/x/y.py"}]
    _, text = run(tmp_path, capsys, "--open")
    assert result["lines"] == text.splitlines()


def test_no_ticket_store_cannot_run(tmp_path, capsys):
    code, out = run(tmp_path, capsys, "--open")
    assert code == 2
    code, envelope = run_json(tmp_path, capsys, "--open")
    assert code == 2 and envelope["ok"] is False and envelope["error"]["code"] == "PLAN_CANNOT_RUN"


def test_a_ticket_that_cannot_be_read_stops_the_plan(tmp_path, capsys):
    plant(tmp_path, ticket("T-1"))
    (tmp_path / ".tickets" / "T-2.md").write_text("---\nid: [unclosed\n---\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["plan", "--root", str(tmp_path), "--open"]) == 2
    assert "PLAN_CANNOT_RUN: .tickets/T-2.md" in capsys.readouterr().err


def test_tickets_names_the_planned_tickets_and_an_unknown_one_cannot_run(tmp_path, capsys):
    plant(tmp_path, ticket("T-1"), ticket("T-2", wbs="W9-77"), ticket("T-3"))
    code, out = run(tmp_path, capsys, "--tickets", "T-1", "W9-77")
    assert code == 0 and batches(out) == [["T-1", "T-2"]]
    code, _ = run(tmp_path, capsys, "--tickets", "T-9")
    assert code == 2


# -- S2: the order --------------------------------------------------------------------------------------------------

def test_a_needed_path_an_unfinished_ticket_writes_makes_it_wait_naming_the_path(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", writes=["src/gov/x/**"]), ticket("T-2", writes=["src/b.py"],
                                                                     needs=["src/gov/x/api.py"]))
    code, out = run(tmp_path, capsys)
    assert batches(out) == [["T-1"], ["T-2"]]
    assert "T-2 waits for T-1 (NEEDS_WHAT_WRITES src/gov/x/api.py)" in out.splitlines()


def test_a_needed_path_a_closed_ticket_wrote_orders_nothing(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", status="closed", writes=["src/x.py"]),
          ticket("T-2", writes=["src/b.py"], needs=["src/x.py"]))
    _, out = run(tmp_path, capsys)
    assert batches(out) == [["T-2"]]


def test_depends_on_and_an_unfinished_waits_on_make_it_wait(tmp_path, capsys):
    plant(tmp_path, ticket("T-1"), ticket("T-2", depends_on=["T-1"]),
          ticket("T-3", waits_on=["T-1 — its schema first"]), ticket("T-4", status="closed"),
          ticket("T-5", waits_on=["T-4 — closed already"], depends_on=["T-4"]))
    _, out = run(tmp_path, capsys)
    assert batches(out) == [["T-1", "T-5"], ["T-2", "T-3"]]
    assert "T-2 waits for T-1 (DEPENDS_ON T-1)" in out
    assert "T-3 waits for T-1 (WAITS_ON T-1)" in out


def test_reads_orders_nothing_and_warns_naming_the_waits_it_would_cause(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", writes=["src/a.py"]), ticket("T-2", writes=["src/b/**"]),
          ticket("T-3", writes=["docs/c.md"], reads=["src/**"]))
    code, out = run(tmp_path, capsys)
    assert code == 0
    assert batches(out) == [["T-1", "T-2", "T-3"]]
    assert "T-3 warning READS_WIDE (reads: would have made it wait for T-1, T-2; it orders nothing)" in out
    assert "READS_WIDE" in out.splitlines()[0]


def test_a_waits_on_decision_not_accepted_holds_the_ticket_and_an_accepted_one_does_not(tmp_path, capsys):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "DECISION_REGISTER.md").write_text(
        "### DEC-1 — one\n- **Status:** ACCEPTED (owner)\n\n### DEC-2 — two\n- **Status:** PROPOSED\n",
        encoding="utf-8")
    plant(tmp_path, ticket("T-1", waits_on=["DEC-1"]), ticket("T-2", waits_on=["DEC-2: the owner's word"]),
          ticket("T-3", depends_on=["T-2"]))
    _, out = run(tmp_path, capsys)
    assert batches(out) == [["T-1"]]
    assert "T-2 waits for DEC-2 (WAITS_ON DEC-2)" in out
    assert "T-3 waits for T-2 (DEPENDS_ON T-2)" in out
    assert "held: T-2, T-3" in out


def test_a_waits_on_record_path_that_exists_is_met(tmp_path, capsys):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "r.md").write_text("---\nstatus: ACCEPTED\n---\n", encoding="utf-8")
    (tmp_path / "docs" / "d.md").write_text("---\nstatus: draft\n---\n", encoding="utf-8")
    plant(tmp_path, ticket("T-1", waits_on=["docs/r.md"]), ticket("T-2", waits_on=["docs/d.md"]))
    _, out = run(tmp_path, capsys)
    assert batches(out) == [["T-1"]] and "T-2 waits for docs/d.md (WAITS_ON docs/d.md)" in out


# -- S3: overlap (the matcher's own tests are in test_w2_136_overlap.py) ----------------------------------------------

@pytest.mark.parametrize("a, b, series", [
    ("src/a/*.py", "src/a/b/c.py", False),       # * stays inside its folder
    ("src/a/**", "src/a/b/c.py", True),          # ** crosses folders
    ("src/new/**", "src/new/sub/*.py", True),    # a folder not yet created, pattern to pattern
    ("src/x.py", "src/x.py", True),
    ("src/x.py", "src/y.py", False),
])
def test_writes_that_overlap_run_in_series(tmp_path, capsys, a, b, series):
    plant(tmp_path, ticket("T-1", writes=[a]), ticket("T-2", writes=[b]))
    _, out = run(tmp_path, capsys)
    assert batches(out) == ([["T-1"], ["T-2"]] if series else [["T-1", "T-2"]])


# -- S4: deterministic ----------------------------------------------------------------------------------------------

def test_the_same_tickets_give_the_same_bytes_in_any_file_order(tmp_path, capsys):
    tickets = [ticket(f"T-{n}", writes=[f"src/{n % 3}/**"], priority=n % 2, needs=[f"src/{(n + 1) % 3}/x.py"])
               for n in range(1, 8)]
    one = plant(tmp_path / "one", *tickets, order=range(7))
    two = plant(tmp_path / "two", *tickets, order=[6, 2, 4, 0, 5, 1, 3])
    outs = [run(root, capsys, "--open")[1] for root in (one, two, one)]
    assert outs[0] == outs[1] == outs[2]


def test_ties_go_by_priority_then_wbs_order_then_id(tmp_path, capsys):
    plant(tmp_path, ticket("T-a", priority=2, wbs="W9-1", writes=["x"]),
          ticket("T-b", priority=1, wbs="W9-10", writes=["x"]),
          ticket("T-c", priority=1, wbs="W9-9", writes=["x"]),
          ticket("T-d", priority=1, wbs="W9-9", writes=["x"]))
    _, out = run(tmp_path, capsys)
    assert batches(out) == [["T-c"], ["T-d"], ["T-b"], ["T-a"]]


def test_a_needs_after_write_cycle_is_broken_by_the_key_and_named(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", priority=2, writes=["src/a.py"], needs=["src/b.py"]),
          ticket("T-2", priority=1, writes=["src/b.py"], needs=["src/a.py"]))
    _, out = run(tmp_path, capsys)
    assert batches(out) == [["T-2"], ["T-1"]]
    assert "CYCLE_TIEBREAK" in out.splitlines()[0]
    assert "T-1 waits for T-2 (NEEDS_WHAT_WRITES src/b.py)" in out
    assert "T-1 waits for T-2 (CYCLE_TIEBREAK NEEDS_WHAT_WRITES src/a.py)" in out


# -- S5: findings ---------------------------------------------------------------------------------------------------

def test_no_needs_is_planned_on_its_writes_and_flagged(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", writes=["src/a.py"], needs=None), ticket("T-2", writes=["src/b.py"]))
    code, out = run(tmp_path, capsys)
    assert code == 1
    assert batches(out) == [["T-1", "T-2"]]
    assert re.search(r"^T-1 finding NEEDS_UNDECLARED", out, re.M)


def test_deps_that_disagree_with_depends_on_is_a_finding(tmp_path, capsys):
    plant(tmp_path, ticket("T-1"), ticket("T-2", depends_on=["T-1"], deps=[]))
    code, out = run(tmp_path, capsys)
    assert code == 1 and "T-2 finding DEPS_DISAGREE" in out


def test_a_waits_on_that_names_nothing_is_a_finding(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", waits_on=["T-404 — gone"]))
    code, out = run(tmp_path, capsys)
    assert code == 1 and "T-1 finding UNKNOWN_WAIT (waits_on T-404 names nothing)" in out
    assert batches(out) == [["T-1"]]


@pytest.mark.parametrize("entry, expected", [
    ("DAEO-x — the reason", "DAEO-x"), ("DEC-12: why", "DEC-12"), ({"id": "W2-3", "reason": "r"}, "W2-3"),
    ({"DAEO-y": "the reason"}, "DAEO-y"), ("", None), (7, None),
])
def test_a_waits_on_entry_is_read_for_its_id(entry, expected):
    assert wait_id(entry) == expected


# -- S6: override ---------------------------------------------------------------------------------------------------

def test_an_override_shares_a_batch_despite_an_overlap_and_a_wait(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", writes=["src/a.py"]),
          ticket("T-2", writes=["src/a.py"], depends_on=["T-1"], plan_override="DEC-899 — the owner's exception"))
    code, out = run(tmp_path, capsys)
    assert code == 0
    assert batches(out) == [["T-1", "T-2"]]
    assert "T-2 overrides its wait for T-1 (OVERRIDE DEC-899 WRITES_OVERLAP src/a.py)" in out
    assert "T-2 overrides its wait for T-1 (OVERRIDE DEC-899 DEPENDS_ON T-1)" in out
    assert "OVERRIDE" in out.splitlines()[0]


# -- S7: --ready writes the list and nothing else -------------------------------------------------------------------

def test_without_ready_nothing_is_written(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", writes=["a"]), ticket("T-2", writes=["a"]))
    before = tree_hash(tmp_path)
    run(tmp_path, capsys, "--open")
    run_json(tmp_path, capsys, "--open")
    assert tree_hash(tmp_path) == before


def test_ready_writes_the_batches_in_the_dispatchers_form_and_nothing_else(tmp_path, capsys):
    root = plant(tmp_path / "repo", ticket("T-1", writes=["a"], wbs="W2-5"), ticket("T-2", writes=["a"], wbs="W2-6"),
                 ticket("T-3", writes=["b"], wbs="W2-7"))
    before = tree_hash(root)
    target = tmp_path / "ready.txt"
    code, _ = run(root, capsys, "--open", "--ready", str(target))
    assert code == 0 and tree_hash(root) == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["ready.txt", "repo"]
    assert target.read_text(encoding="utf-8") == (
        "# batch 1\n"
        "W2-5 T-1 W2-5-A5-run1.md W2-5-A5-run1.json\n"
        "W2-7 T-3 W2-7-A5-run1.md W2-7-A5-run1.json\n"
        "# batch 2\n"
        "W2-6 T-2 W2-6-A5-run1.md W2-6-A5-run1.json\n")


# -- S8: recomputed every run ---------------------------------------------------------------------------------------

def test_a_ticket_changed_between_two_runs_changes_the_plan(tmp_path, capsys):
    plant(tmp_path, ticket("T-1", writes=["src/a.py"]), ticket("T-2", writes=["src/b.py"]))
    assert batches(run(tmp_path, capsys)[1]) == [["T-1", "T-2"]]
    plant(tmp_path, ticket("T-2", writes=["src/a.py"]))
    assert batches(run(tmp_path, capsys)[1]) == [["T-1"], ["T-2"]]
    assert make_plan(tmp_path).batches == [["T-1"], ["T-2"]]


# -- S10: never a gate elsewhere ------------------------------------------------------------------------------------

def test_no_module_but_launchs_check_imports_the_plan():
    allowed = {SRC / "launch" / "plan_check.py"}
    found = []
    for path in sorted(SRC.rglob("*.py")):
        if path.is_relative_to(SRC / "plan") or path in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        if re.search(r"(from|import)\s+gov\.plan\b|from\s+gov\s+import\s+plan\b", text):
            found.append(str(path.relative_to(SRC)))
    assert found == []


def test_the_launcher_reaches_the_plan_only_through_its_check():
    text = (SRC / "launch" / "launcher.py").read_text(encoding="utf-8")
    assert "gov.plan" not in text and text.count("= check_lead(") == 1 and text.count("plan_check.check_lead(") == 1
