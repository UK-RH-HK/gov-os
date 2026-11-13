"""S3 and F2: ``declare`` writes the sets root map's entry, ``DECLARATION.json``, the ``declaration`` ledger line,
``USED`` and the ``used`` ledger line, in that order (Interface 5); every key of the declaration with its value; a set
is measured once (``USED`` present: exit 3, prints ``USED``, writes nothing); a ``retrieval.yaml`` with the pool off
is not ok without ``--decision``; the other ``DC-`` refusals write nothing.

The flow is the callers': ``preflight`` (exit 0), ``void`` (exit 0), then ``declare --store <file> --gov <link>``.
"""

from __future__ import annotations

import sqlite3
import stat
from datetime import datetime, timezone

import pytest

import w2_170_world as W

DROPS = {36: ["q27", "q28", "q33", "q34"], 37: ["q27", "q33", "q34"], 40: []}


def _ready(world, drops=()):
    """The set planted, pre-flighted and voided, ready for ``declare``."""
    world.write_set(W.clean_specs())
    run = world.preflight()
    assert run.code == 0, run
    world.write_notes(2, {q: ("reject", "R1-WRONG") for q in drops})
    run = world.void()
    assert run.code == 0, run


def _iso_utc(text: str) -> datetime:
    when = datetime.fromisoformat(text.replace("Z", "+00:00"))
    assert when.utcoffset() is not None and when.utcoffset().total_seconds() == 0, text
    return when


@pytest.mark.parametrize("n", sorted(DROPS))
def test_s3_declare_writes_every_key_of_the_declaration_with_its_value(world, n):
    _ready(world, DROPS[n])
    run = world.declare()
    assert run.code == 0, run
    doc = world.json_of("DECLARATION.json")
    assert all(key in doc for key in W.DECLARATION_KEYS), sorted(doc)
    assert doc["audit"] == W.AUDIT
    assert doc["audit_commit"] == world.audit_commit
    assert doc["store_commit"] == world.audit_commit
    assert doc["store_sha256"] == W.sha_file(world.store)
    assert doc["gov_pin"] == W.PIN
    assert doc["retrieval_yaml_sha256"] == W.sha_bytes(world.show("governance/project/retrieval.yaml"))
    assert doc["set_digest"] == W.set_digest(world.hidden)
    assert doc["n"] == n
    assert doc["settings"] == {"reranker": "shared", "pool": True, "bundle_tokens": 6000, "search_again_once": True}
    assert doc["nonstandard"] == [] and doc["decision"] is None and doc["ok"] is True
    assert doc["bar"] == W.bar(n)
    assert doc["rounding"] == W.ROUNDING
    _iso_utc(doc["declared_at"])
    assert f"DECLARED: audit commit {world.audit_commit[:12]}, n {n}, set digest {doc['set_digest'][:12]}" \
        in run.lines, run
    assert "USED written" in run.lines, run


def test_s3_the_bar_for_37_is_32_right_1_wrong_target_36(world):
    _ready(world, DROPS[37])
    assert world.declare().code == 0
    assert world.json_of("DECLARATION.json")["bar"] == {"need_right": 32, "max_wrong": 1, "target_right": 36}


def test_f2_declaration_then_used_by_file_times_and_ledger_order(world):
    _ready(world, DROPS[37])
    run = world.declare()
    assert run.code == 0, run
    declaration, used = world.run_dir / "DECLARATION.json", world.run_dir / "USED"
    assert world.sets_map.stat().st_mtime_ns <= declaration.stat().st_mtime_ns
    assert declaration.stat().st_mtime_ns < used.stat().st_mtime_ns     # strictly later, in nanoseconds
    ledger = world.ledger()
    seqs = [e["seq"] for e in ledger]
    assert seqs == list(range(seqs[0], seqs[0] + len(seqs))), seqs
    assert all("at" in e and "event" in e for e in ledger)
    events = [e["event"] for e in ledger]
    for earlier, later in [("preflight", "drop"), ("drop", "declaration"), ("declaration", "used")]:
        assert events.index(earlier) < events.index(later), events
    assert "search" not in events


def test_s3_used_holds_one_line_naming_the_audit_and_the_declaration_s_sha256(world):
    _ready(world)
    assert world.declare().code == 0
    text = (world.run_dir / "USED").read_text(encoding="utf-8")
    assert text.count("\n") <= 1 and len(text.splitlines()) == 1, text
    when, audit, digest = text.split()
    _iso_utc(when)
    assert audit == W.AUDIT
    assert digest == W.sha_file(world.run_dir / "DECLARATION.json")


@pytest.mark.parametrize("sub", ["declare", "preflight", "void"])
def test_f2_with_used_present_every_subcommand_exits_3_prints_used_and_writes_nothing(world, sub):
    _ready(world)
    assert world.declare().code == 0
    before = W.snapshot(world.sets, world.launch)
    run = {"declare": world.declare, "preflight": world.preflight, "void": world.void}[sub]()
    assert run.code == 3, run
    assert "USED" in run.lines, run
    assert not any(x.startswith("DC-") for x in run.lines), run
    assert W.snapshot(world.sets, world.launch) == before


def test_s3_a_planted_used_marker_alone_refuses_the_declaration(world):
    _ready(world)
    (world.run_dir / "USED").write_text("planted\n", encoding="utf-8")
    run = world.declare()
    assert run.code == 3 and "USED" in run.lines, run
    assert not (world.run_dir / "DECLARATION.json").exists()


def test_s3_the_pool_off_without_a_decision_is_named_and_not_ok_and_writes_no_used(make_world):
    world = make_world("pool_off")
    _ready(world)
    run = world.declare()
    assert run.code == 1, run
    assert "DC-DECISION pool" in run.lines, run
    doc = world.json_of("DECLARATION.json")
    assert doc["ok"] is False and doc["decision"] is None
    assert doc["nonstandard"] == ["pool"] and doc["settings"]["pool"] is False
    assert not (world.run_dir / "USED").exists()


def test_s3_the_pool_off_with_a_decision_is_ok_and_writes_used(make_world):
    world = make_world("pool_off")
    _ready(world)
    assert world.declare().code == 1                      # first without: not ok, no USED
    run = world.declare(decision="DEC-1234")              # allowed while USED is absent
    assert run.code == 0, run
    doc = world.json_of("DECLARATION.json")
    assert (doc["ok"], doc["decision"], doc["nonstandard"]) == (True, "DEC-1234", ["pool"])
    assert (world.run_dir / "USED").exists()


def test_s3_a_decision_with_the_standard_file_is_recorded_as_given(world):
    _ready(world)
    run = world.declare(decision="DEC-7")
    assert run.code == 0, run
    doc = world.json_of("DECLARATION.json")
    assert (doc["ok"], doc["decision"], doc["nonstandard"]) == (True, "DEC-7", [])


def test_s3_a_decision_not_of_the_form_dec_n_is_a_usage_refusal(world):
    _ready(world)
    before = W.snapshot(world.sets)
    run = world.declare(decision="dec-12")
    assert run.code == 4, run
    assert W.snapshot(world.sets) == before


def test_s3_the_commit_flag_is_resolved_to_40_hex_digits(world):
    _ready(world)
    run = world.declare(commit=world.audit_commit[:12])
    assert run.code == 0, run
    assert world.json_of("DECLARATION.json")["audit_commit"] == world.audit_commit


def test_s3_preflight_makes_the_audit_s_run_folder_with_mode_700(world):
    world.write_set(W.clean_specs())
    assert not world.run_dir.exists()
    run = world.preflight()
    assert run.code == 0, run
    assert stat.S_IMODE(world.run_dir.stat().st_mode) == 0o700


# -- the DC- refusals: exit 1, the code printed, nothing written ---------------------------------------------------
def _store_with(path, head):
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE fingerprints (head TEXT NOT NULL, code TEXT, records TEXT, kind TEXT NOT NULL)")
    connection.execute("INSERT INTO fingerprints VALUES (?, ?, ?, ?)", (head, "c", "r", "rebuild"))
    connection.commit()
    connection.close()


def _no_table(path):
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE records (id TEXT)")
    connection.commit()
    connection.close()


_REFUSALS = {
    "preflight-absent": ("DC-PREFLIGHT", lambda w: (w.run_dir / "PREFLIGHT.json").unlink(), {}),
    "drops-absent": ("DC-DROPS", lambda w: (w.run_dir / "DROPS.json").unlink(), {}),
    "hidden-changed-since-drops": ("DC-DROPS", lambda w: (w.hidden / "q01.yaml").write_text(
        (w.hidden / "q01.yaml").read_text(encoding="utf-8") + "# edited\n", encoding="utf-8"), {}),
    "store-absent": ("DC-STORE", lambda w: None, {"store": "missing.db"}),
    "store-not-a-database": ("DC-STORE", lambda w: (w.base / "garbage.db").write_bytes(b"not a database" * 64),
                             {"store": "garbage.db"}),
    "store-without-fingerprints": ("DC-STORE", lambda w: _no_table(w.base / "old.db"), {"store": "old.db"}),
    "store-head-not-the-audit-commit": ("DC-STORE", lambda w: _store_with(w.base / "other.db", w.base_commit),
                                        {"store": "other.db"}),
    "gov-without-a-pin": ("DC-PIN", lambda w: None, {"gov": "unpinned"}),
}


@pytest.mark.parametrize("case", sorted(_REFUSALS))
def test_s3_each_dc_refusal_exits_1_with_its_code_and_writes_nothing(world, case):
    code, prepare, flags = _REFUSALS[case]
    _ready(world)
    prepare(world)
    kw = {}
    if "store" in flags:
        kw["store"] = world.base / flags["store"]
    if "gov" in flags:
        kw["gov"] = world.gov_unpinned
    before = W.snapshot(world.sets, world.launch)
    run = world.declare(**kw)
    assert run.code == 1, run
    assert any(x.startswith(code) for x in run.lines), run
    assert W.snapshot(world.sets, world.launch) == before
    assert not (world.run_dir / "DECLARATION.json").exists() and not (world.run_dir / "USED").exists()


def test_s3_dc_preflight_refuses_a_preflight_that_was_not_ok(world):
    specs = W.clean_specs()
    W.by_id(specs, "q08")["commit"] = world.base_commit
    world.write_set(specs)
    assert world.preflight().code == 1
    world.write_notes(2)
    assert world.void().code == 0
    before = W.snapshot(world.sets)
    run = world.declare()
    assert run.code == 1 and any(x.startswith("DC-PREFLIGHT") for x in run.lines), run
    assert W.snapshot(world.sets) == before


def test_s3_dc_drops_refuses_a_void_audit(world):
    world.write_set(W.clean_specs())
    assert world.preflight().code == 0
    world.write_notes(2, {q: ("reject", "R1-WRONG") for q in ["q27", "q28", "q29", "q33", "q34"]})
    assert world.void().code == 2
    before = W.snapshot(world.sets)
    run = world.declare()
    assert run.code == 1 and any(x.startswith("DC-DROPS") for x in run.lines), run
    assert W.snapshot(world.sets) == before
    assert not (world.run_dir / "DECLARATION.json").exists() and not (world.run_dir / "USED").exists()


@pytest.mark.parametrize("variant", ["no_retrieval", "retrieval_list"])
def test_s3_dc_retrieval_refuses_a_missing_or_unmapped_retrieval_yaml(make_world, variant):
    world = make_world(variant)
    _ready(world)
    before = W.snapshot(world.sets)
    run = world.declare()
    assert run.code == 1 and any(x.startswith("DC-RETRIEVAL") for x in run.lines), run
    assert W.snapshot(world.sets) == before
