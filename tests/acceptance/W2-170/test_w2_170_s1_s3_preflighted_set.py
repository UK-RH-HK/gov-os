"""S1, S3, F2 (batch 2): the pre-flighted set is the set declared (Interface section 10, reading 9; review round 1's RV1).

Reading 9: ``PREFLIGHT.json`` records each delivered file's sha256 by id; ``DC-PREFLIGHT`` also refuses when a kept
file is not byte-equal to a pre-flighted one, so a set whose writer round 2 replaced ``hidden/`` after the pre-flight
is never marked ``USED`` until it is pre-flighted again. Sections 3 and 5 read with this line: the refusal is exit 1,
``DC-PREFLIGHT`` printed, and "writing nothing" (no map entry, no ``DECLARATION.json``, no ledger line, no ``USED``).

The flow is the callers' (writer round 1, the pre-flight, checker round 1, writer round 2, checker round 2): the set is
planted and pre-flighted; round 2 re-delivers the whole set (the writer brief section 6: "You write the whole set
again"), some files replaced; ``XCHECK-r2.md`` gives the checker's second pass; ``void``; ``declare``.

RV1 as review round 1 described it (DEC-136): a set pre-flighted clean; afterwards files in ``hidden/`` replaced; the
round-2 notes accept them; ``void`` exits 0; ``declare`` exited 0 and wrote ``USED`` for a set whose current files were
never pre-flighted.
"""

from __future__ import annotations

import os
import re

import pytest

import w2_170_world as W

HEX64 = re.compile(r"[0-9a-f]{64}")
NEW_WORD = "brambleshoxt"          # a word only round 2's re-worded question carries (F1)
FORBIDDEN = ("fixtures/", "runs/", "indep-walls/", "hidden")


# -- helpers --------------------------------------------------------------------------------------------------------
def _digests(world) -> dict[str, str]:
    """The delivered files now in ``hidden/`` (flat, not ``dropped/``): id -> sha256 hex of the file's bytes."""
    return {p.stem: W.sha_file(p) for p in sorted(world.hidden.glob("q*.yaml")) if p.is_file()}


def _walk(node):
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from _walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk(value)


def _holds_digests_by_id(doc, expected: dict[str, str]) -> bool:
    """Key-agnostic: somewhere in ``doc`` either (a) a JSON object whose keys are exactly the delivered ids and whose
    value for each id is that file's digest (or an object holding that digest as one of its values), or (b) a list of
    objects, one per delivered id, each pairing exactly one delivered id with exactly one 64-hex digest, the pairs
    being exactly ``expected``."""
    for node in _walk(doc):
        if isinstance(node, dict) and node and set(node) == set(expected):
            if all(v == expected[k] or (isinstance(v, dict) and expected[k] in v.values()) for k, v in node.items()):
                return True
        if isinstance(node, list) and len(node) == len(expected) and node and all(isinstance(x, dict) for x in node):
            pairs = set()
            for item in node:
                strings = [v for v in item.values() if isinstance(v, str)]
                ids = [v for v in strings if v in expected]
                digests = [v for v in strings if HEX64.fullmatch(v)]
                if len(ids) == 1 and len(digests) == 1:
                    pairs.add((ids[0], digests[0]))
            if pairs == set(expected.items()):
                return True
    return False


def _assert_digests_by_id(world, expected: dict[str, str]) -> None:
    doc = world.json_of("PREFLIGHT.json")
    assert _holds_digests_by_id(doc, expected), (
        "PREFLIGHT.json does not record each delivered file's sha256 by id (reading 9)", sorted(expected)[:3], doc)


def _round_two(world, specs, notes: dict | None = None) -> None:
    """Writer round 2 re-delivers the whole set as ``specs``; checker round 1 and round 2 notes are written (round 2
    accepts every question unless ``notes`` says otherwise)."""
    world.write_notes(1)
    world.write_set(specs)
    world.write_notes(2, notes or {})


def _bump_mtimes(world) -> None:
    """Every file of ``hidden/`` gets a later modification time, as a re-delivery would give it."""
    for path in world.hidden.glob("q*.yaml"):
        st = path.stat()
        os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))


def _refused_writing_nothing(world, run, before) -> None:
    """Section 5's refusal: exit 1, ``DC-PREFLIGHT`` printed, and nothing written (no map entry, no
    ``DECLARATION.json``, no ``declaration`` or ``used`` ledger line, no ``USED``)."""
    assert run.code == 1, ("declare must refuse a set whose kept files were not all pre-flighted", run)
    assert any(x.startswith("DC-PREFLIGHT") for x in run.lines), run
    assert "USED written" not in run.lines, run
    assert not (world.run_dir / "USED").exists()
    assert not (world.run_dir / "DECLARATION.json").exists()
    events = [e["event"] for e in world.ledger()]
    assert "declaration" not in events and "used" not in events, events
    from gov.util.parts import evaluation_sets
    assert W.AUDIT not in evaluation_sets(str(world.sets)), "the sets root's map gained the audit's entry"
    assert W.snapshot(world.sets, world.launch) == before


def _declared(world, run, n: int) -> None:
    assert run.code == 0, run
    assert "USED written" in run.lines, run
    assert (world.run_dir / "USED").exists()
    doc = world.json_of("DECLARATION.json")
    assert doc["ok"] is True and doc["n"] == n, doc
    assert doc["set_digest"] == W.set_digest(world.hidden)
    events = [e["event"] for e in world.ledger()]
    assert events.index("declaration") < events.index("used"), events


def _rv1_specs(world) -> list[dict]:
    """Round 2's replacements that a pre-flight would refuse: q08 gets the earlier commit (PF-COMMIT), q11 a source
    missing at the audit commit (PF-SOURCE). First sources, categories and counts are unchanged."""
    specs = W.clean_specs()
    W.by_id(specs, "q08")["commit"] = world.base_commit
    W.by_id(specs, "q11")["sources"].append(W.source("docs/plan/gone.md", heading=None, lines=(1, 2)))
    return specs


def _valid_replacement_specs() -> list[dict]:
    """Round 2's replacements that a pre-flight would pass: q05 re-worded, q12 re-anchored to other lines inside its
    file. First sources, categories and counts are unchanged."""
    specs = W.clean_specs()
    W.by_id(specs, "q05")["question"] = "Which decision does item 105 of the register state, in its own words?"
    W.by_id(specs, "q12")["sources"][0] = W.source("docs/plan/p12.md", lines=(3, 9))
    return specs


# -- 1 RV1 as described ---------------------------------------------------------------------------------------------
def test_s3_rv1_files_replaced_after_a_clean_preflight_are_refused_by_dc_preflight_writing_nothing(world):
    world.write_set(W.clean_specs())
    assert world.preflight().code == 0                        # pre-flighted clean
    _round_two(world, _rv1_specs(world))                      # round 2 replaces q08 and q11; r2 accepts every one
    void = world.void()
    assert void.code == 0, void
    before = W.snapshot(world.sets, world.launch)
    _refused_writing_nothing(world, world.declare(), before)
    # the replaced set is one a pre-flight refuses (the planted defects are real defects of the set)
    again = world.preflight()
    blocks, _ = W.pf_blocks(again.out)
    assert again.code == 1 and again.last == W.FINAL_NOT, again
    assert blocks["PF-COMMIT"]["ids"] == ["q08"] and blocks["PF-SOURCE"]["ids"] == ["q11"], again
    before = W.snapshot(world.sets, world.launch)
    _refused_writing_nothing(world, world.declare(), before)


# -- 2 byte-equal, not "still valid" --------------------------------------------------------------------------------
def _reworded(world):
    specs = W.clean_specs()
    W.by_id(specs, "q05")["question"] = "Which decision does item 105 of the register state, in its own words?"
    world.write_set(specs)


def _keyword_marked(world):
    specs = W.clean_specs()
    W.by_id(specs, "q12")["extra"] = {"keyword": True}          # a revise the writer brief names
    world.write_set(specs)


def _comment_appended(world):
    world.write_set(W.clean_specs())                            # the whole set re-delivered, byte-identical
    q05 = world.hidden / "q05.yaml"
    q05.write_bytes(q05.read_bytes() + b"# saved again by round 2\n")   # same YAML mapping, other bytes


_STILL_VALID = {"reworded-question": _reworded, "keyword-marked": _keyword_marked,
                "comment-appended": _comment_appended}


@pytest.mark.parametrize("change", sorted(_STILL_VALID))
def test_s3_a_kept_file_rewritten_but_still_valid_is_refused_by_dc_preflight(world, change):
    world.write_set(W.clean_specs())
    assert world.preflight().code == 0
    world.write_notes(1)
    _STILL_VALID[change](world)
    world.write_notes(2)
    void = world.void()
    assert void.code == 0, void
    before = W.snapshot(world.sets, world.launch)
    _refused_writing_nothing(world, world.declare(), before)


# -- 3 a kept file whose id was never pre-flighted -------------------------------------------------------------------
def test_s3_a_kept_file_whose_id_was_never_preflighted_is_refused_by_dc_preflight(world):
    world.write_set(W.without(W.clean_specs(), "q40"))       # 39 files: every check as expected
    assert world.preflight().code == 0
    _round_two(world, W.clean_specs())                        # round 2 delivers q40 as well; r2 accepts all 40
    void = world.void()
    assert void.code == 0, void
    before = W.snapshot(world.sets, world.launch)
    _refused_writing_nothing(world, world.declare(), before)


# -- 4 pre-flighted again, it goes on --------------------------------------------------------------------------------
def test_s3_f2_a_replaced_set_preflighted_again_is_declared_and_marked_used(world):
    world.write_set(W.clean_specs())
    assert world.preflight().code == 0
    _round_two(world, _valid_replacement_specs())
    assert world.void().code == 0
    before = W.snapshot(world.sets, world.launch)
    _refused_writing_nothing(world, world.declare(), before)  # not until it is pre-flighted again
    again = world.preflight()
    assert again.code == 0 and again.last == W.FINAL_OK, again
    _assert_digests_by_id(world, _digests(world))             # the new bytes are the ones recorded
    _declared(world, world.declare(), 40)


# -- 5 PREFLIGHT.json records each delivered file's sha256 by id -----------------------------------------------------
def _clean_forty(world):
    world.write_set(W.clean_specs())
    return 0


def _commit_refused(world):
    specs = W.clean_specs()
    W.by_id(specs, "q08")["commit"] = world.base_commit
    world.write_set(specs)
    return 1


def _thirty_five(world):
    world.write_set(W.without(W.clean_specs(), "q27", "q28", "q29", "q33", "q34"))
    return 1


def _thirty_nine(world):
    world.write_set(W.without(W.clean_specs(), "q40"))
    return 0


_DELIVERED = {"clean-40": _clean_forty, "refused-pf-commit": _commit_refused, "refused-pf-count-35": _thirty_five,
              "clean-39": _thirty_nine}


@pytest.mark.parametrize("delivery", sorted(_DELIVERED))
def test_s1_preflight_json_records_each_delivered_file_s_sha256_by_id(world, delivery):
    expected_exit = _DELIVERED[delivery](world)
    run = world.preflight()
    assert run.code == expected_exit, run
    expected = _digests(world)
    assert len(expected) in (35, 39, 40)
    _assert_digests_by_id(world, expected)


# -- 6 the S3 flow stays green ---------------------------------------------------------------------------------------
def test_s3_f2_a_byte_identical_redelivery_after_the_preflight_goes_on(world):
    world.write_set(W.clean_specs())
    assert world.preflight().code == 0
    _round_two(world, W.clean_specs())                        # every file written again, the same bytes
    _bump_mtimes(world)                                       # later times: bytes decide, not times
    assert world.void().code == 0
    _declared(world, world.declare(), 40)


def _replaced_then_dropped(world):
    """Round 2 replaces q27, q33 and q34 (even with defects); the checker's second pass rejects them."""
    world.write_set(W.clean_specs())
    assert world.preflight().code == 0
    specs = W.clean_specs()
    for qid in ("q27", "q33", "q34"):
        W.by_id(specs, qid)["question"] = f"A new question of round 2 under the id {qid}?"
        W.by_id(specs, qid)["commit"] = world.base_commit
    _round_two(world, specs, {q: ("reject", "R1-WRONG") for q in ("q27", "q33", "q34")})
    return 37


def _new_then_dropped(world):
    """Round 2 delivers q40, never pre-flighted; the checker's second pass rejects it."""
    world.write_set(W.without(W.clean_specs(), "q40"))
    assert world.preflight().code == 0
    _round_two(world, W.clean_specs(), {"q40": ("reject", "R3-ID-EXISTS")})
    return 39


_DROPPED = {"replaced-then-dropped": _replaced_then_dropped, "new-then-dropped": _new_then_dropped}


@pytest.mark.parametrize("flow", sorted(_DROPPED))
def test_s3_f2_files_dropped_after_round_two_need_not_match_the_preflight(world, flow):
    kept = _DROPPED[flow](world)
    void = world.void()
    assert void.code == 0, void
    assert f"DROPS: kept {kept} dropped {40 - kept}" in void.lines, void
    _declared(world, world.declare(), kept)


# -- 7 S5 / F1 for the new record ------------------------------------------------------------------------------------
def _outputs(world) -> str:
    texts = [world.sets_map.read_text(encoding="utf-8", errors="replace")] if world.sets_map.exists() else []
    if world.run_dir.exists():
        for folder, _, names in os.walk(world.run_dir):
            texts += [open(os.path.join(folder, n), encoding="utf-8", errors="replace").read() for n in names]
    return "\n".join(texts)


def test_s1_f1_the_digest_record_and_the_refusal_carry_ids_and_digests_only(world):
    world.write_set(W.clean_specs())
    runs = [world.preflight()]
    assert runs[0].code == 0, runs[0]
    specs = W.clean_specs()
    W.by_id(specs, W.SPECIAL)["question"] = f"Which {W.QWORD} {NEW_WORD} rule does the contract set?"
    _round_two(world, specs)                                  # q07 replaced, its words still the planted ones
    runs.append(world.void())
    assert runs[1].code == 0, runs[1]
    runs += [world.declare(), world.preflight(), world.declare()]
    words = (*W.UNIQUE, NEW_WORD)
    preflight_json = (world.run_dir / "PREFLIGHT.json").read_text(encoding="utf-8")
    for text in [r.out + r.err for r in runs] + [_outputs(world), preflight_json]:
        found = {w: text.count(w) for w in words if w in text}
        assert found == {}, found
    for spec in specs:
        for entry in spec["sources"]:
            for alternative in (entry if isinstance(entry, list) else [entry]):
                assert alternative["path"] not in preflight_json, alternative["path"]
                if alternative.get("heading"):
                    assert alternative["heading"] not in preflight_json, alternative["heading"]
    real = os.path.realpath(world.sets)
    for run in runs:
        text = run.out + run.err
        assert "Traceback" not in text, run
        assert real + "/" not in text and str(world.sets) + "/" not in text, run
        assert not any(f in line for line in run.lines for f in FORBIDDEN), run
        for line in text.splitlines():
            if line.startswith("ERROR"):
                assert re.fullmatch(r"ERROR: [A-Za-z_][\w.]*", line), line
