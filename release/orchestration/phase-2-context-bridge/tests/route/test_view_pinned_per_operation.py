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

PASS 5 (BR-DAG-AMEND-R1-23 extended to every audited site -- the coordinator's own second reopening of this
amendment) widens this file's own scope to match: ``compile_packet`` now makes exactly ONE resolution for its
whole lifetime (``resolver.resolve``, ``Compiler.__init__``, every per-query ``gather_with_followup`` call, and
the D.2 "both ways" gather all reuse it -- the compile test below now also asserts full ``packet_sha256``/
``manifest_sha256`` reproducibility, not just per-item commits), and ``why``/``history``/``cite``/``answers lint``
each resolve exactly once per invocation and accept (why/history/cite) or make internal use of (lint, which calls
cite_identifier many times per run) that one resolution. Since each of why/history/cite is a SINGLE call (no
internal rounds/queries the way gather/compile has), the natural way to prove "threaded as a parameter, not
re-resolved" for them is: resolve the view once, then move the LIVE ref, then make the call PASSING that
already-resolved view explicitly -- if the callee were still re-resolving internally, it would see the moved
commit; since it is fixed, it returns byte-identical output to a call made before the move. ``answers lint``
additionally gets a gather/compile-style internal hook (it calls ``cite_identifier`` once per uncited identifier,
per claim, per answer), proving its own many internal calls all agree with each other, not only with an external
caller.
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
    """PASS 5: ``compile_packet`` now makes exactly ONE resolution for its whole lifetime, reusing
    ``routes.resolved_view`` (the one ``real_routes.build_real_routes`` already made, before this test even calls
    ``compile_packet``) instead of a fresh one -- so this test asserts ``viewmod.resolve_view`` is called ZERO
    ADDITIONAL times during the ``compile_packet`` call itself. This is the precise, mechanical form of "four-plus
    resolutions become one": before pass 5, ``resolver.resolve``'s own call, ``Compiler.__init__``'s own call, and
    every per-query ``gather_with_followup``'s own fallback call would each show up here as a further
    ``resolve_view`` invocation (this assertion FAILS against that code, not merely a coincidence of this
    scenario -- verified directly against the pre-pass-5 tree). The per-item and manifest.view checks below are
    the OBSERVABLE consequence of that one resolution; the count is the mechanism."""
    from govbridge.compile import packet as packetmod

    original_commit = built_repo.records_commit
    routes = real_routesmod.build_real_routes(view_path=built_repo.view_path, repo=str(built_repo.root),
                                               registry_path=built_repo.registry_path)
    assert routes.resolved_view.named["records"].commit == original_commit

    resolve_view_calls = {"n": 0}
    real_resolve_view = viewmod.resolve_view

    def _counting_resolve_view(*args, **kwargs):
        resolve_view_calls["n"] += 1
        return real_resolve_view(*args, **kwargs)

    # Patched on the SHARED govbridge.core.view module object: every caller in this codebase does
    # `from govbridge.core import view as viewmod` and then `viewmod.resolve_view(...)` (an attribute lookup at
    # CALL time, never `from ... import resolve_view` directly), so one patch here is visible to every one of
    # them -- resolver.py, packet.py's own Compiler, followup.py's fallback, lexical/query.py, semantic/search.py,
    # answers/cite.py, all alike.
    monkeypatch.setattr(viewmod, "resolve_view", _counting_resolve_view)

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

    assert resolve_view_calls["n"] == 0, (
        f"compile_packet made {resolve_view_calls['n']} additional view resolution(s) beyond the one already in "
        f"routes.resolved_view -- it is not reusing the one view resolved at this operation's own start"
    )
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
    # manifest.view (BR-DAG-AMEND-R1-23 requirement 1's own named example) must show the ONE commit actually used.
    view_rows = {r["name"]: r["commit"] for r in result["manifest"]["view"]}
    assert view_rows["records"] == original_commit, view_rows

    # PASS 5: compile_packet now makes exactly ONE resolution for its whole lifetime (resolver.resolve,
    # Compiler.__init__, every per-query gather_with_followup call, and the D.2 both-ways gather all reuse it --
    # see govbridge/compile/packet.py's own BR-DAG-AMEND-R1-23 comments), so a mid-compile ref move must now leave
    # the WHOLE packet -- not just its exact-route items -- byte-identical to a no-move run, over the identical
    # repo/commit content (the ref is reset back, exactly like the gather test above, never rebuilt fresh).
    _reset_records_ref(built_repo.root, original_commit)
    routes_b = real_routesmod.build_real_routes(view_path=built_repo.view_path, repo=str(built_repo.root),
                                                 registry_path=built_repo.registry_path)
    control = packetmod.compile_packet(task_spec, routes=routes_b, repo=str(built_repo.root),
                                        registry_path=built_repo.registry_path, facets_path=TEST_FACETS_PATH)
    assert result["packet_sha256"] == control["packet_sha256"]
    assert result["manifest_sha256"] == control["manifest_sha256"]


def _hop_commits(edge_dicts: list) -> set:
    """Every commit embedded in a list of ``govbridge.graph.edges.Edge.to_dict()`` rows'
    ``evidence_occurrence`` ("path@commit" or "path@commit:L1-L2")."""
    out = set()
    for e in edge_dicts:
        occ = e.get("evidence_occurrence") if isinstance(e, dict) else None
        if occ and "@" in occ:
            out.add(occ.split("@", 1)[1].split(":", 1)[0])
    return out


def test_why_uses_the_view_pinned_at_its_own_start_even_if_the_records_ref_moves_before_the_call(built_repo):
    """``why()`` is a single call (no internal rounds/queries) -- the way to prove "threaded as a parameter, not
    re-resolved" for a single-call operation is: resolve once, move the LIVE ref, then call PASSING that already-
    resolved view explicitly. If ``why()`` still re-resolved internally despite being given one, the second call
    would see the moved commit and disagree with the first; since it is fixed (BR-DAG-AMEND-R1-23, pass 5), the
    two calls are byte-identical."""
    from govbridge.graph import why as whymod

    original_commit = built_repo.records_commit
    resolved_view = viewmod.resolve_view(viewmod.load_view(built_repo.view_path), repo=str(built_repo.root))
    assert resolved_view.named["records"].commit == original_commit

    baseline = whymod.why(built_repo.id_defined_elsewhere, repo=str(built_repo.root), view_path=built_repo.view_path,
                           registry_path=built_repo.registry_path, resolved_view=resolved_view)
    assert any(s["status"] == "PRESENT" for s in baseline["stages"].values()), baseline

    moved_commit = _move_records_ref(built_repo.root)
    assert moved_commit != original_commit

    moved = whymod.why(built_repo.id_defined_elsewhere, repo=str(built_repo.root), view_path=built_repo.view_path,
                        registry_path=built_repo.registry_path, resolved_view=resolved_view)

    assert moved == baseline, "why() disagreed with itself after the ref moved -- it re-resolved internally"
    assert {"name": "records", "commit": original_commit, "status": "OK"} in moved["resolved_refs"]
    for stage in moved["stages"].values():
        commits = _hop_commits(stage["hops"])
        assert commits <= {original_commit}, (stage, commits)


def test_history_uses_the_view_pinned_at_its_own_start_even_if_the_records_ref_moves_before_the_call(built_repo):
    """Same technique as the ``why()`` test above, for ``history()``."""
    from govbridge.graph import history as historymod

    original_commit = built_repo.records_commit
    resolved_view = viewmod.resolve_view(viewmod.load_view(built_repo.view_path), repo=str(built_repo.root))

    baseline = historymod.history(built_repo.id_defined_elsewhere, repo=str(built_repo.root),
                                   view_path=built_repo.view_path, registry_path=built_repo.registry_path,
                                   resolved_view=resolved_view)

    moved_commit = _move_records_ref(built_repo.root)
    assert moved_commit != original_commit

    moved = historymod.history(built_repo.id_defined_elsewhere, repo=str(built_repo.root),
                                view_path=built_repo.view_path, registry_path=built_repo.registry_path,
                                resolved_view=resolved_view)

    assert moved == baseline, "history() disagreed with itself after the ref moved -- it re-resolved internally"
    assert {"name": "records", "commit": original_commit, "status": "OK"} in moved["resolved_refs"]
    commits = _hop_commits([e["edge"] for e in moved["entries"] if e.get("edge") is not None])
    assert commits <= {original_commit}, commits


def _add_definable_record(root: Path) -> str:
    """``followup_repobuilder``'s own ``ZK-0002`` is only ever MENTIONED (``# ZK-0002 elsewhere``, a level-1
    heading with trailing text) -- the real config/id-grammar.yaml's own markdown rules all need either a
    two-column header-table row, a severity-suffixed heading, a bare 1-2-letter/1-2-digit local token, or an
    EXACT level-2 ``## <ID>`` heading (``DR-MD-LEDGER-HEADING``) to call something a DEFINITION, so
    ``lifecycle.find_definition``/``cite_identifier``'s own id-grammar branch never resolves it -- confirmed
    empirically, not assumed, and true regardless of this reopening's own fix (a pre-existing property of this
    fixture, unrelated to view-pinning). Adds one new commit with a heading THAT DOES match
    ``DR-MD-LEDGER-HEADING`` (``## ZK-0002`` alone), so the cite/lint tests below have a real definition to
    resolve. Returns the new HEAD commit."""
    (root / "area_ledger.md").write_text("## ZK-0002\n\nA definable record for a test.\n")
    repobuilder._git(root, "add", "-A")
    repobuilder._git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m",
                      "add a definable record for the view-pinning tests")
    return repobuilder._git(root, "rev-parse", "HEAD").stdout.strip()


def test_cite_uses_the_view_pinned_at_its_own_start_even_if_the_records_ref_moves_before_the_call(built_repo):
    """Same technique again, for ``cite_identifier()`` -- the id-grammar branch (``KIND_ID`` ->
    ``lifecycle.find_definition``), the one BR-DAG-AMEND-R1-23 explicitly names ("lifecycle's id_lookup
    definition_sites use the pinned records commit") as needing this thread."""
    from govbridge.answers import cite as citemod

    original_commit = _add_definable_record(built_repo.root)
    resolved_view = viewmod.resolve_view(viewmod.load_view(built_repo.view_path), repo=str(built_repo.root))

    baseline = citemod.cite_identifier(built_repo.id_defined_elsewhere, view_path=built_repo.view_path,
                                        repo=str(built_repo.root), resolved_view=resolved_view)
    assert baseline["status"] == citemod.STATUS_RESOLVED, baseline

    moved_commit = _move_records_ref(built_repo.root)
    assert moved_commit != original_commit

    moved = citemod.cite_identifier(built_repo.id_defined_elsewhere, view_path=built_repo.view_path,
                                     repo=str(built_repo.root), resolved_view=resolved_view)

    assert moved == baseline, "cite_identifier() disagreed with itself after the ref moved -- it re-resolved internally"
    assert moved["citation"]["commit"] == original_commit
    assert {"name": "records", "commit": original_commit, "status": "OK"} in moved["resolved_refs"]


def test_answers_lint_uses_one_view_for_every_internal_cite_call_even_if_the_records_ref_moves_mid_run(
        built_repo, monkeypatch):
    """``lint_answers`` calls ``cite_identifier`` once per uncited identifier, per claim, per answer -- a
    gather/compile-shaped "many internal calls in one operation" case, so this test uses the SAME
    monkeypatched-hook technique those two use (move the ref exactly once, on the first internal call), rather
    than the explicit-resolved_view technique the three single-call operations above use."""
    from govbridge.answers import cite as citemod
    from govbridge.answers import lint as lintmod

    original_commit = _add_definable_record(built_repo.root)
    doc = {
        "schema": "govbridge-answers/1", "run_id": "RA-VIEWPIN", "packets_used": [],
        "answers": [
            {"query_id": "Q1", "status": "ANSWERED",
             "answer_text": f"{built_repo.id_defined_elsewhere} is mentioned here without a citation.",
             "citations": []},
        ],
    }

    moved = {"done": False, "new_commit": None}
    real_cite_identifier = citemod.cite_identifier

    def _cite_and_move_once(*args, **kwargs):
        if not moved["done"]:
            moved["done"] = True
            moved["new_commit"] = _move_records_ref(built_repo.root)
        return real_cite_identifier(*args, **kwargs)

    monkeypatch.setattr(lintmod.citemod, "cite_identifier", _cite_and_move_once)

    result = lintmod.lint_answers(doc, [], view_path=built_repo.view_path, repo=str(built_repo.root))

    assert moved["done"], "the ref-move hook never fired -- this test would prove nothing"
    assert moved["new_commit"] != original_commit
    assert {"name": "records", "commit": original_commit, "status": "OK"} in result["resolved_refs"]
    assert any(f.get("identifier") == "ZK-0002" for f in result["findings"]), result["findings"]

    # CONTROL: an unmoved run over the identical repo/commit content must be identical.
    _reset_records_ref(built_repo.root, original_commit)
    control = lintmod.lint_answers(doc, [], view_path=built_repo.view_path, repo=str(built_repo.root))
    assert result["findings"] == control["findings"]
    assert result["open_findings"] == control["open_findings"]
    assert result["status"] == control["status"]


def test_exact_id_lookup_resolves_the_view_exactly_once_per_call(built_repo, monkeypatch):
    """A second, independent re-audit (pass 5) found this INSIDE govbridge/core/exact.py itself, already in this
    run's own scope: `id_lookup`'s own `mention_sites` (via `grep`) and `definition_sites` (via `lifecycle.
    find_definition`) each resolved `config/canonical-view.yaml` independently whenever the caller (a standalone
    `govbridge exact id` invocation) gave no `resolved_view` -- one `id_lookup` call, two live resolutions of the
    SAME "records" ref, which could disagree if it moved between them. Counting `resolve_view` calls (the same
    technique the compile test above uses) proves it directly: one call must make exactly ONE resolution."""
    from govbridge.core import exact as exactmod

    original_commit = _add_definable_record(built_repo.root)

    resolve_view_calls = {"n": 0}
    real_resolve_view = viewmod.resolve_view

    def _counting_resolve_view(*args, **kwargs):
        resolve_view_calls["n"] += 1
        return real_resolve_view(*args, **kwargs)

    monkeypatch.setattr(viewmod, "resolve_view", _counting_resolve_view)

    result = exactmod.id_lookup(built_repo.id_defined_elsewhere, view_path=built_repo.view_path,
                                 repo=str(built_repo.root))

    assert resolve_view_calls["n"] == 1, (
        f"id_lookup made {resolve_view_calls['n']} view resolution(s) for one call, not one -- mention_sites and "
        f"definition_sites could see different commits if the records ref moved between them"
    )
    assert result["mention_sites"], result
    assert result["definition_sites"], result
    assert result["commit"] == original_commit
    assert result["definition_sites"][0]["commit"] == original_commit
