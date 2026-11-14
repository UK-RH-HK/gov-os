"""W2-94 (DAEO-g87r), S13 (2026-11-14, rv-fix P4, DEC-1180 (4)): the counts schema takes the fix flow's ``fix`` key.

Written from the KPI line and the lead's interface text, as described behaviour (DEC-136): ``indep-counts.schema.json``
allows an optional top-level ``fix`` object with exactly ``id`` (``q`` and two digits), ``code`` (one of the eight
reason codes) and ``action`` (``corrected``, ``replaced`` or ``null`` until the result has passed its checks), and
nothing else; a counts object without ``fix`` validates as before.

Every run is the launch script as a process on the planted world of ``w2_94_fix_support`` (``FixWorld``) or W2-149's
seam (``World``), with the stub ``claude``. The schema is the one beside the script under test (``W2_94_FIX_SCRIPT``
moves both), checked with the script's own ``schema_ok``. Planted words begin with ``zqxw94``; nothing under
``~/gov-os-eval`` or ``~/gov-os-runs`` is opened.
"""

from __future__ import annotations

import copy
import json

import pytest

from w2_94_fix_support import CODE, FIX_CODES, SCRIPT, SETN, FixWorld, World, good_out, indep_launch, writer_out


def counts_schema():
    """The counts schema beside the script under test, as the script reads it (``COUNTS_SCHEMA``)."""
    return json.loads((SCRIPT.parent / "indep-schemas" / indep_launch.COUNTS_SCHEMA).read_text())


def valid(obj):
    return indep_launch.schema_ok(obj, counts_schema())


def without_fix(counts):
    return {k: v for k, v in counts.items() if k != "fix"}


def on_disk(w, counts):
    return json.loads((w.runs / "writer" / counts["run"] / "counts.json").read_text())


def log_text(w, counts):
    p = w.runs / "writer" / counts["run"] / "launch.log"
    assert p.exists(), "the run wrote no launch.log"
    return p.read_text()


def assert_validates_with_fix(counts, action):
    assert counts["fix"] == {"id": "q02", "code": CODE, "action": action}, counts.get("fix")
    # control: the rest of the counts validates, so a failure below is the fix key's alone
    assert valid(without_fix(counts)), "the counts fail the schema even without their fix key"
    assert valid(counts), "the counts schema refuses the fix key"


@pytest.fixture
def fw(tmp_path):
    return FixWorld(tmp_path)


@pytest.fixture(scope="module")
def delivered(tmp_path_factory):
    """One delivered fix run (``corrected``): the world and its counts."""
    w = FixWorld(tmp_path_factory.mktemp("s13delivered"))
    w.session(good_out("corrected"))
    rc, counts, p = w.fix()
    assert rc == 0, (counts, p.stderr)
    assert counts["status"] == "delivered"
    return w, counts


# =====================================================================================================================
# S13, first Verify: a fix run's counts with fix validate
# =====================================================================================================================
@pytest.mark.parametrize("action", ["corrected", "replaced"])
def test_s13_a_delivered_fix_runs_counts_validate(fw, action):
    fw.session(good_out(action))
    rc, counts, p = fw.fix()
    assert rc == 0, (counts, p.stderr)
    assert counts["status"] == "delivered"
    assert_validates_with_fix(counts, action)
    assert_validates_with_fix(on_disk(fw, counts), action)


def test_s13_a_dry_fix_runs_counts_validate_with_the_action_null(fw):
    rc, counts, p = fw.dry_fix()
    assert rc == 0, p.stderr
    assert counts["status"] == "dry"
    assert_validates_with_fix(counts, None)
    assert_validates_with_fix(on_disk(fw, counts), None)
    assert "counts schema" not in log_text(fw, counts)


STOPPED_OUT = {"out/result.json": json.dumps({"stopped": "input-missing"}), "out/conflicts.md": "path classes\n"}


@pytest.mark.parametrize("out,code,status", [
    (good_out("fixed"), 20, "rejected"),
    (STOPPED_OUT, 21, "stopped"),
], ids=["refused 20 at the result", "stopped 21"])
def test_s13_a_fix_run_refused_at_the_result_or_stopped_validates_with_the_action_null(fw, out, code, status):
    fw.session(out)
    rc, counts, p = fw.fix()
    assert rc == code, (counts, p.stderr)
    assert counts["status"] == status
    assert_validates_with_fix(counts, None)
    assert_validates_with_fix(on_disk(fw, counts), None)
    assert "counts schema" not in log_text(fw, counts)


@pytest.mark.parametrize("code", FIX_CODES)
def test_s13_each_code_each_edge_id_and_each_action_validate(delivered, code):
    _w, counts = delivered
    assert valid(without_fix(counts)), "the counts fail the schema even without their fix key"
    wrong = []
    for qid in ("q00", "q02", "q99"):
        for action in ("corrected", "replaced", None):
            obj = copy.deepcopy(counts)
            obj["fix"] = {"id": qid, "code": code, "action": action}
            if not valid(obj):
                wrong.append((qid, action))
    assert not wrong, f"refused with code {code}: {wrong}"


# =====================================================================================================================
# S13, the visible effects: no "counts schema failed" line; --counts-only of a fix run is 0
# =====================================================================================================================
def test_s13_a_delivered_fix_runs_log_has_no_counts_schema_failure(delivered):
    w, counts = delivered
    text = log_text(w, counts)
    assert text.strip(), "the launch.log is empty"
    assert [ln for ln in text.splitlines() if "counts schema" in ln] == []


def test_s13_counts_only_of_a_delivered_fix_run_exits_0_and_prints_its_counts_with_fix(delivered):
    w, counts = delivered
    rc, printed, p = w.run("--sets-root", str(w.sets), "--kind", "writer", "--run", counts["run"], "--counts-only")
    assert rc == 0, (rc, printed, p.stderr)
    assert printed == on_disk(w, counts)
    assert printed["fix"] == {"id": "q02", "code": CODE, "action": "corrected"}


# =====================================================================================================================
# S13, second Verify: a fix with an extra key, a missing key or another value is refused
# =====================================================================================================================
def _with(**changes):
    def mutate(fix):
        for k, v in changes.items():
            fix[k] = v
        return fix
    return mutate


def _drop(key):
    def mutate(fix):
        del fix[key]
        return fix
    return mutate


def _whole(value):
    return lambda fix: value


REFUSED = {
    "an extra key": _with(extra="x"),
    "an extra key reason": _with(reason=CODE),
    "id missing": _drop("id"),
    "code missing": _drop("code"),
    "action missing": _drop("action"),
    "action another word": _with(action="fixed"),
    "action Corrected": _with(action="Corrected"),
    "action empty": _with(action=""),
    "action a list": _with(action=["corrected"]),
    "id q2": _with(id="q2"),
    "id Q02": _with(id="Q02"),
    "id q002": _with(id="q002"),
    "id q0a": _with(id="q0a"),
    "id null": _with(id=None),
    "code unknown": _with(code="UNKNOWN"),
    "code lower case": _with(code="answer_not_in_spans"),
    "code null": _with(code=None),
    "fix null": _whole(None),
    "fix a list": _whole([]),
    "fix a string": _whole("q02"),
    "fix empty": _whole({}),
}


@pytest.mark.parametrize("name", list(REFUSED))
def test_s13_a_fix_object_of_another_form_is_refused(delivered, name):
    _w, counts = delivered
    # control: the delivered counts validate as they are (red today: the schema refuses every fix key)
    assert valid(counts), "the counts schema refuses the fix key"
    obj = copy.deepcopy(counts)
    obj["fix"] = REFUSED[name](copy.deepcopy(counts["fix"]))
    assert not valid(obj), f"{name}: accepted {obj['fix']!r}"


# =====================================================================================================================
# S13, third Verify: counts without fix validate as before (a guard, green today and after)
# =====================================================================================================================
def _writer_round_two_without_fix(tmp):
    w = FixWorld(tmp)
    w.stub({"session": "write", "out": writer_out()})
    return w, w.run(*w.args("writer", rnd=2, set_name=SETN))


def _checker_dry(tmp):
    w = World(tmp)
    w.plant_set()
    return w, w.launch("checker", seed=17, dry=True)


def _auditor_dry(tmp):
    w = World(tmp)
    w.plant_set()
    (w.sets / "runs" / "e0").mkdir(parents=True)
    (w.sets / "runs" / "e0" / "misses.jsonl").write_text(json.dumps(
        {"id": "m1", "question": "zqxw94-q", "gold_answer": "zqxw94-g", "gold_sources": ["s"], "answer": "a",
         "outcome": "wrong", "evidence_in_bundle": False}) + "\n")
    return w, w.launch("auditor", audit="e0", seed=17, dry=True)


AS_BEFORE = {"writer round 2 without fix": (_writer_round_two_without_fix, 0, "delivered"),
             "checker dry run": (_checker_dry, 0, "dry"),
             "auditor dry run": (_auditor_dry, 0, "dry")}


@pytest.mark.parametrize("name", list(AS_BEFORE))
def test_s13_counts_without_fix_validate_as_before(tmp_path, name):
    plant, code, status = AS_BEFORE[name]
    w, (rc, counts, p) = plant(tmp_path)
    assert rc == code, (counts, p.stderr)
    assert counts["status"] == status
    assert "fix" not in counts
    assert valid(counts), counts
    kind_dir = w.runs / counts["kind"] / counts["run"]
    assert valid(json.loads((kind_dir / "counts.json").read_text()))
    assert "counts schema" not in (kind_dir / "launch.log").read_text()
