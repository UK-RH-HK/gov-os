"""S1: every approved ticket goes to the landing command as one batch; never one not approved, never twice; each
outcome is an inbox item (ticket DAEO-ifgf, Interface item 1).

The landing command is a stub under ``tmp_path`` that records its argv, the state folder's listing as it started and its
working folder, and exits with the code the test chose. Finalisation happens on a later ``tick`` after the stub exits.
"""

from __future__ import annotations

import os
import sys

import pytest

import w2_121b_support as s
from w2_121b_support import HEAD_A, HEAD_B, HEAD_C, HEAD_D

A, B, C, D = (f"W2-1={HEAD_A}", f"W2-2={HEAD_B}", f"W2-3={HEAD_C}", f"W2-4={HEAD_D}")


def approvals_of(run: dict, before: int = 0, after: int = 0) -> list[str]:
    argv = run["argv"]
    return sorted(argv[before:len(argv) - after])


def test_approved_tickets_go_as_one_batch_claimed_before_the_launch(landing):
    p = landing
    for n in (1, 2, 3):
        p.add_ticket(n)
    p.cfg(landing_command=[sys.executable, str(p.stubs / "land.py"), str(p.rec), str(p.state), "--before",
                           "{approvals}", "--after"])
    (p.root / "scratch-notes.txt").write_text("untracked: never holds a landing\n", encoding="utf-8")
    p.stub_waits()
    p.plant_land(A, B)

    run = p.tick_ok()
    assert run.seconds < 10, f"the pass waited for the landing command (it must run detached): {run}"
    runs = p.wait_land_runs(1)
    p.settle_none()
    assert len(p.land_runs()) == 1, "the two approvals went as more than one batch"
    batch = runs[0]
    assert batch["argv"][0] == "--before" and batch["argv"][-1] == "--after", batch["argv"]
    assert approvals_of(batch, 1, 1) == sorted([A, B]), f"{{approvals}} is one argument per approved line: {batch['argv']}"
    assert os.path.realpath(batch["cwd"]) == os.path.realpath(p.root), "the batch runs in the root"
    # the claim precedes the launch: when the command starts, land.txt is already renamed
    assert "land.txt" not in batch["state_listing"], batch["state_listing"]
    land_id = p.land_id_of(batch)
    assert s.LAND_ID.match(land_id), land_id
    assert not p.land_file.exists()
    assert (p.state / "logs" / land_id).exists(), "the batch's output goes to logs/<land id>"

    p.release()
    assert p.wait_exit_file(land_id) == "0", "logs/<land id>.exit holds the batch's exit code"
    assert "landing stub ran with 2 approval" in (p.state / "logs" / land_id).read_text(encoding="utf-8")
    p.tick_until(p.finalised(A), what="the landing to be finalised")

    for pair in (A, B):
        (fields,) = p.done_for(pair)
        assert len(fields) >= 4 and fields[-2] == "0" and fields[-1] == land_id, \
            f"land-done.txt: `<W2>=<head> <time> <exit code> <land id>`, got {fields}"
    assert p.claimed_files() == [], "the claimed file is removed when the landing is finalised"
    (item,) = p.land_items()
    assert item.path.name == f"{land_id}.land.txt"
    assert item.fields.get("log") == land_id
    assert sorted(item.fields.get("W2", "").split()) == ["W2-1", "W2-2"], item.text
    assert item.fields.get("status") == "landed", item.text
    assert item.fields.get("kind") == "land", item.text
    # one outcome, one item; nothing runs again
    p.tick_ok()
    p.settle_none()
    assert len(p.land_items()) == 1 and len(p.land_runs()) == 1 and len(p.done_lines()) == 2
    assert "W2-3" not in "".join(p.done_lines()) and "W2-3" not in " ".join(batch["argv"])


def test_token_absent_the_approvals_are_appended_at_the_end(landing):
    p = landing
    p.add_ticket(1)
    p.add_ticket(2)
    p.cfg(landing_command=[sys.executable, str(p.stubs / "land.py"), str(p.rec), str(p.state), "--flag"])
    p.plant_land(A, B)
    batch = p.claim_and_run(1)
    assert batch["argv"][0] == "--flag", batch["argv"]
    assert sorted(batch["argv"][1:]) == sorted([A, B]), f"the approvals go at the end, one argument per line: {batch['argv']}"


def test_unapproved_and_malformed_lines_never_go(landing):
    p = landing
    for n in (1, 2, 3):  # W2-3 is in the project (worktree, ticket) but not approved
        p.add_ticket(n)
    p.plant_land(A, "W2-9=xyz", B, "W2-8=abc123")
    p.tick_ok()
    (batch,) = p.wait_land_runs(1)
    p.settle_none()
    assert len(p.land_runs()) == 1
    assert sorted(batch["argv"]) == sorted([A, B]), f"only the well-formed approved lines go: {batch['argv']}"
    blob = p.status_blob()
    assert "W2-9" in blob and "W2-8" in blob, "a line not of the form <W2>=<12-hex> is named in the status"
    p.tick_until(p.finalised(A), what="the landing to be finalised")
    text = "\n".join(p.done_lines()) + "\n".join(i.text for i in p.land_items())
    for never in ("W2-3", "W2-9", "W2-8"):
        assert never not in text, f"{never} was recorded as landed"


def test_only_malformed_lines_are_named_and_never_sent(landing):
    p = landing
    p.add_ticket(1)
    p.plant_land("W2-9=xyz", "W2-8=abc123", "W2-6=")
    run = p.tick_ok()
    p.settle_none()
    assert p.land_runs() == [], "a malformed line was sent to the landing command"
    blob = p.status_blob()
    for ident in ("W2-9", "W2-8", "W2-6"):
        assert ident in blob, f"{ident}'s line is malformed and must be named in the status\n{run}"
    # the same file with one well-formed approval added: that one goes, the malformed ones still do not
    p.plant_land("W2-9=xyz", A, "W2-8=abc123")
    batch = p.claim_and_run(1)
    assert batch["argv"] == [A], batch["argv"]


def test_a_failed_batch_is_an_inbox_item_with_its_exit_code(landing):
    p = landing
    p.add_ticket(1)
    p.add_ticket(2)
    p.set_land_exit(3)
    p.plant_land(A, B)
    batch = p.claim_and_run(1)
    land_id = p.land_id_of(batch)
    assert p.wait_exit_file(land_id) == "3"
    p.tick_until(p.finalised(A), what="the failed landing to be finalised")
    (item,) = p.land_items()
    assert item.path.name == f"{land_id}.land.txt"
    assert item.fields.get("status") == "failed (exit 3)", item.text
    assert item.fields.get("kind") == "land" and item.fields.get("log") == land_id, item.text
    assert sorted(item.fields.get("W2", "").split()) == ["W2-1", "W2-2"], item.text
    for pair in (A, B):
        (fields,) = p.done_for(pair)
        assert fields[-2] == "3" and fields[-1] == land_id, fields
    assert p.claimed_files() == []


def test_approvals_already_done_are_dropped_from_the_batch(landing):
    p = landing
    p.add_ticket(1)
    p.add_ticket(2)
    p.plant_done(A)
    p.plant_land(A, B)
    batch = p.claim_and_run(1)
    assert batch["argv"] == [B], f"an approval already in land-done.txt is never sent again: {batch['argv']}"


def test_an_approval_is_never_sent_twice_across_landings(landing):
    p = landing
    for n in (1, 2, 3):
        p.add_ticket(n)
    p.plant_land(A)
    first = p.claim_and_run(1)
    assert first["argv"] == [A]
    p.tick_until(p.finalised(A), what="the first landing to be finalised")
    p.plant_land(A, B)  # A planted again: never twice
    second = p.claim_and_run(2)
    assert second["argv"] == [B], second["argv"]
    p.tick_until(p.finalised(B), what="the second landing to be finalised")
    p.plant_land(A, B, C)
    third = p.claim_and_run(3)
    assert third["argv"] == [C], third["argv"]
    assert len(p.land_runs()) == 3
    p.tick_until(p.finalised(C), what="the third landing to be finalised")
    assert len(p.land_items()) == 3
    assert [len(p.done_for(x)) for x in (A, B, C)] == [1, 1, 1]


def test_a_second_pass_while_the_batch_runs_starts_no_second_batch(landing):
    p = landing
    p.add_ticket(1)
    p.add_ticket(2)
    p.stub_waits()
    p.plant_land(A)
    first = p.claim_and_run(1)
    land_id = p.land_id_of(first)

    p.plant_land(B)  # a new approval arrives while the first batch is unfinished
    run = p.tick_ok()
    p.settle_none()
    assert len(p.land_runs()) == 1, "a second batch was started while the first was unfinished"
    assert p.land_file.exists() and p.land_file.read_text(encoding="utf-8").strip() == B, \
        "the new approval is not claimed while a landing of the dispatcher's own is unfinished"
    assert [f.name for f in p.claimed_files()] == [f"land-claimed-{land_id}.txt"]
    assert p.land_lines_in_status(), f"the held landing's reason is a `land:` line in status.txt\n{run}"

    p.release()
    p.tick_until(p.finalised(A), what="the first landing to be finalised")
    p.tick_until(lambda: len(p.land_runs()) >= 2, what="the second batch to start once the first is finished")
    assert p.land_runs()[1]["argv"] == [B]


def test_an_unclean_tree_holds_the_landing_until_it_is_clean(landing):
    p = landing
    p.add_ticket(1)
    p.dirty_root()
    p.plant_land(A)
    run = p.tick()
    assert run.code == 0, run
    p.settle_none()
    assert p.land_runs() == [] and p.land_file.exists() and p.claimed_files() == [], "a landing went with a tracked change in the root"
    assert p.land_lines_in_status(), f"the reason is a `land:` line in status.txt\n{run}"
    p.clean_root()
    batch = p.claim_and_run(1)
    assert batch["argv"] == [A]


def test_a_root_on_another_branch_holds_the_landing(landing):
    p = landing
    p.add_ticket(1)
    s.git(p.root, "switch", "-q", "-c", "other")
    p.plant_land(A)
    run = p.tick()
    assert run.code == 0, run
    p.settle_none()
    assert p.land_runs() == [] and p.land_file.exists() and p.claimed_files() == [], "a landing went from a root not on the integration branch"
    assert p.land_lines_in_status(), f"the reason is a `land:` line in status.txt\n{run}"
    s.git(p.root, "switch", "-q", "integ")
    batch = p.claim_and_run(1)
    assert batch["argv"] == [A]
