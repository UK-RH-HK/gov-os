"""S13, S14, S15, S17 (success-13, -14, -15, -17), F6 (failure-6), F8 (failure-8); I4, I7: the memory standard's practice.

The practice is carried by ``gov.memaudit`` (W2-170's set record, W2-171's measure, W2-172's driver), which this ticket calls
and never copies (S20). The cases here plant sets of stand-in questions (W2-170's ``clean_specs``, written for the tests, never
a real question) and judge what the core does with them. **Most of these cases are GREEN on the base, because the core exists
and the KPI is the adopted repository's use of it** (README names each: marked GUARD). The red ones are those that read the
proof record (``docs/changes/W2-88-evidence.md``) or the variant briefs A9 writes.
"""

from __future__ import annotations

import re

import pytest

import w2_170_world as V
import w2_88_sets_support as T
import w2_88_support as W

EVIDENCE = W.REPO_ROOT / W.EVIDENCE_REL
CHECKS = ("path missing 0", "heading on no line 0", "heading on more than one line 0", "unresolved 0", "quota PASS")


def ready(world, drops=()):
    world.write_set(V.clean_specs())
    run = world.preflight()
    assert run.code == 0, run
    world.write_notes(2, {q: ("reject", "R1-WRONG") for q in drops})
    assert world.void().code == 0


# ---- S13: the tuning set's checks -----------------------------------------------------------------------------

def test_s13_guard_a_planted_clean_set_passes_every_check_with_the_quota_met(pworld):
    pworld.write_set(V.clean_specs())
    run = pworld.preflight()
    blocks, _ = V.pf_blocks(run.out)
    assert run.code == 0 and run.last == V.FINAL_OK, run
    assert blocks["PF-QUOTA"]["word"] == "ok" and blocks["PF-SOURCE"]["word"] == "ok", blocks


def test_s13_guard_a_planted_set_with_a_path_missing_is_refused_on_that_check(pworld):
    specs = V.clean_specs()
    V.by_id(specs, "q11")["sources"].append(V.source("docs/plan/gone.md", heading=None, lines=(1, 2)))
    pworld.write_set(specs)
    run = pworld.preflight()
    blocks, _ = V.pf_blocks(run.out)
    assert run.code == 1 and blocks["PF-SOURCE"]["word"] == "refused" and blocks["PF-SOURCE"]["ids"] == ["q11"], run


def test_s13_the_proof_record_holds_the_sets_checks():
    assert EVIDENCE.is_file(), f"{W.EVIDENCE_REL} is not written (red until the engineer writes the proof record)"
    text = EVIDENCE.read_text(encoding="utf-8")
    missing = [check for check in CHECKS if check.lower() not in text.lower()]
    assert not missing, f"the proof record does not hold the set checks: {missing}"


# ---- S14 / F6: the verdict set, used once ----------------------------------------------------------------------

def test_s14_guard_the_declaration_is_written_before_the_used_marker(pworld):
    ready(pworld)
    assert pworld.declare().code == 0
    declaration, used = pworld.run_dir / "DECLARATION.json", pworld.run_dir / "USED"
    assert declaration.is_file() and used.is_file()
    assert declaration.stat().st_mtime_ns < used.stat().st_mtime_ns, "the declaration is not earlier than the USED marker"


@pytest.mark.parametrize("sub", ["declare", "preflight", "void"])
def test_s14_f6_guard_a_planted_used_marker_makes_the_runner_refuse(pworld, sub):
    ready(pworld)
    (pworld.run_dir / "USED").write_text("planted\n", encoding="utf-8")
    run = {"declare": pworld.declare, "preflight": pworld.preflight, "void": pworld.void}[sub]()
    assert run.code == 3 and "USED" in run.lines, f"{sub} with USED present: {run}"


def test_s14_f6_guard_a_measured_role_is_refused_a_read_of_the_set_and_the_orchestrator_is_not(pworld):
    """ACT-GUARD-SETS-1 (existing, I7): ``gov.guard.reads.parts`` lists the protected parts of a session; the planted set's
    entry measures the engineer, so the engineer has a protected part (the hidden globs) and the orchestrator has none."""
    from gov.guard import reads
    engineer = reads.parts(str(pworld.repo), "engineer", None)
    orchestrator = reads.parts(str(pworld.repo), "orchestrator", None)
    assert engineer, "the engineer, a role the planted set measures, is refused nothing"
    assert not orchestrator, "the orchestrator, a role no set measures, is refused a part"


# ---- S15: the bar ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("n, drops", [(40, ()), (37, ("q27", "q33", "q34"))])
def test_s15_guard_the_declared_bar_is_ceil_085_n_right_and_floor_005_n_wrong(pworld, n, drops):
    ready(pworld, drops)
    assert pworld.declare().code == 0
    doc = pworld.json_of("DECLARATION.json")
    assert doc["n"] == n and doc["bar"] == V.bar(n), f"the declared bar for n={n}: {doc['bar']}"


def test_s15_the_figures_printer_states_the_verdict_and_the_side_table():
    """The verdict line and the side table are ``gov.memaudit.figures.verdict_lines``'s five lines (W2-171's): the words the
    KPI names (right end to end, wrong claims, hit@5, gold in the first bundle, citation aside, one search against two with
    the exact McNemar, the exact 95 % interval, the second grader's agreement) are in its source."""
    import inspect
    from gov.memaudit import figures
    source = inspect.getsource(figures.verdict_lines)
    for word in ("VERDICT right end to end", "wrong claims", "hit@5", "first bundle", "citation aside",
                 "one search against two", "McNemar", "95 % interval", "grader agreement"):
        assert word in source, f"verdict_lines does not state: {word}"


# ---- S17: a miss is a result -----------------------------------------------------------------------------------

def test_s17_guard_the_runner_refuses_a_set_marked_used_and_changes_nothing(pworld):
    ready(pworld)
    assert pworld.declare().code == 0
    before = V.snapshot(pworld.sets, pworld.launch)
    for run in (pworld.declare(), pworld.preflight(), pworld.void()):
        assert run.code == 3 and "USED" in run.lines, run
    assert V.snapshot(pworld.sets, pworld.launch) == before, "a refused run wrote something"


# ---- F8: a question written with the product's own search ------------------------------------------------------

@pytest.mark.parametrize("kind", T.KINDS)
def test_f8_guard_the_gov_os_briefs_forbid_the_products_own_search(kind):
    text = T.gov_brief(kind)
    section = text[text.index("## 4."):text.index("## 5.")]
    assert "gov retrieve" in section, f"the Gov OS {kind} brief does not forbid `gov retrieve` in its section 4"


@pytest.mark.parametrize("kind", ["writer", "checker"])
def test_f8_a_variant_brief_keeps_the_products_own_search_forbidden(worlds, kind):
    nine = worlds.a9("audit", audit_tools=True)
    nine.record()
    files = T.variant_files(nine.out / "memory-audit" / "briefs")
    assert kind in files, f"no {kind} variant under memory-audit/briefs/"
    text = files[kind].read_text(encoding="utf-8")
    assert re.search(r"never read", text, re.I) and "gov retrieve" in text, \
        f"the {kind} variant's list of what it must never read no longer names `gov retrieve`"
