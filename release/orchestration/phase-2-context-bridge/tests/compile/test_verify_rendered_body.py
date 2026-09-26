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
