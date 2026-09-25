"""``govbridge receipt check`` (ARCHITECTURE.md section 7.4): pass/fail fixtures. A well-formed receipt built from
the packet's OWN manifest passes; a receipt with the wrong packet hash, a wrong read token, a missing section-A
acknowledgement, or a dangling ``items_relied_on`` id each fails, naming the specific problem.
"""
from govbridge.compile import packet as packetmod
from govbridge.compile import receipt as receiptmod
from govbridge.route.router import RouteSet


def _compile(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    return task_spec, result


def _valid_receipt(manifest: dict) -> dict:
    import hashlib
    m_sha = manifest["manifest_sha256"]
    read_tokens = {letter: hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12]
                   for letter in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")}
    inputs_consumed = [f"{r['unit']['id']}@{r['content_sha256']}" for r in manifest["sections"]["A"]["items"]]
    return {
        "context_packet_hash": manifest["packet_sha256"],
        "manifest_sha256": manifest["manifest_sha256"],
        "read_tokens": read_tokens,
        "inputs_consumed": inputs_consumed,
        "items_relied_on": [manifest["sections"]["A"]["items"][0]["item_id"]] if manifest["sections"]["A"]["items"] else [],
        "external_reads": [],
        "outputs_produced": [],
        "decisions_applied": [],
        "acceptance_evidence": [],
        "deviations": [],
        "unresolved": [],
    }


def test_receipt_check_passes_for_a_well_formed_receipt(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = result["manifest"]
    receipt = _valid_receipt(manifest)
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["status"] == "PASS", out["problems"]


def test_receipt_check_fails_on_wrong_packet_hash(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = result["manifest"]
    receipt = _valid_receipt(manifest)
    receipt["context_packet_hash"] = "0" * 64
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["status"] == "FAIL"
    assert any("context_packet_hash" in p for p in out["problems"])


def test_receipt_check_fails_on_wrong_read_token(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = result["manifest"]
    receipt = _valid_receipt(manifest)
    receipt["read_tokens"]["A"] = "deadbeefcafe"
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["status"] == "FAIL"
    assert any("read_tokens" in p for p in out["problems"])


def test_receipt_check_fails_on_missing_a_acknowledgement(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = result["manifest"]
    receipt = _valid_receipt(manifest)
    receipt["inputs_consumed"] = []
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["status"] == "FAIL"
    assert any("not acknowledged in inputs_consumed" in p for p in out["problems"])


def test_receipt_check_fails_on_dangling_item_id(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = result["manifest"]
    receipt = _valid_receipt(manifest)
    receipt["items_relied_on"] = ["no-such-item-id"]
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["status"] == "FAIL"
    assert any("unknown item_id" in p for p in out["problems"])


def test_receipt_check_reports_external_read_bytes(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = result["manifest"]
    receipt = _valid_receipt(manifest)
    receipt["external_reads"] = [{"path": "spec/decisions/CX-0002.yaml", "commit": fixture_repo.c2,
                                   "lines": [1, 3], "why": "checked the replacement decision"}]
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["status"] == "PASS", out["problems"]
    assert out["external_read_files"] == 1
    assert out["external_read_bytes"] > 0


def test_receipt_check_fails_on_external_read_that_does_not_resolve(fixture_repo, view_path, registry_path,
                                                                       task_spec_factory):
    task_spec, result = _compile(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = result["manifest"]
    receipt = _valid_receipt(manifest)
    receipt["external_reads"] = [{"path": "no/such/path.yaml", "commit": fixture_repo.c2, "lines": [1, 1],
                                   "why": "nonexistent"}]
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["status"] == "FAIL"
    assert any("does not resolve to a real blob" in p for p in out["problems"])
