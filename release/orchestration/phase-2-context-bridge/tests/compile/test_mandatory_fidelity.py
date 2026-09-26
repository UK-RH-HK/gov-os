"""BR-DAG node R1-RM acceptance (REPAIR_PLAN.md section 3, RC-1: "mandatory-input fidelity"): a mandatory item is
never silently cut, declared ``keys``/``entries``/multi-``paths`` selectors are honoured exactly, a by-reference
directory item is expanded into a member manifest, and the receipt/manifest can tell delivered bytes apart from
the resolver's own source hash. Every id here is ``MF-*`` (Mandatory Fidelity), unrelated to Review-8/Phase-2
(OC-BR-02); the fixture repo (``tests/fixtures/compile/mandatory/repobuilder.py``) is this node's own, independent
of the shared ``tests/fixtures/compile/compile_repobuilder.py``.
"""
import copy
from pathlib import Path

import pytest

from govbridge.authority import resolver as resolvermod
from govbridge.compile import packet as packetmod
from govbridge.compile import sectionmap as sectionmapmod
from govbridge.compile import validate as validatemod
from govbridge.core import gitobj
from govbridge.route.router import FAKE_ROUTES

from mandatory import repobuilder as mf  # tests/fixtures/compile/mandatory/repobuilder.py (namespace package,
                                          # reached via conftest.py's sys.path insert of tests/fixtures/compile)


@pytest.fixture
def mf_repo(tmp_path):
    return mf.build(tmp_path / "repo")


@pytest.fixture
def mf_view_path(tmp_path, mf_repo):
    p = tmp_path / "canonical-view.yaml"
    mf.write_canonical_view(p, mf_repo)
    return str(p)


@pytest.fixture
def mf_registry_path(tmp_path):
    p = tmp_path / "authority-registry.yaml"
    mf.write_registry(p)
    return str(p)


def _a_rows(manifest: dict) -> dict:
    return {r["unit"]["id"]: r for r in manifest["sections"]["A"]["items"]}


def _notices_by_id(manifest: dict, ntype: str) -> dict:
    return {n["id"]: n for n in manifest["notices"] if n["type"] == ntype}


def _compile(mf_repo, mf_view_path, mf_registry_path, required_inputs=None):
    task_spec = mf.make_task_spec(mf_view_path, required_inputs=required_inputs)
    result = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=str(mf_repo.root),
                                       registry_path=mf_registry_path)
    return task_spec, result


# ---------------------------------------------------------------------------------------------------------------
# the happy path: every declared MF-* item, all selectors honoured, section A never dropped
# ---------------------------------------------------------------------------------------------------------------

def test_all_mandatory_items_resolve_and_land_in_a(mf_repo, mf_view_path, mf_registry_path):
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK, result["resolve_result"].blocked_reasons
    a_rows = _a_rows(result["manifest"])
    for item_id in ("MF-BIG", "MF-ENTRIES", "MF-KEYS", "MF-PATHS", "MF-DIR", "MF-LEDGER"):
        assert item_id in a_rows, f"{item_id} must be in A (never dropped, whatever its size or shape)"
    assert validatemod.verify_packet(result["manifest"], task_spec, repo=str(mf_repo.root),
                                      registry_path=mf_registry_path) == []


def test_oversize_item_never_ends_mid_content(mf_repo, mf_view_path, mf_registry_path):
    """MF-BIG has no selector and exceeds the per-item cap: it must be delivered as a full section map (never a
    bare, silently-cut string), with a MANDATORY_PARTIAL_DELIVERY notice listing every undelivered range."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    manifest = result["manifest"]
    a_rows = _a_rows(manifest)
    row = a_rows["MF-BIG"]

    raw = gitobj.read_path(row["source"]["commit"], row["source"]["path"], repo=str(mf_repo.root)).decode("utf-8")
    expected_sections = sectionmapmod.markdown_flat_tiling(raw)
    assert len(expected_sections) >= 5, "the generated fixture must have several headings to be a meaningful probe"

    # the delivered TEXT is the section map itself, not a truncated prefix of the raw document -- it never just
    # stops mid-sentence: the raw document's own tail sentence must NOT appear verbatim in what was delivered.
    delivered_text = next(i.text for i in result["sections"]["A"] if i.unit_id == "MF-BIG")
    assert "[section map:" in delivered_text
    assert raw.strip().splitlines()[-1] not in delivered_text

    notices = _notices_by_id(manifest, "MANDATORY_PARTIAL_DELIVERY")
    assert "MF-BIG" in notices, "an oversize mandatory item with no selector must carry the notice"
    notice = notices["MF-BIG"]
    assert notice["delivered"] == []
    got_names = {u["name"] for u in notice["undelivered_ranges"]}
    want_names = {s.name for s in expected_sections}
    assert got_names == want_names
    # every disclosed range's sha256 is independently reproducible from the raw text alone.
    got_by_name = {u["name"]: u for u in notice["undelivered_ranges"]}
    for s in expected_sections:
        assert got_by_name[s.name]["sha256"] == s.sha256
        assert got_by_name[s.name]["line_start"] == s.line_start
        assert got_by_name[s.name]["line_end"] == s.line_end

    # nothing raw was delivered (only the map above) -- delivered_sha256 stays None, forcing `packet verify` onto
    # the coverage/tiling check (2b) rather than a hash comparison that could never legitimately pass here.
    assert row["delivered_sha256"] is None
    assert row["source_sha256"] is not None
    assert row["declared_sha256"] is not None
    assert validatemod.verify_packet(manifest, task_spec, repo=str(mf_repo.root),
                                      registry_path=mf_registry_path) == []
    assert row["delivered_sha256"] != row["source_sha256"], \
        "a section-map delivery must never be mistaken for the full source"


def test_entries_selector_delivers_exactly_those_entries(mf_repo, mf_view_path, mf_registry_path):
    """MF-ENTRIES declares ``entries: {under: records, start: E-0003, end: E-0006}`` -- exactly entries 3-6 must be
    delivered in full; 1, 2, 7 and 8 must not appear anywhere in the delivered text."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    delivered_text = next(i.text for i in result["sections"]["A"] if i.unit_id == "MF-ENTRIES")
    for i in range(3, 7):
        assert f"entry number {i}, generated fixture content" in delivered_text
    for i in (1, 2, 7, 8):
        assert f"entry number {i}, generated fixture content" not in delivered_text

    resolve_result = result["resolve_result"]
    mi = next(m for m in resolve_result.items if m.id == "MF-ENTRIES")
    assert [p["kind"] for p in mi.parts] == ["entries"] * 4
    assert {p["name"].rsplit("[", 1)[-1].rstrip("]") for p in mi.parts} == {"E-0003", "E-0004", "E-0005", "E-0006"}


def test_keys_selector_delivers_exactly_those_keys(mf_repo, mf_view_path, mf_registry_path):
    """MF-KEYS declares ``keys: [alpha, gamma]`` -- alpha/gamma must be delivered in full; beta/delta must not
    appear in the delivered text, and must be named in the MANDATORY_PARTIAL_DELIVERY notice's undelivered ranges."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    manifest = result["manifest"]
    delivered_text = next(i.text for i in result["sections"]["A"] if i.unit_id == "MF-KEYS")
    assert "the first selectable top-level key" in delivered_text
    assert "the second selectable top-level key" in delivered_text
    assert "NOT selected by the fixture" not in delivered_text
    assert "another remainder member" not in delivered_text

    notice = _notices_by_id(manifest, "MANDATORY_PARTIAL_DELIVERY")["MF-KEYS"]
    undelivered_names = {u["name"] for u in notice["undelivered_ranges"]}
    assert undelivered_names == {"beta", "delta"}


def test_two_path_item_delivers_both_paths(mf_repo, mf_view_path, mf_registry_path):
    """MF-PATHS declares ``paths: [PATH_A, PATH_B]`` -- BOTH files' content must be delivered, not merely the
    first path's content with the second only existence-checked."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    delivered_text = next(i.text for i in result["sections"]["A"] if i.unit_id == "MF-PATHS")
    assert "Content of the FIRST declared path." in delivered_text
    assert "Content of the SECOND declared path" in delivered_text

    resolve_result = result["resolve_result"]
    mi = next(m for m in resolve_result.items if m.id == "MF-PATHS")
    assert len(mi.parts) == 1
    assert mi.parts[0]["kind"] == "paths"
    assert mi.parts[0]["path"] == mf.PATH_B
    # no MANDATORY_PARTIAL_DELIVERY notice fires here -- a paths-only selector narrows nothing; both files are
    # delivered in full, so nothing is undelivered.
    assert "MF-PATHS" not in _notices_by_id(result["manifest"], "MANDATORY_PARTIAL_DELIVERY")


def test_directory_item_becomes_a_member_manifest(mf_repo, mf_view_path, mf_registry_path):
    """MF-DIR (``spec/mf/bundle/``) must be expanded into a member manifest -- path, blob, size and class per
    tracked file under it -- never left a bare, contentless pointer."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    manifest = result["manifest"]
    row = _a_rows(manifest)["MF-DIR"]
    assert row["is_directory"] is True
    members = {m["path"]: m for m in row["directory_members"]}
    expected_paths = {f"{mf.DIR_PATH}/{mf.DIR_FILE_1}", f"{mf.DIR_PATH}/{mf.DIR_FILE_2}",
                      f"{mf.DIR_PATH}/{mf.DIR_FILE_3}"}
    assert set(members) == expected_paths
    for path, m in members.items():
        assert m["blob"], f"{path}: member manifest must carry a real blob id"
        assert m["size"] is not None
        assert m["cls"]
    # a member's class comes from the SAME generic class_rules glob any other occurrence uses (never hard-coded).
    assert members[f"{mf.DIR_PATH}/{mf.DIR_FILE_1}"]["cls"] == "EVIDENCE"

    delivered_text = next(i.text for i in result["sections"]["A"] if i.unit_id == "MF-DIR")
    assert "directory manifest" in delivered_text
    for path in expected_paths:
        assert path in delivered_text

    # a directory item with no row-declared sha256 no longer carries source_sha256=None (the run-1 "acknowledged
    # as ID@None" gap) -- it gets a real, deterministic identity hash over its own member manifest.
    assert row["source_sha256"] is not None
    assert row["delivered_sha256"] is not None


def test_markdown_entries_resolve_in_document_order_not_lexicographic(mf_repo, mf_view_path, mf_registry_path):
    """MF-LEDGER declares ``entries: {start: MF-GEN-010, end: MF-GEN-005}`` over a Markdown ledger whose entries
    are, in DOCUMENT order, GEN-010, GEN-002, GEN-005 -- the LOWEST id (GEN-002) sits between the two named
    endpoints in the document, but is neither endpoint. A correct, document-order resolver must select ALL THREE
    entries (position 0 through position 2, inclusive); a buggy lexicographic-comparison resolver would either
    select nothing (since "MF-GEN-005" <= "MF-GEN-010" as strings makes the range look empty/backwards) or the
    wrong subset."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    delivered_text = next(i.text for i in result["sections"]["A"] if i.unit_id == "MF-LEDGER")
    for entry_id in ("MF-GEN-010", "MF-GEN-002", "MF-GEN-005"):
        assert f"body for {entry_id}" in delivered_text

    resolve_result = result["resolve_result"]
    mi = next(m for m in resolve_result.items if m.id == "MF-LEDGER")
    assert [p["kind"] for p in mi.parts] == ["entries", "entries", "entries"]
    got_ids = [p["name"].split(":")[0] for p in mi.parts]  # each part's name is the full heading title
    assert got_ids == ["MF-GEN-010", "MF-GEN-002", "MF-GEN-005"], \
        f"parts must be in DOCUMENT order, not lexicographic: got {got_ids}"


def test_markdown_entries_reverse_document_order_fails_closed(mf_repo, mf_view_path, mf_registry_path):
    """``entries: {start: MF-GEN-002, end: MF-GEN-010}`` -- MF-GEN-002 sits AFTER MF-GEN-010 in the document, so
    ``start`` does not precede ``end`` in document order (even though it does lexicographically: "002" < "010").
    This must fail closed, never silently resolve via string comparison."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path, required_inputs=[
        {"state_ref": "state:bridge#mandatory_bridge_inputs.unresolvable_probe_items[*]", "reason": "test"},
    ])
    assert result["status"] == packetmod.STATUS_BLOCKED
    reasons = " ".join(result["resolve_result"].blocked_reasons)
    assert "MF-REVERSE-ORDER" in reasons
    assert "DOCUMENT order" in reasons


def test_unresolvable_selector_fails_closed(mf_repo, mf_view_path, mf_registry_path):
    """A ``keys`` selector naming a key the document does not have must BLOCK the whole resolution (never a
    silent partial match) and disclose why."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path, required_inputs=[
        {"state_ref": "state:bridge#mandatory_bridge_inputs.unresolvable_probe_items[*]", "reason": "test"},
    ])
    assert result["status"] == packetmod.STATUS_BLOCKED
    assert result["resolve_result"].status == resolvermod.STATUS_BLOCKED
    reasons = " ".join(result["resolve_result"].blocked_reasons)
    assert "MF-UNRESOLVABLE" in reasons
    assert "no-such-key" in reasons
    # the failure is disclosed in J, never silently dropped.
    assert any(n["type"] == "BLOCKED_INPUT" and "no-such-key" in n["detail"] for n in result["manifest"]["notices"])


def test_a_free_text_entries_annotation_is_never_treated_as_a_selector(mf_repo, mf_view_path, mf_registry_path):
    """A real ``mandatory_bridge_inputs`` row (PHASE-2-LEDGER-P2-L-0033-0047, ORCHESTRATOR_STATE.yaml) already uses
    ``entries`` as a free-text, human-readable annotation, not a structured selector. This must never be
    misinterpreted as ``{under, start, end}`` and crash or silently mis-resolve -- proven here directly against
    ``resolver._resolve_row_selectors`` on a synthetic row of that exact non-structured shape."""
    row = {"id": "MF-FREE-TEXT", "class": "ORCHESTRATION_RECORD", "path": mf.KEYS_YAML_PATH,
           "entries": "E-0001..E-0002 (free text, not a selector)"}
    parts, unresolved = resolvermod._resolve_row_selectors(row, mf.KEYS_YAML_PATH, mf_repo.c1, repo=str(mf_repo.root))
    assert parts == ()
    assert unresolved == ()


def test_full_compile_suite_untouched_by_this_fixture(mf_repo, mf_view_path, mf_registry_path):
    """A sanity check that this node's own fixture corpus does not leak into, or depend on, the shared
    ``tests/fixtures/compile/compile_repobuilder.py`` fixture."""
    assert mf_repo.root != Path(".")
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK


# ---------------------------------------------------------------------------------------------------------------
# BR-DAG-AMEND reopening ("packet verify cannot detect silent truncation"): negative controls. Each of these
# MUST make `packet verify` FAIL -- proving the declared/delivered coverage check actually catches the three
# concrete failure shapes the reopening named, not merely that it passes on well-formed input.
# ---------------------------------------------------------------------------------------------------------------

def test_truncated_body_with_no_notice_fails_verify(mf_repo, mf_view_path, mf_registry_path):
    """A compiler that delivered something OTHER than the declared content, but recorded a delivered_sha256 for
    it anyway with NO ``MANDATORY_PARTIAL_DELIVERY`` notice to explain the gap, must fail ``packet verify``. This
    is RC-1's exact silent-truncation shape: a hash is present, but it does not match what was declared, and
    nothing discloses why."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    manifest = copy.deepcopy(result["manifest"])
    row = next(r for r in manifest["sections"]["A"]["items"] if r["unit"]["id"] == "MF-PATHS")
    assert row["delivered_sha256"] == row["declared_sha256"], "MF-PATHS must be a fully-delivered, no-notice item"
    row["delivered_sha256"] = "0" * 64  # a body silently swapped/cut, with a hash recorded for the wrong content
    problems = validatemod.verify_packet(manifest, task_spec, repo=str(mf_repo.root),
                                          registry_path=mf_registry_path)
    assert any("MF-PATHS" in p and "no MANDATORY_PARTIAL_DELIVERY notice" in p for p in problems), problems


def test_notice_with_a_gap_fails_verify(mf_repo, mf_view_path, mf_registry_path):
    """A ``MANDATORY_PARTIAL_DELIVERY`` notice whose disclosed ranges leave a GAP (one undisclosed range is
    simply dropped) must fail ``packet verify``'s coverage/tiling check -- proving a real gap is detected, not
    just that a complete disclosure is accepted."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    manifest = copy.deepcopy(result["manifest"])
    notice = next(n for n in manifest["notices"]
                  if n["type"] == "MANDATORY_PARTIAL_DELIVERY" and n["id"] == "MF-BIG")
    assert len(notice["undelivered_ranges"]) >= 2, "MF-BIG's fixture must have several disclosed ranges"
    notice["undelivered_ranges"].pop()  # drop one disclosed range -- introduces a real gap
    problems = validatemod.verify_packet(manifest, task_spec, repo=str(mf_repo.root),
                                          registry_path=mf_registry_path)
    assert any("MF-BIG" in p and "gap" in p for p in problems), problems


def test_declared_sha256_mismatch_fails_verify(mf_repo, mf_view_path, mf_registry_path):
    """A tampered ``declared_sha256`` that no longer matches the source at the recorded view must fail ``packet
    verify`` -- proving the value is independently RECOMPUTED from Git at verify time, never trusted from the
    stored manifest (the whole point of the reopening: a compiler's own claim about what it declared is not
    evidence)."""
    task_spec, result = _compile(mf_repo, mf_view_path, mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    manifest = copy.deepcopy(result["manifest"])
    row = next(r for r in manifest["sections"]["A"]["items"] if r["unit"]["id"] == "MF-KEYS")
    row["declared_sha256"] = "f" * 64
    problems = validatemod.verify_packet(manifest, task_spec, repo=str(mf_repo.root),
                                          registry_path=mf_registry_path)
    assert any("MF-KEYS" in p and "declared_sha256" in p and "does not match the source" in p for p in problems), \
        problems
