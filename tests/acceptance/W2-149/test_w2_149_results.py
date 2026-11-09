"""S12 (traces counted), S13 (only counts return), S14 (a bad result not delivered), S16 (the delivery lands only where
the kind delivers), S17 (a finished wall is one file), S18 (the hidden part's file budget)."""

from __future__ import annotations

import json
import shutil
import stat

import pytest

import w2_149_support as support
from w2_149_support import assert_good_launch, assert_nothing_built, assert_refused

MARK = "MARK-W2149-7f3a-free-text"


def text_of(path):
    return path.read_text(errors="replace") if path.exists() else ""


# -- S12 ------------------------------------------------------------------------------------------------------------

def test_s12_a_trace_under_claude_is_counted_and_reported_22(world):
    """The stub's session leaves ~/.claude/projects/<x>/<session id>.jsonl in the planted HOME; the planted file of
    another session id is not counted."""
    world.write_stub(session={"out": support.good_out("writer"), "trace": True, "session_id": "stub-sid-0001"})
    run = world.launch(*world.args("writer"))
    assert run.code == 22, run.why()
    assert run.line["traces"] == 1 and run.line["reason"] == "trace", run.line
    counts = json.loads((world.counts_dir(run.line) / "counts.json").read_text())
    assert counts["traces"] == 1


# -- S13 ------------------------------------------------------------------------------------------------------------

def test_s13_free_text_from_out_or_the_session_reaches_no_output(world):
    out = support.good_out("writer", note=MARK)
    out["set/q01.yaml"] = f"id: q01\nquestion: {MARK}\n"
    denials = [{"tool_name": "Read", "tool_use_id": "t1", "tool_input": {"file_path": f"/nowhere/{MARK}.txt"}},
               {"tool_name": MARK, "tool_use_id": "t2", "tool_input": {"x": MARK}}]
    run = world.deliver("writer", session_extra={"result": f"the answer is {MARK}", "denials": denials}, out=out)
    assert run.code == 0, run.why()
    line = run.line
    folder = world.counts_dir(line)
    counts_text = text_of(folder / "counts.json")
    log = folder / "launch.log"
    assert log.is_file(), "the script's log (launch.log in the run's counts folder) is missing"
    for name, text in (("counts.json", counts_text), ("stdout", run.out), ("stderr", run.err),
                       ("launch.log", text_of(log))):
        assert MARK not in text, f"the marker reached {name}"
        assert str(world.wall(line)) not in text, f"a path under the wall reached {name}"
    assert json.loads(counts_text) == line, "the printed line is not counts.json"
    refusals = line["session"]["refusals"]
    assert refusals["Read"] == 1 and refusals["other"] == 1, refusals
    again = world.launch("--sets-root", world.sr, "--kind", "writer", "--run", line["run"], "--counts-only")
    assert again.code == 0, again.why()
    assert again.line == line and MARK not in again.out + again.err


def test_s13_the_counts_schema_is_closed_and_every_value_typed(world):
    assert support.COUNTS_SCHEMA.is_file(), "indep-schemas/indep-counts.schema.json does not exist yet"
    schema = json.loads(support.COUNTS_SCHEMA.read_text())
    assert support.schema_holes(schema) == []
    run = world.deliver("writer")
    assert run.code == 0, run.why()
    line = run.line
    assert support.validate(schema, line) == []
    assert world.free_text(line) == []
    assert line["act"] == support.ACT and line["kind"] == "writer" and line["status"] == "delivered"
    assert line["code"] == 0 and line["reason"] is None and line["traces"] == 0
    out = line["out"]
    assert out["schema_ok"] is True and out["files"] == 4
    assert out["questions"] == 3
    for key in ("by_kind", "by_area"):
        want = support.GOOD_RESULT["writer"][key]
        assert all(out[key].get(k, 0) == v for k, v in want.items()) and sum(out[key].values()) == sum(want.values())
    s = line["session"]
    assert s["turns"] == 3 and s["is_error"] is False and s["exit"] == 0
    assert s["cost_usd"] == pytest.approx(0.0123) and s["duration_s"] == pytest.approx(2.345)


def test_s13_a_refusal_line_carries_its_code_reason_word_and_approved_sha256(world):
    assert support.COUNTS_SCHEMA.is_file(), "indep-schemas/indep-counts.schema.json does not exist yet"
    schema = json.loads(support.COUNTS_SCHEMA.read_text())
    good = world.brief_sha("writer")
    run = world.launch(*world.args("writer", sha=good[::-1]))
    assert_refused(world, run, 10)
    assert support.validate(schema, run.line) == []
    assert world.free_text(run.line) == []


# -- S14 ------------------------------------------------------------------------------------------------------------

def destinations(world):
    return (world.hashes(world.sr / "fixtures/evaluation/memory-verdict-4"),
            world.hashes(world.sr / support.SEALED))


def rejected(world, run, before):
    assert run.code == 20, run.why()
    line = run.line
    assert line["status"] == "rejected" and line["reason"] == "result" and line["out"]["schema_ok"] is False
    assert line["delivered"]["files"] == 0 and line["delivered"]["to"] is None
    assert destinations(world) == before, "something was written under the set's folder or the sealed folder"
    assert world.tar(line).is_file() and not world.wall(line).exists() and not world.tree(line).exists()


def test_s14_a_missing_result_is_rejected_20(world):
    out = support.good_out("writer")
    del out["result.json"]
    before = destinations(world)
    rejected(world, world.deliver("writer", out=out), before)


def test_s14_a_result_failing_its_kind_s_schema_is_rejected_20(world):
    """by_kind holds a word outside the writer's fixed list."""
    out = support.good_out("writer")
    out["result.json"] = json.dumps({"questions": 1, "by_kind": {"made-up": 1}, "by_area": {"docs": 1}})
    before = destinations(world)
    rejected(world, world.deliver("writer", out=out), before)


# -- S16 ------------------------------------------------------------------------------------------------------------

DESTINATION = {"writer": "fixtures/evaluation/memory-verdict-4/hidden",
               "checker": "fixtures/evaluation/memory-verdict-3/XCHECK-r1.md",
               "auditor": "runs/audit-1/miss-classes.json",
               "labeller": support.SEALED + "/labels/{run}.jsonl"}


@pytest.mark.parametrize("kind", support.KINDS)
def test_s16_the_delivery_lands_only_where_the_kind_delivers(world, kind):
    before = world.hashes(world.sr)
    run = world.deliver(kind)
    assert run.code == 0, run.why()
    line = run.line
    after = world.hashes(world.sr)
    assert {k: v for k, v in after.items() if k in before} == before, "a file under the sets root changed or went"
    dest = DESTINATION[kind].format(run=line["run"])
    files = {k: v.encode() for k, v in support.GOOD_DELIVERY[kind].items()}
    if kind == "writer":
        landed = {k[len(dest) + 1:]: k for k in after if k.startswith(dest + "/")}
        want = {k[len("set/"):]: v for k, v in files.items()}
    else:
        landed = {dest.rsplit("/", 1)[-1]: dest} if dest in after else {}
        want = {dest.rsplit("/", 1)[-1]: next(iter(files.values()))}
    assert set(landed) == set(want), (sorted(landed), sorted(want))
    for rel, data in want.items():
        assert (world.sr / landed[rel]).read_bytes() == data
    tar = f"indep-walls/{kind}/{line['run']}.tar"
    added = set(after) - set(before)
    assert added == set(landed.values()) | {tar}, f"files beyond the delivery: {sorted(added - set(landed.values()) - {tar})}"
    d = line["delivered"]
    assert d["files"] == len(want) and d["to"] == support.DELIVER_TO[kind]
    assert d["sha256"] == support.bundle_sha(kind, want)
    result = support.GOOD_RESULT[kind]
    for k, v in result.items():
        if isinstance(v, dict):
            assert all(line["out"][k].get(x, 0) == n for x, n in v.items())
        else:
            assert line["out"][k] == v, (k, line["out"])
    if kind == "auditor":
        last = [json.loads(x) for x in (world.runs / "AUDITS.log").read_text().splitlines() if x.strip()][-1]
        assert last["commit"] == world.sha("B"), "AUDITS.log did not gain the audit's commit"


# -- S17 ------------------------------------------------------------------------------------------------------------

def test_s17_a_finished_wall_is_one_file(world):
    walls_before = sum(1 for _ in world.hashes(world.walls))
    hidden_before = world.hidden_count()
    run = world.deliver("checker")
    assert run.code == 0, run.why()
    line = run.line
    tar = world.tar(line)
    assert tar.is_file() and stat.S_IMODE(tar.stat().st_mode) == 0o400
    assert not world.wall(line).exists() and not world.tree(line).exists()
    assert sum(1 for _ in world.hashes(world.walls)) == walls_before + 1
    assert world.hidden_count() == hidden_before + 1
    names = world.tar_names(line)
    assert any(n.endswith("WALL.json") for n in names) and any(n.endswith(".session.json") for n in names)
    assert any(n.endswith("out/result.json") for n in names)


# -- S18 ------------------------------------------------------------------------------------------------------------

def big_set(world):
    for i in range(20):
        support.write_file(world.sr, f"fixtures/evaluation/memory-verdict-3/hidden/big/q{i:02d}.yaml", f"id: {i}\n")


def test_s18_a_launch_past_the_8000_file_budget_refuses_15(world):
    big_set(world)
    world.fill_hidden(7990)
    before = world.built_state("checker")
    run = world.launch(*world.args("checker"))
    assert_refused(world, run, 15)
    assert_nothing_built(world, "checker", before)
    assert world.hidden_count() == 7990
    shutil.rmtree(world.sr / "fixtures/evaluation/memory-verdict/hidden/bulk")
    assert_good_launch(world, "checker")


def test_s18_a_launch_inside_the_budget_builds(world):
    big_set(world)
    world.fill_hidden(7900)
    run = world.launch(*world.args("checker", dry=True))
    assert run.code == 0, run.why()
    assert run.line["status"] == "dry"
