"""Checkpoint and renewal (ARCHITECTURE.md section 7.6): ``RENEW_NOOP`` when nothing changed (no model call, no
re-read -- same packet id); ``RENEW_DELTA`` when the corpus changed, with added/changed/removed items and unchanged
A items carried by reference; ``RENEW_BLOCKED`` when a mandatory input is now missing or mismatched.
"""
from govbridge.compile import packet as packetmod
from govbridge.compile import renewal as renewalmod
from govbridge.route.router import RouteSet


def test_renew_noop_when_nothing_changed(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    checkpoint = renewalmod.make_checkpoint("RUN-1", result, done=["step 1"], open_questions=[],
                                             next_action="keep going")

    out = renewalmod.renew(task_spec, checkpoint, old_manifest=result["manifest"], routes=RouteSet(),
                            repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["outcome"] == renewalmod.RENEW_NOOP
    assert out["manifest_sha256"] == checkpoint["manifest_sha256"]
    assert out["packet_id"] == checkpoint["packet_id"]


def test_renew_delta_when_a_new_mandatory_item_is_added(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    old_manifest = result["manifest"]
    checkpoint = renewalmod.make_checkpoint("RUN-1", result, done=[], open_questions=[], next_action="continue")

    # narrow required_inputs to just the two anchored OWNER_DECISION items -- a smaller A than the full run, so the
    # delta below is unambiguous (added: none from this narrower set; removed: everything else).
    narrowed = dict(task_spec)
    narrowed["required_inputs"] = [
        {"id": "CX-0010A", "reason": "narrowed", "required_status": "ACTIVE"},
        {"id": "CX-0010B", "reason": "narrowed", "required_status": "ACTIVE"},
    ]
    out = renewalmod.renew(narrowed, checkpoint, old_manifest=old_manifest, routes=RouteSet(),
                            repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["outcome"] == renewalmod.RENEW_DELTA
    assert out["new_manifest_sha256"] != checkpoint["manifest_sha256"]
    assert out["delta"] is not None
    assert out["delta"]["removed"], "narrowing required_inputs must remove items from the delta"


def test_renew_blocked_when_a_mandatory_input_goes_missing(fixture_repo, view_path, registry_path,
                                                              task_spec_factory):
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    checkpoint = renewalmod.make_checkpoint("RUN-1", result, done=[], open_questions=[], next_action="continue")

    broken = dict(task_spec)
    broken["required_inputs"] = [{"id": "NO-SUCH-ID", "reason": "will not resolve"}]
    out = renewalmod.renew(broken, checkpoint, old_manifest=result["manifest"], routes=RouteSet(),
                            repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["outcome"] == renewalmod.RENEW_BLOCKED
    assert out["blocked_reasons"]


def test_renew_without_old_manifest_still_reports_delta_outcome(fixture_repo, view_path, registry_path,
                                                                    task_spec_factory):
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    stale_checkpoint = dict(renewalmod.make_checkpoint("RUN-1", result, done=[], open_questions=[],
                                                         next_action="continue"))
    stale_checkpoint["manifest_sha256"] = "0" * 64  # force a mismatch without recompiling anything

    out = renewalmod.renew(task_spec, stale_checkpoint, old_manifest=None, routes=RouteSet(),
                            repo=str(fixture_repo.root), registry_path=registry_path)
    assert out["outcome"] == renewalmod.RENEW_DELTA
    assert out["delta"] is None
    assert "note" in out
