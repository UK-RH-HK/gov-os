"""BR-DAG-AMEND-R1-1 regression: ``packet verify`` (and, transitively, ``receipt check``, which calls into the
SAME ``validate.verify_packet``) must re-derive section A at the VIEW RECORDED IN THE PACKET'S OWN MANIFEST
(pinned refs/commits), never at the repository's moving tip -- so a stored packet stays re-verifiable at any
LATER time (ARCHITECTURE.md section 5.3 rule 4), even after a new mandatory record has since been committed to the
same ref. This is the exact failure the R1-RG quarantined check hit: "packet verify re-derives section A at the
CURRENT tip: 24 expected vs 20 -- OD-BR-03..06 became mandatory after run-1".

The fixture (``tests/fixtures/compile/recorded_view/repobuilder.py``) is this regression's own, independent of the
shared ``tests/fixtures/compile/compile_repobuilder.py`` -- its whole point (a SECOND commit landing on the
``records`` branch after a packet has already been compiled) has no counterpart there. Every id is ``RV-*``
(Recorded View), unrelated to Review-8/Phase-2 (OC-BR-02).
"""
from govbridge.compile import packet as packetmod
from govbridge.compile import receipt as receiptmod
from govbridge.compile import validate as validatemod
from govbridge.route.router import FAKE_ROUTES

from recorded_view import repobuilder as rv  # tests/fixtures/compile/recorded_view/repobuilder.py (namespace
                                              # package, reached via conftest.py's sys.path insert)


def _valid_receipt(manifest: dict) -> dict:
    import hashlib
    m_sha = manifest["manifest_sha256"]
    read_tokens = {letter: hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12]
                   for letter in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")}
    inputs_consumed = [f"{r['unit']['id']}@{r['content_sha256']}" for r in manifest["sections"]["A"]["items"]]
    return {
        "context_packet_hash": manifest["packet_sha256"], "manifest_sha256": manifest["manifest_sha256"],
        "read_tokens": read_tokens, "inputs_consumed": inputs_consumed,
        "items_relied_on": [manifest["sections"]["A"]["items"][0]["item_id"]],
        "external_reads": [], "outputs_produced": [], "decisions_applied": [], "acceptance_evidence": [],
        "deviations": [], "unresolved": [],
    }


def test_packet_verify_passes_after_a_new_mandatory_record_is_committed(tmp_path):
    repo = rv.build(tmp_path / "repo")
    view_path = str(tmp_path / "canonical-view.yaml")
    rv.write_canonical_view(tmp_path / "canonical-view.yaml", repo)
    registry_path = str(tmp_path / "authority-registry.yaml")
    rv.write_registry(tmp_path / "authority-registry.yaml")

    task_spec = rv.make_task_spec(view_path)
    result = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=str(repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    manifest = result["manifest"]
    a_ids_before = {r["unit"]["id"] for r in manifest["sections"]["A"]["items"]}
    assert a_ids_before == {"RV-0001"}, "the packet must be compiled BEFORE RV-0002 exists"

    # the packet is valid right after compilation...
    assert validatemod.verify_packet(manifest, task_spec, repo=str(repo.root), registry_path=registry_path) == []

    # ...now advance the SAME `records` branch with a brand-new mandatory owner record. A live re-resolve of the
    # view would see ONE MORE item (RV-0002) than the stored packet recorded.
    rv.add_new_mandatory_record(repo)

    problems = validatemod.verify_packet(manifest, task_spec, repo=str(repo.root), registry_path=registry_path)
    assert problems == [], f"packet verify must PASS at the packet's OWN recorded view: {problems}"

    # receipt check calls into the SAME validator -- the fix is not duplicated, so this passes too.
    receipt = _valid_receipt(manifest)
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(repo.root), registry_path=registry_path)
    assert out["status"] == "PASS", out["problems"]


def test_a_live_re_resolve_would_have_seen_the_new_record(tmp_path):
    """A control on the regression above: proves the fixture's new commit really DOES change what a fresh,
    UN-pinned resolve sees -- so "packet verify still passes" above is a real fix, not a fixture that never
    exercised the bug in the first place."""
    repo = rv.build(tmp_path / "repo")
    view_path = str(tmp_path / "canonical-view.yaml")
    rv.write_canonical_view(tmp_path / "canonical-view.yaml", repo)
    registry_path = str(tmp_path / "authority-registry.yaml")
    rv.write_registry(tmp_path / "authority-registry.yaml")

    from govbridge.authority import resolver as resolvermod

    task_spec = rv.make_task_spec(view_path)
    before = resolvermod.resolve(task_spec, repo=str(repo.root), registry_path=registry_path)
    assert {i.id for i in before.items} == {"RV-0001"}

    rv.add_new_mandatory_record(repo)

    after = resolvermod.resolve(task_spec, repo=str(repo.root), registry_path=registry_path)
    assert {i.id for i in after.items} == {"RV-0001", "RV-0002"}, \
        "a live (un-pinned) resolve after the new commit must see the new record -- proving the fixture is a " \
        "genuine moving-tip scenario"


def test_verify_section_a_fails_without_the_pinned_view_fix(tmp_path):
    """A direct negative control: if ``verify_section_a`` recomputed at the LIVE view (the pre-repair behaviour)
    instead of the packet's own recorded view, it would fail here -- proven by calling the OLD code path directly
    (``recompute_section_a`` with no ``resolved_view`` override, exactly what R1-RG's quarantined check hit)."""
    repo = rv.build(tmp_path / "repo")
    view_path = str(tmp_path / "canonical-view.yaml")
    rv.write_canonical_view(tmp_path / "canonical-view.yaml", repo)
    registry_path = str(tmp_path / "authority-registry.yaml")
    rv.write_registry(tmp_path / "authority-registry.yaml")

    task_spec = rv.make_task_spec(view_path)
    result = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=str(repo.root),
                                       registry_path=registry_path)
    manifest = result["manifest"]
    rv.add_new_mandatory_record(repo)

    expected_live, _ = validatemod.recompute_section_a(task_spec, repo=str(repo.root), registry_path=registry_path)
    actual = validatemod._manifest_a_tuples(manifest)
    assert expected_live != actual, \
        "a LIVE (un-pinned) re-derivation must disagree with the stored packet once a new record lands -- this is " \
        "the failure BR-DAG-AMEND-R1-1 moved verify_section_a away from"
