"""The canonical worker bootstrap (ARCHITECTURE.md section 7.5): the ADAPT keeps the conventions blocks and the
checkpoint protocol verbatim, but ``phase_state()``'s hard-coded text becomes a structured, provenanced state
lookup and the fixed ``DECISIONS`` dict becomes the compiled packet's own section A -- so nothing in the output is a
literal, hard-coded value from the ADAPT source.
"""
from govbridge.compile import bootstrap as bootstrapmod
from govbridge.compile import packet as packetmod
from govbridge.route.router import RouteSet


def test_bootstrap_contains_prelude_packet_and_receipt_instructions(fixture_repo, view_path, registry_path,
                                                                       task_spec_factory):
    task_spec = task_spec_factory(view_path, seeds=["CX-0001"])
    brief, result = bootstrapmod.compile_brief(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                                 registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK

    assert "## Where you are" in brief
    assert "## How this repository works" in brief
    assert "## Your context packet (sections A-J)" in brief
    assert "## Context and checkpoint protocol" in brief
    assert "## Completion semantics" in brief
    assert "## Your receipt" in brief
    assert result["packet_sha256"] in brief

    # the packet itself (A-J) is embedded, not summarised away.
    assert "## A. MANDATORY AUTHORITATIVE INPUTS" in brief
    assert "## J. COMPLETION / EVIDENCE OBLIGATIONS" in brief


def test_bootstrap_where_you_are_carries_provenance_not_hardcoded_text(fixture_repo, view_path, registry_path,
                                                                          task_spec_factory):
    where = bootstrapmod.where_you_are(view_path=view_path, repo=str(fixture_repo.root))
    assert "lifecycle_id" in where
    assert "CX-FIXTURE" in where  # this fixture's OWN state value, never a literal from the ADAPT source
    assert "source:" in where and "seal" in where


def test_bootstrap_never_contains_the_adapt_sources_hardcoded_literals(fixture_repo, view_path, registry_path,
                                                                          task_spec_factory):
    """The regression the ADAPT was built to fix: the ORIGINAL worker_bootstrap.py's ``phase_state()`` baked in
    literal Phase-2 strings. This bridge's bootstrap reads ITS OWN state generically and can never reproduce them."""
    task_spec = task_spec_factory(view_path, seeds=["CX-0001"])
    brief, _ = bootstrapmod.compile_brief(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                            registry_path=registry_path)
    assert "cap2-candidate-1" not in brief
    assert "GATE-P2-REPAIR-2" not in brief


def test_bootstrap_completion_semantics_reflect_task_spec_vocabulary(fixture_repo, view_path, registry_path,
                                                                        task_spec_factory):
    task_spec = task_spec_factory(view_path)
    task_spec["completion_vocabulary"] = ["REPAIRED_CLAIMED", "OWNER_DECISION_REQUIRED"]
    brief, _ = bootstrapmod.compile_brief(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                            registry_path=registry_path)
    assert "`REPAIRED_CLAIMED`" in brief
    assert "`OWNER_DECISION_REQUIRED`" in brief
    assert "never accepted or verified by you" in brief
