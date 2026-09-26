"""BR-DAG-AMEND-R1-10 (routed from BR-AR-0022's open issue): ``packet verify``/``receipt check`` must re-extract
each section-A item's DELIVERED BODY from the RENDERED packet (never trust the manifest's own ``delivered_sha256``
alone) and independently recompute its hash, so a renderer that drops or mangles content AFTER the compiler
already hashed it correctly is caught. This is the negative test the amendment names explicitly: "tamper the
rendered body and leave the manifest intact; verify must FAIL."
"""
from __future__ import annotations

import json

from govbridge.compile import packet as packetmod
from govbridge.compile import render as rendermod
from govbridge.compile import validate as validatemod
from govbridge.route.router import RouteSet


def _compile(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    assert result["manifest"]["sections"]["A"]["items"], "the fixture task spec must have a real mandatory item"
    return task_spec, result


def _tamper_a_item_body(rendered: str, unit_kind: str, unit_id: str) -> str:
    """Replaces the exact bytes between this item's own body-begin/body-end markers with unrelated content,
    leaving every marker, every metadata line and every OTHER item's body untouched -- the tampering is confined
    to precisely what ``extract_item_delivered_body`` would extract."""
    begin = rendermod.item_body_marker(unit_kind, unit_id, "body-begin")
    end = rendermod.item_body_marker(unit_kind, unit_id, "body-end")
    b_start = rendered.index(begin) + len(begin)
    e_pos = rendered.index(end, b_start)
    return rendered[:b_start] + "\nTAMPERED: this replaces the real delivered body\n" + rendered[e_pos:]


# ---------------------------------------------------------------------------------------------------------------
# The positive control: an honest packet passes with `rendered` supplied.
# ---------------------------------------------------------------------------------------------------------------

def test_verify_packet_passes_with_rendered_when_untampered(fixture_repo, view_path, registry_path,
                                                               task_spec_factory):
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    problems = validatemod.verify_packet(result["manifest"], task_spec, repo=str(fixture_repo.root),
                                          registry_path=registry_path, rendered=result["rendered"])
    assert problems == []


# ---------------------------------------------------------------------------------------------------------------
# The amendment's own negative test: tamper the RENDERED body, leave manifest.json untouched -> FAIL.
# ---------------------------------------------------------------------------------------------------------------

def test_verify_packet_fails_when_rendered_body_tampered_manifest_intact(fixture_repo, view_path, registry_path,
                                                                           task_spec_factory):
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    a_row = result["manifest"]["sections"]["A"]["items"][0]
    unit_kind, unit_id = a_row["unit"]["kind"], a_row["unit"]["id"]

    tampered_rendered = _tamper_a_item_body(result["rendered"], unit_kind, unit_id)
    assert tampered_rendered != result["rendered"]

    # the manifest -- the thing a compiler-hash-only check would trust -- is passed UNCHANGED.
    manifest_before = json.dumps(result["manifest"], sort_keys=True)
    problems = validatemod.verify_packet(result["manifest"], task_spec, repo=str(fixture_repo.root),
                                          registry_path=registry_path, rendered=tampered_rendered)
    assert json.dumps(result["manifest"], sort_keys=True) == manifest_before, "verify must never mutate the manifest"

    assert problems, "a tampered rendered body (manifest intact) must fail packet verify"
    assert any(unit_id in p and "A/" in p for p in problems), problems


def test_verify_packet_without_rendered_does_not_see_the_tamper(fixture_repo, view_path, registry_path,
                                                                   task_spec_factory):
    """Documents WHY the amendment exists: the pre-existing manifest-only checks alone (``rendered=None``) cannot
    see a renderer bug -- only passing the actual rendered bytes closes the gap."""
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    problems = validatemod.verify_packet(result["manifest"], task_spec, repo=str(fixture_repo.root),
                                          registry_path=registry_path, rendered=None)
    assert problems == []


# ---------------------------------------------------------------------------------------------------------------
# The same guarantee through `govbridge receipt check`.
# ---------------------------------------------------------------------------------------------------------------

def test_receipt_check_fails_when_rendered_body_tampered(fixture_repo, view_path, registry_path,
                                                            task_spec_factory):
    from govbridge.compile import receipt as receiptmod
    import hashlib

    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = result["manifest"]
    a_row = manifest["sections"]["A"]["items"][0]

    m_sha = manifest["manifest_sha256"]
    read_tokens = {letter: hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12]
                   for letter in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")}
    receipt = {
        "context_packet_hash": manifest["packet_sha256"], "manifest_sha256": manifest["manifest_sha256"],
        "read_tokens": read_tokens,
        "inputs_consumed": [f"{r['unit']['id']}@{r['content_sha256']}" for r in manifest["sections"]["A"]["items"]],
        "items_relied_on": [], "external_reads": [], "outputs_produced": [], "decisions_applied": [],
        "acceptance_evidence": [], "deviations": [], "unresolved": [],
    }

    tampered_rendered = _tamper_a_item_body(result["rendered"], a_row["unit"]["kind"], a_row["unit"]["id"])
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path,
                            rendered=tampered_rendered)
    assert out["status"] == "FAIL"
    assert any("packet verify" in p for p in out["problems"]), out["problems"]


# ---------------------------------------------------------------------------------------------------------------
# End to end through the CLI: `govbridge packet verify DIR` on a packet whose packet.md was tampered on disk.
# ---------------------------------------------------------------------------------------------------------------

def test_cli_packet_verify_fails_when_packet_md_tampered_on_disk(fixture_repo, view_path, registry_path,
                                                                    task_spec_factory, tmp_path, monkeypatch):
    from govbridge import cli
    import yaml

    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK

    out_dir = tmp_path / "pkt"
    out_dir.mkdir()
    (out_dir / "packet.md").write_text(result["rendered"], encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(result["manifest"], indent=1, sort_keys=True),
                                            encoding="utf-8")
    (out_dir / "task_spec.yaml").write_text(yaml.safe_dump(task_spec, sort_keys=False), encoding="utf-8")
    (out_dir / "meta.json").write_text(json.dumps({"packet_kind": "main", "status": "OK",
                                                    "registry_path": registry_path}, indent=1), encoding="utf-8")

    # sanity: untampered, it verifies clean through the real CLI path first.
    rc_clean = cli.main(["packet", "verify", str(out_dir), "--repo", str(fixture_repo.root)])
    assert rc_clean == 0

    a_row = result["manifest"]["sections"]["A"]["items"][0]
    tampered = _tamper_a_item_body(result["rendered"], a_row["unit"]["kind"], a_row["unit"]["id"])
    (out_dir / "packet.md").write_text(tampered, encoding="utf-8")
    # manifest.json is left untouched on disk.

    rc_tampered = cli.main(["packet", "verify", str(out_dir), "--repo", str(fixture_repo.root)])
    assert rc_tampered != 0


# ---------------------------------------------------------------------------------------------------------------
# render.py's own extraction primitives, directly.
# ---------------------------------------------------------------------------------------------------------------

def test_extract_item_delivered_body_roundtrips_the_exact_text():
    body_text = "line one\nline two"
    rendered = (
        "## A. MANDATORY AUTHORITATIVE INPUTS\n\n"
        "- unit: record:X-1  (delivery=MANDATORY, route=resolver, class=OWNER_DECISION, lifecycle=ACTIVE)\n"
        f"{rendermod.item_body_marker('record', 'X-1', 'body-begin')}\n"
        f"{body_text}\n"
        f"{rendermod.item_body_marker('record', 'X-1', 'body-end')}\n"
        "read_token: abc123\n\n"
        "## B. SYSTEM PURPOSE / WHY\n\n(none)\nread_token: def456\n"
    )
    found, body, ambiguous = rendermod.extract_item_delivered_body(rendered, "A", "record", "X-1")
    assert found is True
    assert ambiguous is False
    assert body == body_text


def test_extract_item_delivered_body_not_found_for_unknown_unit():
    rendered = "## A. MANDATORY AUTHORITATIVE INPUTS\n\n(none)\nread_token: abc\n"
    found, body, ambiguous = rendermod.extract_item_delivered_body(rendered, "A", "record", "NO-SUCH-ID")
    assert found is False
    assert ambiguous is False


def test_extract_item_delivered_body_ambiguous_when_duplicated():
    begin = rendermod.item_body_marker("record", "X-1", "body-begin")
    end = rendermod.item_body_marker("record", "X-1", "body-end")
    rendered = (
        f"## A. MANDATORY AUTHORITATIVE INPUTS\n\n{begin}\nfirst\n{end}\n\n{begin}\nsecond\n{end}\n"
        "read_token: abc\n"
    )
    found, body, ambiguous = rendermod.extract_item_delivered_body(rendered, "A", "record", "X-1")
    assert found is True
    assert ambiguous is True
    assert body is None


def test_extract_section_text_isolates_one_section():
    rendered = "## A. TITLE\n\nAAA\nread_token: t1\n\n## B. TITLE\n\nBBB\nread_token: t2\n"
    a_text = rendermod.extract_section_text(rendered, "A")
    assert "AAA" in a_text
    assert "BBB" not in a_text
    b_text = rendermod.extract_section_text(rendered, "B")
    assert "BBB" in b_text
    assert "AAA" not in b_text


# ---------------------------------------------------------------------------------------------------------------
# BR-AR-0025 reopening: R1-10 must be EXACT for EVERY A-item shape, not a hash-of-the-whole-body-or-containment
# reading that a selector item's own headers happen to need. ``govbridge.compile.packet``'s own R1-RM fixture
# (``tests/fixtures/compile/mandatory/repobuilder.py``, imported read-only exactly as
# ``tests/compile/test_mandatory_fidelity.py`` already does) gives every real shape ``Compiler._mandatory_text``
# produces: MF-BIG (oversize, no selector), MF-ENTRIES/MF-LEDGER (a Markdown/YAML ``entries`` selector),
# MF-KEYS (a ``keys`` selector), MF-PATHS (a ``paths``-only selector, no notice), MF-DIR (a directory manifest).
# ---------------------------------------------------------------------------------------------------------------

from mandatory import repobuilder as mf  # noqa: E402  (tests/fixtures/compile/mandatory/repobuilder.py; reached
                                          # via tests/compile/conftest.py's own sys.path insert of
                                          # tests/fixtures/compile -- never imported by, or duplicated from,
                                          # test_mandatory_fidelity.py, which is R1-RM's file, not this node's)


import pytest  # noqa: E402


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


def _mf_compile(mf_repo, mf_view_path, mf_registry_path):
    task_spec = mf.make_task_spec(mf_view_path)
    result = packetmod.compile_packet(task_spec, routes=packetmod.FAKE_ROUTES, repo=str(mf_repo.root),
                                       registry_path=mf_registry_path)
    assert result["status"] == packetmod.STATUS_OK
    return task_spec, result


def _extract_body_span(rendered: str, unit_id: str) -> tuple:
    """``(body, body_start, body_end)`` -- the exact span ``extract_item_delivered_body`` would return, plus its
    absolute offsets in ``rendered``, so a test can splice a tamper INTO that exact span (never touching a
    marker, another item's body, or anything outside section A)."""
    begin = rendermod.item_body_marker("record", unit_id, "body-begin")
    end = rendermod.item_body_marker("record", unit_id, "body-end")
    b_start = rendered.index(begin) + len(begin) + 1  # +1: the single "\n" _render_item_body's own join adds
    e_pos = rendered.index(end, b_start) - 1           # -1: the matching "\n" before the end marker
    return rendered[b_start:e_pos], b_start, e_pos


def test_verify_passes_exactly_for_every_real_mandatory_fidelity_shape(mf_repo, mf_view_path, mf_registry_path):
    """The positive control for this reopening: one compile carries all six MF-* shapes in section A at once, and
    every one of them must independently recompose EXACTLY from the rendered packet -- not just the shapes
    test_verify_rendered_body.py's other tests already covered via the default (single-piece) fixture."""
    task_spec, result = _mf_compile(mf_repo, mf_view_path, mf_registry_path)
    a_ids = {r["unit"]["id"] for r in result["manifest"]["sections"]["A"]["items"]}
    assert a_ids >= {"MF-BIG", "MF-ENTRIES", "MF-KEYS", "MF-PATHS", "MF-DIR", "MF-LEDGER"}
    problems = validatemod.verify_packet(result["manifest"], task_spec, repo=str(mf_repo.root),
                                          registry_path=mf_registry_path, rendered=result["rendered"])
    assert problems == []


def test_verify_fails_on_text_inserted_between_two_pieces_of_a_selector_item(mf_repo, mf_view_path,
                                                                               mf_registry_path):
    """Negative test 1 (BR-AR-0025 reopening): text inserted BETWEEN two pieces of a selector item (MF-ENTRIES,
    a Markdown ``entries`` selector delivering 4 pieces) must fail verify. A CONTAINMENT check (every piece's own
    text still present) would have PASSED this -- only an exact whole-body comparison catches it."""
    task_spec, result = _mf_compile(mf_repo, mf_view_path, mf_registry_path)
    manifest_before = json.dumps(result["manifest"], sort_keys=True)

    body, b_start, e_pos = _extract_body_span(result["rendered"], "MF-ENTRIES")
    piece_header_positions = [i for i in range(len(body)) if body.startswith("--- ", i)]
    assert len(piece_header_positions) >= 2, "MF-ENTRIES must declare at least 2 pieces for this probe"
    insert_at = piece_header_positions[1]  # strictly between the end of piece 1's text and piece 2's own header
    tampered_body = body[:insert_at] + "INSERTED-BETWEEN-PIECES\n" + body[insert_at:]
    tampered_rendered = result["rendered"][:b_start] + tampered_body + result["rendered"][e_pos:]

    problems = validatemod.verify_packet(result["manifest"], task_spec, repo=str(mf_repo.root),
                                          registry_path=mf_registry_path, rendered=tampered_rendered)
    assert json.dumps(result["manifest"], sort_keys=True) == manifest_before
    assert any("MF-ENTRIES" in p for p in problems), problems


def test_verify_fails_on_a_changed_line_inside_one_of_a_selector_items_delivered_pieces(mf_repo, mf_view_path,
                                                                                          mf_registry_path):
    """A mutation (never an insertion) INSIDE one of MF-ENTRIES's own delivered piece texts must also fail --
    the exact-body comparison catches a changed line inside a genuinely delivered section, not merely a gap
    between sections."""
    task_spec, result = _mf_compile(mf_repo, mf_view_path, mf_registry_path)
    body, b_start, e_pos = _extract_body_span(result["rendered"], "MF-ENTRIES")
    needle = "entry number 4, generated fixture content"
    assert needle in body
    tampered_body = body.replace(needle, "MUTATED " + needle)
    assert tampered_body != body
    tampered_rendered = result["rendered"][:b_start] + tampered_body + result["rendered"][e_pos:]

    problems = validatemod.verify_packet(result["manifest"], task_spec, repo=str(mf_repo.root),
                                          registry_path=mf_registry_path, rendered=tampered_rendered)
    assert any("MF-ENTRIES" in p for p in problems), problems


def test_verify_fails_on_a_changed_line_inside_an_oversize_items_section_map(mf_repo, mf_view_path,
                                                                               mf_registry_path):
    """Negative test 2 (BR-AR-0025 reopening): a changed line inside MF-BIG's own section map (no selector, over
    the per-item cap -- Contract v3's own real shape) must fail verify. Independently confirmed on the REAL
    CONTROL-A packet too (AGENT_RUNS/BR-AR-0025.check4...out, a shell/sed-level probe outside this test)."""
    import re

    task_spec, result = _mf_compile(mf_repo, mf_view_path, mf_registry_path)
    body, b_start, e_pos = _extract_body_span(result["rendered"], "MF-BIG")
    m = re.search(r"sha256=([0-9a-f]+)", body)
    assert m, "MF-BIG's rendered body must disclose at least one section-map sha256 line"
    pos = m.start(1)
    flipped = "1" if body[pos] == "0" else "0"
    tampered_body = body[:pos] + flipped + body[pos + 1:]
    tampered_rendered = result["rendered"][:b_start] + tampered_body + result["rendered"][e_pos:]

    problems = validatemod.verify_packet(result["manifest"], task_spec, repo=str(mf_repo.root),
                                          registry_path=mf_registry_path, rendered=tampered_rendered)
    assert any("MF-BIG" in p for p in problems), problems


def test_verify_fails_on_an_extra_member_line_in_a_directory_manifest(mf_repo, mf_view_path, mf_registry_path):
    """Negative test 4 (BR-AR-0025 reopening): an extra member line appended to MF-DIR's own directory manifest
    must fail verify -- a renderer (or an attacker) adding an undeclared member is exactly the kind of insertion
    into A the hard authority invariant forbids, and a directory item was previously SKIPPED by this check
    entirely."""
    task_spec, result = _mf_compile(mf_repo, mf_view_path, mf_registry_path)
    body, b_start, e_pos = _extract_body_span(result["rendered"], "MF-DIR")
    tampered_body = body + "\n- fake/injected/member.txt  (blob=deadbeefcafe, size=1, class=EVIDENCE)"
    tampered_rendered = result["rendered"][:b_start] + tampered_body + result["rendered"][e_pos:]

    problems = validatemod.verify_packet(result["manifest"], task_spec, repo=str(mf_repo.root),
                                          registry_path=mf_registry_path, rendered=tampered_rendered)
    assert any("MF-DIR" in p for p in problems), problems
