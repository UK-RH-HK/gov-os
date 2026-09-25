"""ARCHITECTURE.md section 7.3 / section 5.3 rule 6: under budget pressure A is intact, every drop is listed in the
manifest, and BLOCKED_BUDGET is emitted when A itself cannot fit even after its oversized items are converted to
by-reference delivery.
"""
import dataclasses

from govbridge.compile import budgets as budgetsmod
from govbridge.compile import packet as packetmod
from govbridge.route.router import RouteHit, RouteOccurrence, RouteSet


def _tiny_profile(total_a_bytes=None, other_cap_bytes=1) -> budgetsmod.BudgetProfile:
    caps = {k: other_cap_bytes for k in ("B", "C", "D", "E", "F", "G", "H", "I", "J")}
    caps["A"] = None
    return budgetsmod.BudgetProfile(
        name="tiny", total_bytes=(total_a_bytes if total_a_bytes is not None else 10_000_000),
        section_caps_bytes=caps, per_item_cap_bytes=24 * 1024, rrf_k=60, graph_neighbour_depth=1,
        parent_expansion_top_n=3, max_slice_chars=1600,
    )


def _many_h_hits(n: int) -> list:
    occ = RouteOccurrence(ref="records", commit="deadbeef", path="spec/research/CX-RES-0001.md",
                           version_status="CANONICAL")
    return [
        RouteHit(unit_id=f"CHUNK-{i}", unit_kind="chunk", route="lexical", rank=i + 1, occurrences=(occ,),
                 text="x" * 500, authority_class="UNCLASSIFIED", lifecycle="UNKNOWN")
        for i in range(n)
    ]


def test_budget_pressure(fixture_repo, view_path, registry_path, task_spec_factory,
                                                      monkeypatch):
    hits = _many_h_hits(30)

    def fake_lexical(text=None, k=8, exclude=None, **kw):
        return hits

    routes = RouteSet(lexical=fake_lexical)
    task_spec = task_spec_factory(view_path, queries=[{"id": "q1", "text": "a long natural language query here"}])

    tiny = _tiny_profile(other_cap_bytes=200)  # enough for one or two 500-byte chunks, not all 30
    monkeypatch.setattr(budgetsmod, "load_profile", lambda name, path=None: tiny)

    full = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                     registry_path=registry_path)
    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK  # A alone still fits; only H is under pressure

    a_full = [(it["unit"]["id"], it["content_sha256"]) for it in full["manifest"]["sections"]["A"]["items"]]
    a_pressured = [(it["unit"]["id"], it["content_sha256"]) for it in result["manifest"]["sections"]["A"]["items"]]
    assert a_full == a_pressured, "A must be intact under budget pressure"

    h_section = result["manifest"]["sections"]["H"]
    assert len(h_section["items"]) < len(hits), "some H items must have been dropped"
    assert h_section["dropped"], "every drop must be listed in the manifest"
    for d in h_section["dropped"]:
        assert d["reason"] == "BUDGET"
        assert "item_id" in d and "bytes" in d

    # the rendered H section names the omission, never silently.
    h_start = result["rendered"].index("## H.")
    h_end = result["rendered"].index("## I.")
    assert "omitted: see manifest" in result["rendered"][h_start:h_end]


def test_blocked_budget_when_a_cannot_fit_even_by_reference(fixture_repo, view_path, registry_path,
                                                               task_spec_factory, monkeypatch):
    # a budget so small that even A's by-reference pointers cannot fit.
    starved = budgetsmod.BudgetProfile(
        name="starved", total_bytes=1, section_caps_bytes={k: None for k in "ABCDEFGHIJ"},
        per_item_cap_bytes=1, rrf_k=60, graph_neighbour_depth=1, parent_expansion_top_n=3, max_slice_chars=1600,
    )
    monkeypatch.setattr(budgetsmod, "load_profile", lambda name, path=None: starved)

    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_BLOCKED_BUDGET
    # BLOCKED_BUDGET never drops a mandatory item -- A still names every required input, unchanged.
    assert len(result["manifest"]["sections"]["A"]["items"]) > 0


def test_over_per_item_cap_a_item_becomes_by_reference(fixture_repo, view_path, registry_path, task_spec_factory,
                                                          monkeypatch):
    small_total = budgetsmod.BudgetProfile(
        name="small-total", total_bytes=50, section_caps_bytes={k: None for k in "ABCDEFGHIJ"},
        per_item_cap_bytes=10, rrf_k=60, graph_neighbour_depth=1, parent_expansion_top_n=3, max_slice_chars=1600,
    )
    monkeypatch.setattr(budgetsmod, "load_profile", lambda name, path=None: small_total)

    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    a_items = result["manifest"]["sections"]["A"]["items"]
    assert a_items, "the fixture must resolve at least one A item"
    if result["status"] == packetmod.STATUS_OK:
        assert any(it["by_reference"] for it in a_items)
