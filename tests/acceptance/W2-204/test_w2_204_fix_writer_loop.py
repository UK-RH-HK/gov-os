"""The fix under the closed ticket DAEO-ma4q: the fresh 80's writer loop (I-23 with EF-9, I-18, I-19), FM-1 to FM-4.

FM-1 deliver refuses what the pre-flight would refuse, with codes only; FM-2 round 2 sees pre-flight 1's refusals;
FM-3 a void is said at once, before any measure; FM-4 every stop names its cause. Each test name carries its KPI id
(``fm1`` .. ``fm4``). Planted sets only; the tool is driven as a child process through the CLI."""

from __future__ import annotations

import re

import pytest

import w2_204_support as K
import w2_204_writer_loop_support as L
from w2_204_support import HIDDEN, VISIBLE

BOTH = (VISIBLE, HIDDEN)


# -- FM-1: deliver ------------------------------------------------------------------------------------------------------
def _assert_refusal_shape(run, expected: str):
    lines = run.lines
    assert run.code == 1 and lines and lines[0] == "DL-PREFLIGHT", run
    assert len(lines) >= 2 and any(re.fullmatch(expected, x) for x in lines[1:]), (expected, run)
    for x in lines[1:]:
        assert L.PF_LINE.fullmatch(x), ("a line that is not a code with its count and ids", x)
        if x.split()[0] in L.SET_LEVEL:
            assert L.PF_SET_LINE.fullmatch(x), ("a set-level code carries no ids", x)
    assert not any(word in run.text for word in K.planted_words())


@pytest.mark.parametrize("fault", sorted(L.FAULTS))
def test_fm1_deliver_refuses_a_set_the_pre_flight_would_refuse_then_accepts_it_repaired(world, tmp_path, fault):
    L.briefed(world)
    out = L.writer_out(world, tmp_path / "bad", L.faulty(world, fault))
    run = world.deliver("writer", HIDDEN, out)
    _assert_refusal_shape(run, L.FAULTS[fault][1])
    assert L.landed(world) == {}, "a refused delivery copied a file"
    assert K.files_holding(world.sets, [K.QWORD, K.GWORD]) == [], "a planted question or gold word reached the sets root"
    # the same round, repaired, is accepted and passes pre-flight 1 on the same files
    L.unfault(world, fault)
    good = L.writer_out(world, tmp_path / "good", K.clean_specs())
    ok = world.deliver("writer", HIDDEN, good)
    assert ok.code == 0 and ok.lines == ["DELIVER writer round 1 files 40"], ok
    pre = world.step("preflight", HIDDEN)
    assert pre.code == 0, pre


def test_fm1_a_round_2_delivery_is_checked_the_same_way_and_the_round_1_files_stay(world, tmp_path):
    L.briefed(world)
    first = L.writer_out(world, tmp_path / "a", K.clean_specs())
    assert world.deliver("writer", HIDDEN, first).code == 0
    before = L.landed(world)
    bad = L.writer_out(world, tmp_path / "b", L.faulty(world, "source"), salt="r2")
    run = world.deliver("writer", HIDDEN, bad, round_no=2)
    _assert_refusal_shape(run, L.FAULTS["source"][1])
    assert L.landed(world) == before and not (world.set_dir(HIDDEN) / "r1").exists(), "round 1 was moved aside"
    good = L.writer_out(world, tmp_path / "c", K.clean_specs(), salt="r2")
    ok = world.deliver("writer", HIDDEN, good, round_no=2)
    assert ok.code == 0 and ok.lines == ["DELIVER writer round 2 files 40"], ok
    assert world.step("preflight", HIDDEN).code == 0


def test_fm1_guard_a_clean_writer_set_is_delivered_and_passes_pre_flight_1(world, tmp_path):
    L.briefed(world)
    run = world.deliver("writer", HIDDEN, L.writer_out(world, tmp_path, K.clean_specs()))
    assert run.code == 0 and run.lines == ["DELIVER writer round 1 files 40"], run
    pre = world.step("preflight", HIDDEN)
    assert pre.code == 0 and len(L.landed(world)) == 40, pre


def test_fm1_guard_the_existing_deliver_refusals_stay(world, tmp_path):
    L.briefed(world)
    empty = tmp_path / "empty"
    empty.mkdir()
    run = world.deliver("writer", HIDDEN, empty)
    assert run.code == 1 and run.lines and run.lines[0] in ("DL-RESULT", "DL-SET"), run
    assert L.landed(world) == {}


# -- FM-1: the Stop hook ------------------------------------------------------------------------------------------------
def test_fm1_the_writer_brief_writes_a_stop_hook_that_runs_writer_check(world):
    folder = L.session(world)
    cmd = L.hook_command(folder)
    assert "memaudit" in cmd and "writer-check" in cmd, cmd


def test_fm1_a_round_2_writer_brief_writes_the_hook_too(world):
    world.write_half(HIDDEN, K.clean_specs())
    world.write_notes(HIDDEN, 1)
    folder = L.session(world, "writer-2", round_no=2)
    assert "writer-check" in L.hook_command(folder)


def test_fm1_a_checker_brief_writes_no_hook(world):
    world.write_half(HIDDEN, K.clean_specs())
    folder = L.session(world, "checker-1", kind="checker")
    assert not (folder / ".claude" / "settings.json").exists()


@pytest.mark.parametrize("fault", sorted(L.FAULTS))
def test_fm1_the_hook_blocks_the_stop_naming_ids_and_codes_only(world, fault):
    L.briefed(world)
    folder = L.session(world)
    L.put_set(world, folder, L.faulty(world, fault))
    call = L.run_hook(world, folder)
    lines = L.reason_lines(call)
    assert any(re.fullmatch(L.FAULTS[fault][1], x) for x in lines), (L.FAULTS[fault][1], call)
    for x in lines:
        assert L.PF_LINE.fullmatch(x), ("a reason line that is not a code with its count and ids", x)
        if x.split()[0] in L.SET_LEVEL:
            assert L.PF_SET_LINE.fullmatch(x), x
    assert not any(word in call.text for word in K.planted_words()), "a question's text, gold or source in the output"
    doc = L.record(world)
    assert doc["returns"] == 1 and doc["ended"] is None, doc
    code = L.FAULTS[fault][1].split()[0]
    assert code in doc["refused"], doc
    if code in L.SET_LEVEL:
        assert doc["refused"][code] == [], doc
    assert K.files_holding(world.run_dir(HIDDEN), K.planted_words()) == [], "a planted word reached the run folder"
    assert L.landed(world) == {}, "the check wrote into hidden/"
    # equivalence: the reason's lines are exactly pre-flight 1's refusals of the same files
    files = {p.name: p.read_bytes() for p in (folder / "out" / "set").iterdir()}
    hidden = world.hidden(HIDDEN)
    hidden.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (hidden / name).write_bytes(data)
    assert sorted(lines) == sorted(L.preflight_refused_lines(world)), "writer-check and pre-flight 1 disagree"


def test_fm1_a_clean_set_ends_at_once_and_passes_pre_flight_1_and_deliver(world, tmp_path):
    L.briefed(world)
    folder = L.session(world)
    L.put_set(world, folder, K.clean_specs())
    call = L.run_hook(world, folder)
    assert call.code == 0 and call.out.strip() == "", call
    doc = L.record(world)
    assert doc["ended"] == "pass" and doc["returns"] == 0 and doc["refused"] == {}, doc
    assert L.landed(world) == {}
    out = L.writer_out(world, tmp_path / "o", K.clean_specs())
    ok = world.deliver("writer", HIDDEN, out)
    assert ok.code == 0 and ok.lines == ["DELIVER writer round 1 files 40"], ok
    assert world.step("preflight", HIDDEN).code == 0


def test_fm1_a_repaired_set_ends_the_loop_after_one_return(world):
    L.briefed(world)
    folder = L.session(world)
    L.put_set(world, folder, L.faulty(world, "form"))
    L.block_of(L.run_hook(world, folder))
    L.put_set(world, folder, K.clean_specs())
    call = L.run_hook(world, folder)
    assert call.code == 0 and call.out.strip() == "", call
    doc = L.record(world)
    assert doc["ended"] == "pass" and doc["returns"] == 1, doc


def test_fm1_the_fourth_stop_is_allowed_and_the_refused_ids_are_recorded(world):
    L.briefed(world)
    folder = L.session(world)
    L.put_set(world, folder, L.faulty(world, "form"))
    for n in (1, 2, 3):
        call = L.run_hook(world, folder)
        assert any(x == "PF-FORM refused 1 q07" for x in L.reason_lines(call)), call
        assert L.record(world)["returns"] == n
    call = L.run_hook(world, folder)
    assert call.code == 0 and call.out.strip() == "", call
    doc = L.record(world)
    assert doc["ended"] == "limit" and doc["returns"] == 3 and doc["refused"] == {"PF-FORM": ["q07"]}, doc
    assert L.landed(world) == {}


@pytest.mark.parametrize("make", ["missing", "empty"])
def test_fm1_a_missing_or_empty_set_is_refused_as_pf_count(world, make):
    L.briefed(world)
    folder = L.session(world)
    if make == "empty":
        (folder / "out" / "set").mkdir(parents=True)
    call = L.run_hook(world, folder)
    assert any(re.fullmatch(r"PF-COUNT refused [0-9]+( .*)?", x) for x in L.reason_lines(call)), call
    assert L.record(world)["refused"].get("PF-COUNT") == []


def test_fm1_one_reason_names_every_refused_code_once(world):
    L.briefed(world)
    folder = L.session(world)
    specs = L.faulty(world, "form")
    L.f_source(world, specs)
    L.put_set(world, folder, specs)
    lines = L.reason_lines(L.run_hook(world, folder))
    assert "PF-FORM refused 1 q07" in lines and "PF-SOURCE refused 1 q21" in lines, lines
    assert len({x.split()[0] for x in lines}) == len(lines), lines


# -- FM-2 -------------------------------------------------------------------------------------------------------------
def _refused_half(world, specs, *, clean: bool = False):
    world.write_half(HIDDEN, specs)
    world.write_notes(HIDDEN, 1, {"q05": ("revise", "R6-SPAN-MISSES")})
    pre = world.step("preflight", HIDDEN)
    assert pre.code == (0 if clean else 1), ("the planted half's pre-flight 1 was not as planted", pre)


def _round_2_brief(world, kind: str) -> str:
    out = world.base / "briefs" / f"{kind}-2"
    run = world.brief(kind, HIDDEN, out, round_no=2)
    assert run.code == 0, run
    return (out / "brief.md").read_text(encoding="utf-8")


def _refusing_specs():
    """q21's source is nowhere (PF-SOURCE, one id); three failure-memory questions cite code (PF-SPREAD, set level)."""
    specs = K.thin_specs()
    next(s for s in specs if s["id"] == "q21")["sources"] = [{"path": "app/engine/nowhere.py"}]
    return specs


@pytest.mark.parametrize("kind", ["writer", "checker"])
def test_fm2_the_round_2_brief_lists_pre_flight_1_s_refusals_by_id_and_code(world, kind):
    _refused_half(world, _refusing_specs())
    text = _round_2_brief(world, kind)
    section = L.section_of(text)
    assert section is not None, "no '## Pre-flight 1 refusals' section"
    lines = L.section_lines(section)
    assert "q21 PF-SOURCE" in lines, lines
    assert any(re.fullmatch(r"set PF-SPREAD \S.*", x) for x in lines), ("a set-level line is 'set <CODE> <detail>'", lines)
    assert [x for x in lines if re.match(r"q[0-9]{2} PF-", x)] == ["q21 PF-SOURCE"], lines
    assert not any(word in text for word in K.planted_words()), "a question's text reached the brief"


def test_fm2_the_writer_s_section_says_to_repair_or_replace_exactly_those(world):
    _refused_half(world, _refusing_specs())
    section = L.section_of(_round_2_brief(world, "writer"))
    assert section is not None, "no '## Pre-flight 1 refusals' section"
    low = section.lower()
    assert "repair" in low and "replace" in low and "exactly" in low, section


@pytest.mark.parametrize("kind", ["writer", "checker"])
def test_fm2_guard_a_round_2_after_a_clean_pre_flight_1_has_no_such_section(world, kind):
    _refused_half(world, K.clean_specs(), clean=True)
    assert "Pre-flight 1 refusals" not in _round_2_brief(world, kind)


# -- FM-3 -------------------------------------------------------------------------------------------------------------
@pytest.fixture(scope="module")
def count_pair(tmp_path_factory):
    return L.void_pair(tmp_path_factory.mktemp("fm3-count"), "count")


@pytest.fixture(scope="module")
def domain_pair(tmp_path_factory):
    return L.void_pair(tmp_path_factory.mktemp("fm3-domain"), "domain")


def _visible_untouched(pair):
    world, final = pair.world, pair.calls["final"]
    run = world.run_dir(VISIBLE)
    assert world.gov_calls() == [] and world.claude_calls() == [], "a measure or a judge was started"
    assert not (run / "COUNTS").exists() and not (run / "USED").exists(), final


def test_fm3_a_hidden_half_under_the_minimum_is_void_at_once_and_the_visible_half_is_not_measured(count_pair):
    final = count_pair.calls["final"]
    hidden = HIDDEN
    assert f"VOID {hidden} VOID-COUNT kept 35 dropped 5 need 36" in final.lines, final
    assert f"STOPPED {hidden} void 2" in final.lines, final
    assert final.lines.index(f"VOID {hidden} VOID-COUNT kept 35 dropped 5 need 36") < final.lines.index(
        f"STOPPED {hidden} void 2")
    assert final.code == 2 and not any(x.startswith("FRESH VERDICT") for x in final.lines), final
    _visible_untouched(count_pair)
    assert not any(word in final.text for word in K.planted_words())


def test_fm3_a_hidden_half_still_thin_in_a_domain_says_void_domain_and_the_visible_half_is_not_measured(domain_pair):
    final = domain_pair.calls["final"]
    voids = [re.fullmatch(rf"VOID {HIDDEN} VOID-DOMAIN kept 40 dropped 0 need [0-9]+", x) for x in final.lines]
    assert any(voids), final
    assert f"STOPPED {HIDDEN} void 2" in final.lines and final.code == 2, final
    _visible_untouched(domain_pair)


# -- FM-4 -------------------------------------------------------------------------------------------------------------
def _every_stop_has_its_cause(call: K.Call, expect_steps: dict[str, str]) -> list:
    """Every STOPPED line (at least one) just after a CAUSE line of its audit and step; ``expect_steps`` the stops
    (audit -> step) that must be among them. Returns the CAUSE matches."""
    found = L.stops(call)
    assert found, call
    causes = []
    for at, audit, step in found:
        cause = L.cause_before(call, at)
        assert cause and (cause[1], cause[2]) == (audit, step), ("STOPPED without its CAUSE just before", call.lines[at - 1:at + 1])
        causes.append(cause)
    assert {(a, s) for _, a, s in found} >= set(expect_steps.items()), (found, call)
    assert not any(word in call.text for word in K.planted_words())
    return causes


def test_fm4_a_preflight_final_refusal_names_its_pf_codes(stage):
    call = stage("stopped-heavy")["r2"]
    causes = _every_stop_has_its_cause(call, {})
    assert call.code == 2 and any(c[2] == "preflight-final" and c[3] == "PF-SPREAD" for c in causes), call
    assert all(re.fullmatch(r"PF-[A-Z]+", c[3]) for c in causes if c[2] == "preflight-final"), causes


def test_fm4_a_void_stop_names_its_cause(stage, count_pair):
    for call in (stage("stopped-thin")["r2"], count_pair.calls["final"]):
        causes = _every_stop_has_its_cause(call, {})
        assert call.code == 2 and any(c[2] == "void" and c[3] in ("VOID-COUNT", "VOID-DOMAIN") for c in causes), call


def test_fm4_a_measure_stop_after_a_used_marker_names_its_cause(tmp_path_factory):
    pair = L.prepared_pair(tmp_path_factory.mktemp("fm4-used"), used=True)
    call = pair.calls["final"]
    _every_stop_has_its_cause(call, {VISIBLE: "measure"})
    causes = [L.CAUSE.fullmatch(x) for x in call.lines]
    assert any(m and m[2] == "measure" and m[3] == "FR-MEASURE-USED" for m in causes), call
    assert call.code == 2 and (pair.world.run_dir(VISIBLE) / "USED").exists(), call


def test_fm4_a_busy_gate_stop_names_its_cause(tmp_path_factory):
    gate = f"{K.sys.executable} -c 'import sys; sys.exit(1)'"
    pair = L.prepared_pair(tmp_path_factory.mktemp("fm4-gate"), used=False, extra=("--gate-cmd", gate),
                           env={"GOV_MEMAUDIT_GATE_MAX_S": "0", "GOV_MEMAUDIT_GATE_POLL_S": "0"})
    call = pair.calls["final"]
    causes = _every_stop_has_its_cause(call, {VISIBLE: "measure"})
    assert call.code == 2 and pair.world.gov_calls() == [], call
    assert any(c[3] == "FR-GATE-BUSY" for c in causes), causes


def test_fm4_an_fr_refusal_is_beside_a_cause_line(world):
    assert world.fresh().code == 5
    call = world.fresh(commit=world.later_commit)
    assert call.code == 1 and "FR-NAME" in call.lines, call
    at = call.lines.index("FR-NAME")
    after = call.lines[at + 1] if at + 1 < len(call.lines) else ""
    m = L.CAUSE.fullmatch(after)
    assert m and m[1] == "fresh" and m[3] == "FR-NAME", call


def test_fm4_a_bad_tag_prints_its_cause_before_the_usage_error(world):
    call = world.fresh(tag="bad")
    assert call.code == 4 and "ERROR: UsageError" in call.lines, call
    causes = [i for i, x in enumerate(call.lines) if re.fullmatch(r"CAUSE fresh FR-USAGE-TAG: \S.*", x)]
    assert causes and causes[0] < call.lines.index("ERROR: UsageError"), call


def test_fm4_a_flag_inside_the_sets_root_prints_a_usage_cause_before_the_usage_error(world):
    call = world.fresh(runs=world.sets / "inside")
    assert call.code == 4 and "ERROR: UsageError" in call.lines, call
    causes = [i for i, x in enumerate(call.lines) if re.fullmatch(r"CAUSE fresh FR-USAGE-FLAG-INSIDE-SETS-ROOT: \S.*", x)]
    assert causes and causes[0] < call.lines.index("ERROR: UsageError"), call
    assert not (world.sets / "inside").exists()
