"""BR-DAG-AMEND-R1-23 (ONE RESOLVED VIEW PER OPERATION): a query operation resolves config/canonical-view.yaml
ONCE, at its own start, and threads that one ``ResolvedView`` through every route/graph-hop/git-read it makes for
its whole lifetime -- never re-resolving a ``follow: tip`` ref (concretely, the "records" role) mid-operation,
which could otherwise see a DIFFERENT commit if that ref moves while the operation is still running. This is
exactly what AGENT_RUNS/BR-AR-0024.check-ca-why-wall-time-defaults.out found empirically: a single,
uninterrupted ~1031s gather call recorded FOUR different "records" commits across its own merged items, traced to
``govbridge.core.exact.grep``/``id_lookup`` re-resolving the view fresh on every call instead of reusing the ONE
view ``govbridge.route.real_routes.build_real_routes`` already resolved once (``code_route``'s own
``product_commit``, computed once and closed over, never had this problem).

Both tests below reuse ``tests/fixtures/gather/followup/followup_repobuilder.py``'s own small, real, three-ref git
fixture (never a live/production ref) and move ITS "records" ref (``refs/heads/main``, ``follow: tip``) with a
monkeypatched hook fired EXACTLY ONCE, between two of the operation's own exact-route calls -- never a real
thread or a sleep, so the test's own pass is fully deterministic (R1-T1), not merely likely. An empty commit
(``git commit --allow-empty``) is the stand-in for "another agent's own commit lands on the shared orchestration
branch while this operation is still running" -- it never touches tracked file content, so nothing about the
fixture's own corpus changes, only its "records" ref's tip commit.

The compile test is deliberately narrower than the gather test: this run's own mutation_scope is
``core/exact.py``, ``core/view.py``, ``route/router.py`` and ``route/real_routes.py`` (``compile/packet.py`` is
not). The tests-wide audit this reopening also ran (checkpoint ``findings``) found ``compile_packet`` itself
resolves the view independently, several MORE times, in places this run cannot fix (``resolver.resolve``,
``Compiler.__init__``, each query's own ``gather_with_followup`` call, which never receives ``routes.
resolved_view``) -- a broader defect this test does not claim to close. What IS proven here is the exact slice
BR-DAG-AMEND-R1-23 asks this node to fix for compile too: the SAME ``RouteSet.exact`` closure this compile's own
``real_routes.build_real_routes`` call built is reused, unchanged, across every query -- so every exact-route
occurrence in the resulting packet carries the ONE commit pinned when that RouteSet was built, regardless of
what the live ref does afterward.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from govbridge.core import taskctx as taskctxmod
from govbridge.core import view as viewmod
from govbridge.gather import facets as facetsmod
from govbridge.gather import followup as followupmod
from govbridge.gather import identifiers as identifiersmod
from govbridge.route import real_routes as real_routesmod

FIXTURES_GATHER = Path(__file__).resolve().parents[1] / "fixtures" / "gather"
FIXTURES_FOLLOWUP = FIXTURES_GATHER / "followup"
sys.path.insert(0, str(FIXTURES_GATHER))
sys.path.insert(0, str(FIXTURES_FOLLOWUP))
import followup_repobuilder as repobuilder  # noqa: E402

TEST_FACETS_PATH = str(FIXTURES_GATHER / "test-facets.yaml")


@pytest.fixture(autouse=True)
def _isolated_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    facetsmod.clear_cache()
    taskctxmod.reset()
    yield
    taskctxmod.reset()
    facetsmod.clear_cache()


@pytest.fixture
def built_repo(tmp_path):
    from govbridge.core import freshness
    br = repobuilder.build(tmp_path)
    r = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    assert r["trigger"] == "FULL"
    return br


def _move_records_ref(root: Path) -> str:
    """A single, deterministic stand-in for "another agent commits to the shared orchestration branch while this
    operation is still running" (the defect BR-DAG-AMEND-R1-23 reports): an empty commit onto this fixture's own
    "records" ref (``refs/heads/main``, ``follow: tip``), never touching any tracked file content. Returns the new
    tip commit (asserted, by both tests below, to differ from the one pinned before this ran)."""
    repobuilder._git(root, "commit", "--allow-empty", "-q", "-m", "simulated concurrent commit (BR-DAG-AMEND-R1-23)")
    return repobuilder._git(root, "rev-parse", "HEAD").stdout.strip()


def _reset_records_ref(root: Path, commit: str) -> None:
    """Restores ``refs/heads/main`` to ``commit`` directly (``git update-ref``, never a checkout -- every read
    this domain makes is through git plumbing, not the working tree), so the SAME fixture repo/commit content can
    be reused for a "control" (no-move) run after ``_move_records_ref`` -- two SEPARATE ``followup_repobuilder.
    build()`` calls would each stamp their own commit at a different wall-clock second, making their own
    ``records_commit`` values differ for reasons having nothing to do with this test, and defeating a fair
    moved-vs-unmoved comparison."""
    repobuilder._git(root, "update-ref", "refs/heads/main", commit)


def _query(text, id_="Q1", facets=None, routes=None):
    q = {"id": id_, "text": text, "class": None, "subject": None}
    if facets is not None:
        q["facets"] = facets
    if routes is not None:
        q["routes"] = routes
    return q


def test_gather_merged_items_all_carry_the_records_commit_pinned_at_gather_start_even_if_the_ref_moves_mid_gather(
        built_repo, monkeypatch):
    """The ref moves once, via a monkeypatched hook, exactly between round 0 (the base ``engine.gather`` call,
    already run by the time the hook fires) and round 1's own new-candidate identification
    (``identifiersmod.extract_all``, ``followup.py``'s own round-loop entry point) -- after ``real_routes.
    build_real_routes`` has ALREADY resolved and closed over the view, so this is squarely "moves DURING the
    operation", not "before it starts". "citing record explains a rule" is the same query text
    ``tests/gather/test_followup.py``'s own
    ``test_a_record_citing_an_id_defined_elsewhere_is_reached_within_three_rounds`` uses to reach a KIND_RECORD_ID
    identifier, resolved via ``resolve_identifier`` -> ``_resolve_via_exact`` -> ``routes.run("exact", ...)`` --
    the exact call path this reopening's fix touches."""
    original_commit = built_repo.records_commit

    routes = real_routesmod.build_real_routes(view_path=built_repo.view_path, repo=str(built_repo.root),
                                               registry_path=built_repo.registry_path)
    resolved_view = viewmod.resolve_view(viewmod.load_view(built_repo.view_path), repo=str(built_repo.root))
    # sanity: both resolutions above happen BEFORE any move, so both must already agree with the fixture's own
    # known records commit -- if this fails, the test fixture itself (not the fix) is broken.
    assert resolved_view.named["records"].commit == original_commit
    assert routes.resolved_view.named["records"].commit == original_commit

    moved = {"done": False, "new_commit": None}
    real_extract_all = identifiersmod.extract_all

    def _extract_all_and_move_once(*args, **kwargs):
        if not moved["done"]:
            moved["done"] = True
            moved["new_commit"] = _move_records_ref(built_repo.root)
        return real_extract_all(*args, **kwargs)

    monkeypatch.setattr(followupmod.identifiersmod, "extract_all", _extract_all_and_move_once)

    ctx = taskctxmod.TaskContext(source="test")
    result = followupmod.gather_with_followup(
        _query("citing record explains a rule", facets=["purpose"]), routes, task=ctx, batch_size=8, max_rounds=10,
        threads=1, max_followup_rounds=3, resolved_view=resolved_view, repo=str(built_repo.root),
        facets_path=TEST_FACETS_PATH,
    )

    assert moved["done"], "the ref-move hook never fired -- this test would prove nothing"
    assert moved["new_commit"] != original_commit

    exact_items = [m for m in result["merged"] if m["route"] == "exact"]
    assert exact_items, "the record-id citation must resolve via the exact route for this test to be meaningful"
    for m in exact_items:
        assert m["occurrence"]["commit"] == original_commit, (
            f"exact-route item {m['unit_id']!r} carries commit {m['occurrence']['commit']!r}, not the commit "
            f"({original_commit!r}) pinned once at the start of this gather -- the records ref was re-resolved "
            f"mid-operation"
        )
        # AGENT_RUNS/BR-AR-0024.check-ca-why-wall-time-defaults.out's own observed symptom: a mixed
        # ref_summary.identical like ["records", "records"] (one entry per DIFFERENTLY-resolved occurrence that
        # merged into the same item) instead of a clean ["records"] (one entry, since every occurrence of this
        # item agreed on the same commit).
        assert m["ref_summary"]["identical"].count("records") <= 1, m["ref_summary"]

    # CONTROL: an unmoved run of the identical query, over the identical store/fixture/commit content, must be
    # byte-identical -- BR-DAG-AMEND-R1-23's own acceptance line ("merged_sha256 equals a run with no move"). The
    # ref is restored to its ORIGINAL commit first: it is still sitting at moved["new_commit"] from the run above
    # (the SAME repo is reused, deliberately, so both runs see byte-identical commit content -- see
    # _reset_records_ref's own docstring for why a second, fresh followup_repobuilder.build() would not do).
    _reset_records_ref(built_repo.root, original_commit)
    routes_b = real_routesmod.build_real_routes(view_path=built_repo.view_path, repo=str(built_repo.root),
                                                 registry_path=built_repo.registry_path)
    resolved_view_b = viewmod.resolve_view(viewmod.load_view(built_repo.view_path), repo=str(built_repo.root))
    ctx_b = taskctxmod.TaskContext(source="test")
    control = followupmod.gather_with_followup(
        _query("citing record explains a rule", facets=["purpose"]), routes_b, task=ctx_b, batch_size=8,
        max_rounds=10, threads=1, max_followup_rounds=3, resolved_view=resolved_view_b, repo=str(built_repo.root),
        facets_path=TEST_FACETS_PATH,
    )
    assert result["merged_sha256"] == control["merged_sha256"]


def test_compile_exact_route_items_all_carry_the_records_commit_pinned_once_even_if_the_ref_moves_mid_compile(
        built_repo, monkeypatch):
    """See the module docstring for why this is narrower than the gather test above: it proves exactly what this
    reopening's own fix guarantees for compile (every exact-route occurrence across every query in ONE compile
    shares the ONE commit ``real_routes.build_real_routes`` pinned), not that ``compile_packet`` as a whole is
    immune to a mid-compile ref move (it is not, for reasons outside this node's mutation_scope -- see this run's
    own checkpoint findings)."""
    from govbridge.compile import packet as packetmod

    original_commit = built_repo.records_commit
    routes = real_routesmod.build_real_routes(view_path=built_repo.view_path, repo=str(built_repo.root),
                                               registry_path=built_repo.registry_path)
    assert routes.resolved_view.named["records"].commit == original_commit

    moved = {"done": False, "new_commit": None}
    real_exact = routes.exact

    def _exact_and_move_once(**kwargs):
        # Fires on the FIRST call to the exact route ANY query in this compile makes -- guaranteed to be AFTER
        # compile_packet's own upfront resolver.resolve()/Compiler.__init__ resolutions (neither ever calls
        # routes.exact), so the move lands strictly BETWEEN two queries' own exact-route retrievals, never before
        # the first one.
        if not moved["done"]:
            moved["done"] = True
            moved["new_commit"] = _move_records_ref(built_repo.root)
        return real_exact(**kwargs)

    monkeypatch.setattr(routes, "exact", _exact_and_move_once)

    # config/facets.yaml (and this fixture's own tests/fixtures/gather/test-facets.yaml) never declare "exact" as
    # a FACET route -- a query's own `routes` field only RESTRICTS which routes a facet may use, it cannot make a
    # facet invoke one the facet itself never lists. The only path to the exact route, here as in gather, is
    # follow-up identifier resolution (KIND_RECORD_ID -> resolve_identifier -> _resolve_via_exact ->
    # routes.run("exact", ...)) -- the SAME "citing record explains a rule" trigger the gather test above (and
    # tests/gather/test_followup.py's own test_a_record_citing_an_id_defined_elsewhere_is_reached_within_three_
    # rounds) already uses, run here as two SEPARATE queries in one compile. Unlike a bare gather_with_followup
    # call, compile_packet's own per-query loop (packet.py) additionally zeroes any route not in
    # ``routermod.select_routes(q, grammar)`` -- plain prose like this query's own text contains no id/path/commit
    # -shaped token, so auto-detection alone would zero "exact" out before follow-up ever gets a chance to use it.
    # An explicit `routes` list on the query "always wins verbatim" (select_routes's own docstring), so both
    # queries name lexical (round 0 needs it to surface the citing record at all) and exact (for the follow-up
    # resolution this test is about) explicitly.
    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-VIEWPIN", "role": "test",
        "objective": "prove one resolved view per compile operation (BR-DAG-AMEND-R1-23)",
        "view": built_repo.view_path,
        "required_inputs": [{"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"}],
        "seeds": [],
        "queries": [
            _query("citing record explains a rule", id_="Q1", facets=["purpose"], routes=["lexical", "exact"]),
            _query("citing record explains a rule", id_="Q2", facets=["purpose"], routes=["lexical", "exact"]),
        ],
        "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED", "PARTIAL", "BLOCKED"],
        "budget_profile": "bounded-builder",
    }
    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(built_repo.root),
                                       registry_path=built_repo.registry_path, facets_path=TEST_FACETS_PATH)

    assert moved["done"], "the ref-move hook never fired -- this test would prove nothing"
    assert moved["new_commit"] != original_commit

    exact_items = []
    for qid in ("Q1", "Q2"):
        gr = result["gather_results"].get(qid) or {}
        exact_items.extend(m for m in gr.get("merged", []) if m["route"] == "exact")
    assert exact_items, "both queries' own exact-route retrieval must find the literal for this test to mean anything"
    for m in exact_items:
        assert m["occurrence"]["commit"] == original_commit, (
            f"compile's own exact-route item {m['unit_id']!r} carries commit {m['occurrence']['commit']!r}, not "
            f"the commit ({original_commit!r}) this compile's own RouteSet was built with"
        )
