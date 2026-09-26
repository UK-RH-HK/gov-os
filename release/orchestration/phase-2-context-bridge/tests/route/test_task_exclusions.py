"""REPAIR-1 node R1-RX (OBS-BR-08, OD-BR-03 item 1): ``retrieval_exclusions`` applied AUTOMATICALLY by every route,
every CLI query command (search/why/impact/history/exact/state) and every compile call site (the query loop, the
seed code route, the D.2 "evidence both ways" templates). Acceptance shape: "in a fixture repo whose excluded
directory holds the best lexical and semantic match, every command and compile return 0 excluded occurrences and a
non-zero excluded_hits disclosure."

No public demonstration query text, no run-1 answer and no oracle content is used here (REPAIR-1 rule 2): the
fixture (``tests/fixtures/route/exclusions/exclusions_repobuilder.py``) is self-contained and synthetic (OC-BR-02).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

FIXTURES_EXCLUSIONS = Path(__file__).resolve().parents[1] / "fixtures" / "route" / "exclusions"
sys.path.insert(0, str(FIXTURES_EXCLUSIONS))
import exclusions_repobuilder as repobuilder  # noqa: E402

from govbridge import cli  # noqa: E402
from govbridge.authority import state as statemod  # noqa: E402
from govbridge.compile import packet as packetmod  # noqa: E402
from govbridge.core import exact as exactmod  # noqa: E402
from govbridge.core import freshness, pathrules, taskctx as taskctxmod  # noqa: E402
from govbridge.graph import history as historymod  # noqa: E402
from govbridge.graph import impact as impactmod  # noqa: E402
from govbridge.graph import why as whymod  # noqa: E402
from govbridge.route import real_routes  # noqa: E402
from govbridge.route.router import FusedHit, RouteHit, RouteOccurrence, RouteSet  # noqa: E402

RETRIEVAL_EXCLUSIONS = repobuilder.RETRIEVAL_EXCLUSIONS


# ---------------------------------------------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _isolated_env(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    monkeypatch.delenv(taskctxmod.ENV_VAR, raising=False)
    taskctxmod.reset()
    yield
    # R1-RX rule 8 / this module's own discipline: never leak the ambient TaskContext into a later, unrelated test.
    taskctxmod.reset()


@pytest.fixture
def fixture_repo(tmp_path):
    return repobuilder.build(tmp_path / "repo")


@pytest.fixture
def view_path(tmp_path):
    p = tmp_path / "canonical-view.yaml"
    repobuilder.write_canonical_view(p)
    return str(p)


@pytest.fixture
def registry_path(tmp_path):
    p = tmp_path / "authority-registry.yaml"
    repobuilder.write_registry(p)
    return str(p)


@pytest.fixture
def task_spec_path(tmp_path, view_path):
    """A task-spec YAML on disk, for ``--task``/``GOVBRIDGE_TASK`` loading -- never the compiler's own task_spec
    dict (that one is built inline, per test, since its ``view``/``seeds``/``queries`` vary)."""
    p = tmp_path / "task-spec.yaml"
    p.write_text(
        "schema: govbridge-task-spec/1\n"
        "task_id: T-EXCL-TASK\n"
        f"retrieval_exclusions: {json.dumps(RETRIEVAL_EXCLUSIONS)}\n",
        encoding="utf-8",
    )
    return str(p)


def _built_routes(fixture_repo, view_path, registry_path):
    freshness.run(view_path=view_path, rules_path=str(fixture_repo.root / "config" / "corpus-rules.yaml"),
                  repo=str(fixture_repo.root), from_clean=True)
    return real_routes.build_real_routes(view_path=view_path, repo=str(fixture_repo.root),
                                          registry_path=registry_path)


def _any_excluded_path(paths) -> bool:
    return any(pathrules.any_glob_match(p, RETRIEVAL_EXCLUSIONS) is not None for p in paths if p)


# ---------------------------------------------------------------------------------------------------------------
# govbridge.core.taskctx -- the module itself
# ---------------------------------------------------------------------------------------------------------------

def test_task_context_is_excluded_and_merge_and_count(tmp_path):
    ctx = taskctxmod.TaskContext(source="t", retrieval_exclusions=("excluded/**",))
    assert ctx.is_excluded("excluded/x.rs") is True
    assert ctx.is_excluded("included/x.rs") is False
    assert ctx.is_excluded(None) is False
    assert ctx.merge_exclude(["extra/**", "excluded/**"]) == ["excluded/**", "extra/**"]
    assert ctx.count_excluded(["excluded/a", "included/a", "excluded/b"]) == 2


def test_task_context_load_from_path_and_missing_file_is_empty(tmp_path):
    p = tmp_path / "task-spec.yaml"
    p.write_text("retrieval_exclusions: ['a/**', 'b/**']\n", encoding="utf-8")
    ctx = taskctxmod.load(str(p))
    assert ctx.retrieval_exclusions == ("a/**", "b/**")

    assert taskctxmod.load(str(tmp_path / "does-not-exist.yaml")) is taskctxmod.EMPTY
    assert taskctxmod.load(None, env={}) is taskctxmod.EMPTY


def test_task_context_ambient_current_reads_env_without_from_args(tmp_path, monkeypatch):
    p = tmp_path / "task-spec.yaml"
    p.write_text("retrieval_exclusions: ['env-excluded/**']\n", encoding="utf-8")
    assert taskctxmod.current() is taskctxmod.EMPTY
    monkeypatch.setenv(taskctxmod.ENV_VAR, str(p))
    assert taskctxmod.current().retrieval_exclusions == ("env-excluded/**",)
    monkeypatch.delenv(taskctxmod.ENV_VAR)
    assert taskctxmod.current() is taskctxmod.EMPTY


def test_task_context_from_args_only_installs_when_task_flag_given():
    class Args:
        task = None

    ctx = taskctxmod.from_args(Args())
    assert ctx is taskctxmod.EMPTY
    assert taskctxmod.current() is taskctxmod.EMPTY  # never installed just because from_args() was called


def test_task_context_set_current_and_reset_round_trip():
    previous = taskctxmod.set_current(taskctxmod.TaskContext(source="x", retrieval_exclusions=("z/**",)))
    assert previous is taskctxmod.EMPTY
    assert taskctxmod.current().retrieval_exclusions == ("z/**",)
    taskctxmod.reset()
    assert taskctxmod.current() is taskctxmod.EMPTY


def test_filter_edges_drops_excluded_path_shaped_edges_and_counts():
    class FakeEdge:
        def __init__(self, occ):
            self.evidence_occurrence = occ

    edges = [
        FakeEdge("excluded/a.md@deadbeef"), FakeEdge("included/a.md@deadbeef"),
        FakeEdge("blob123:4"),  # not path-shaped -- always kept, honestly (occurrence_path returns None)
        {"evidence_occurrence": "excluded/b.md@deadbeef:1-2"},
    ]
    ctx = taskctxmod.TaskContext(source="t", retrieval_exclusions=("excluded/**",))
    kept, excluded = taskctxmod.filter_edges(edges, ctx)
    assert excluded == 2
    assert len(kept) == 2
    kept_occs = {e.evidence_occurrence if not isinstance(e, dict) else e["evidence_occurrence"] for e in kept}
    assert kept_occs == {"included/a.md@deadbeef", "blob123:4"}


def test_occurrence_path_is_honestly_none_for_non_path_shaped_occurrences():
    assert taskctxmod.occurrence_path("a/b.rs@deadbeef:1-2") == "a/b.rs"
    assert taskctxmod.occurrence_path("blob123:4") is None
    assert taskctxmod.occurrence_path(None) is None


# ---------------------------------------------------------------------------------------------------------------
# govbridge.route.real_routes -- explicit AND ambient exclusion, every route
# ---------------------------------------------------------------------------------------------------------------

def test_lexical_route_excludes_explicitly_and_discloses_count(fixture_repo, view_path, registry_path):
    routes = _built_routes(fixture_repo, view_path, registry_path)
    counter = taskctxmod.ExclusionCounter()
    hits = routes.lexical(text='"zzyzx" OR "quartz"', k=8, exclude=RETRIEVAL_EXCLUSIONS, exclude_counter=counter)
    assert hits, "the weaker, included match must still surface once the best (excluded) one is dropped"
    assert not _any_excluded_path(o.path for h in hits for o in h.occurrences)
    assert counter.count > 0


def test_lexical_route_excludes_ambiently_via_govbridge_task_env(fixture_repo, view_path, registry_path,
                                                                   task_spec_path, monkeypatch):
    routes = _built_routes(fixture_repo, view_path, registry_path)
    # mirrors ARCHITECTURE/REPAIR-1/evidence/tools/exclusion_probe.py's own "cli_default_no_exclude" mode: no
    # exclude= passed at all -- only GOVBRIDGE_TASK names the task context.
    before = routes.lexical(text='"zzyzx" OR "quartz"', k=8)
    assert _any_excluded_path(o.path for h in before for o in h.occurrences), \
        "sanity: without a task context the excluded content leaks, exactly as run-1 measured"

    monkeypatch.setenv(taskctxmod.ENV_VAR, task_spec_path)
    after = routes.lexical(text='"zzyzx" OR "quartz"', k=8)
    assert not _any_excluded_path(o.path for h in after for o in h.occurrences)


def test_code_route_excludes_definitions_callers_and_bare_occurrences(fixture_repo, view_path, registry_path):
    routes = _built_routes(fixture_repo, view_path, registry_path)
    counter = taskctxmod.ExclusionCounter()
    hits = routes.code(seeds=["ex_target_fn"], exclude=RETRIEVAL_EXCLUSIONS, exclude_counter=counter)
    assert hits == []  # the ONLY definition of ex_target_fn is under excluded/x.rs
    assert counter.count > 0


def test_exact_route_excludes_mention_sites_and_discloses_count(fixture_repo, view_path, registry_path):
    routes = _built_routes(fixture_repo, view_path, registry_path)
    counter = taskctxmod.ExclusionCounter()
    hits = routes.exact(text="ex_target_fn", exclude=RETRIEVAL_EXCLUSIONS, exclude_counter=counter)
    assert hits == []
    assert counter.count > 0


def test_semantic_route_excludes_via_monkeypatched_search(fixture_repo, view_path, registry_path, monkeypatch):
    """The real semantic engine needs an embedding model this bounded node does not depend on -- the exclusion
    logic real_routes.py itself owns is exercised directly against a controlled ``semanticsearch.search`` result,
    the same technique tests/compile/test_compile_router.py already uses for fusion logic."""
    routes = real_routes.build_real_routes(view_path=view_path, repo=str(fixture_repo.root),
                                            registry_path=registry_path)

    def fake_search(text, k=10, view_path=None, repo=None, classify=None, **_kw):
        return {"results": [
            {"id": "SEM-EXCLUDED", "rank": 1, "score": 0.9,
             "occurrence": {"ref": "records", "commit": fixture_repo.commit,
                             "path": repobuilder.LEXICAL_BEST_PATH, "line_start": 1, "line_end": 1}},
            {"id": "SEM-INCLUDED", "rank": 2, "score": 0.5,
             "occurrence": {"ref": "records", "commit": fixture_repo.commit,
                             "path": repobuilder.LEXICAL_WEAK_PATH, "line_start": 1, "line_end": 1}},
        ]}

    monkeypatch.setattr(real_routes.semanticsearch, "search", fake_search)
    counter = taskctxmod.ExclusionCounter()
    hits = routes.semantic(text="zzyzx quartz protocol details", k=8, exclude=RETRIEVAL_EXCLUSIONS,
                            exclude_counter=counter)
    assert [h.unit_id for h in hits] == ["SEM-INCLUDED"]
    assert counter.count == 1


def test_semantic_route_excludes_ambiently(fixture_repo, view_path, registry_path, task_spec_path, monkeypatch):
    routes = real_routes.build_real_routes(view_path=view_path, repo=str(fixture_repo.root),
                                            registry_path=registry_path)

    def fake_search(text, k=10, view_path=None, repo=None, classify=None, **_kw):
        return {"results": [
            {"id": "SEM-EXCLUDED", "rank": 1, "score": 0.9,
             "occurrence": {"ref": "records", "commit": fixture_repo.commit,
                             "path": repobuilder.LEXICAL_BEST_PATH, "line_start": 1, "line_end": 1}},
        ]}

    monkeypatch.setattr(real_routes.semanticsearch, "search", fake_search)
    monkeypatch.setenv(taskctxmod.ENV_VAR, task_spec_path)
    hits = routes.semantic(text="zzyzx quartz protocol details", k=8)  # no exclude= at all
    assert hits == []


# ---------------------------------------------------------------------------------------------------------------
# govbridge.cli search -- --task wiring end to end
# ---------------------------------------------------------------------------------------------------------------

def test_cli_search_applies_task_and_discloses_excluded_hits(fixture_repo, view_path, registry_path,
                                                                task_spec_path, capsys, monkeypatch):
    freshness.run(view_path=view_path, rules_path=str(fixture_repo.root / "config" / "corpus-rules.yaml"),
                  repo=str(fixture_repo.root), from_clean=True)
    # cli.py's `search` has no --repo of its own (a pre-existing gap, not this node's to add): its real_routes
    # build resolves git refs against the process cwd, so the fixture repo must BE that cwd for this one test.
    monkeypatch.chdir(fixture_repo.root)
    rc = cli.main(["search", '"zzyzx" OR "quartz"', "--route", "lexical", "--view", view_path,
                   "--registry", registry_path, "--task", task_spec_path])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["excluded_hits"] > 0
    all_paths = [o["path"] for hits in out["hits_by_route"].values() for h in hits for o in h["occurrences"]]
    assert not _any_excluded_path(all_paths)


# ---------------------------------------------------------------------------------------------------------------
# govbridge.compile.packet -- the query loop, the seed code route, the D.2 both-ways templates
# ---------------------------------------------------------------------------------------------------------------

def _leaky_route_set(excluded_path="excluded/leaky", included_path="included/leaky"):
    """A deterministic, controlled RouteSet standing in for the real B2-B4 routes: every slot returns one hit
    under ``excluded_path`` and one under ``included_path``, and -- exactly as govbridge.route.real_routes's own
    adapters must -- drops/counts the excluded one whenever it is CALLED WITH exclude=/exclude_counter=. A call
    site in govbridge.compile.packet that forgot to pass them would leak "LEAK-EXCLUDED" into the rendered packet,
    which the tests below check for directly."""
    def route_fn(text=None, seeds=None, k=8, exclude=None, exclude_counter=None, **_kw):
        candidates = [
            RouteHit(unit_id="LEAK-EXCLUDED", unit_kind="chunk", route="lexical", rank=1,
                     occurrences=(RouteOccurrence(ref="records", commit="deadbeef", path=excluded_path,
                                                   version_status="CANONICAL"),),
                     text="excluded content", authority_class="EVIDENCE", lifecycle="ACTIVE"),
            RouteHit(unit_id="LEAK-INCLUDED", unit_kind="chunk", route="lexical", rank=2,
                     occurrences=(RouteOccurrence(ref="records", commit="deadbeef", path=included_path,
                                                   version_status="CANONICAL"),),
                     text="included content", authority_class="EVIDENCE", lifecycle="ACTIVE"),
        ]
        kept = []
        for h in candidates:
            if exclude and pathrules.any_glob_match(h.occurrences[0].path, exclude) is not None:
                if exclude_counter is not None:
                    exclude_counter.bump()
                continue
            kept.append(h)
        return kept
    return RouteSet(exact=route_fn, lexical=route_fn, semantic=route_fn, code=route_fn)


def test_compile_query_loop_and_d2_both_ways_never_leak_excluded_hit(view_path, registry_path, fixture_repo):
    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-EXCL-COMPILE-1", "role": "test",
        "objective": "verify retrieval_exclusions at the query loop and the D.2 both-ways call sites",
        "view": view_path,
        "required_inputs": [{"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"}],
        "seeds": [],
        "queries": [{"id": "q1", "text": "zzyzx quartz protocol", "k": 8}],
        "retrieval_exclusions": RETRIEVAL_EXCLUSIONS,
        "mutation_scope": ["tests/route/**"],
        "prohibitions": ["do not touch anything outside mutation_scope"],
        "required_checks": ["pytest tests/route/test_task_exclusions.py -q"],
        "completion_vocabulary": ["ANSWERED", "PARTIAL", "BLOCKED"],
        "budget_profile": "bounded-builder",
    }
    result = packetmod.compile_packet(task_spec, routes=_leaky_route_set(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    assert "LEAK-EXCLUDED" not in result["rendered"]
    assert "LEAK-INCLUDED" in result["rendered"], "the D.2 direction (EX-DIRECTION) must trigger both-ways templates"
    assert result["excluded_hits"] > 0
    notice = next(n for n in result["notices"] if n["type"] == "RETRIEVAL_EXCLUSIONS_APPLIED")
    assert notice["excluded_hits"] == result["excluded_hits"] > 0
    for items in result["sections"].values():
        assert not any((it.path or "") == "excluded/leaky" for it in items)


def test_compile_seed_code_route_excludes_real_code_hits(view_path, registry_path, fixture_repo):
    routes = _built_routes(fixture_repo, view_path, registry_path)
    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-EXCL-COMPILE-2", "role": "test",
        "objective": "verify the compiler's seed code route excludes real code hits (RC-8's first named site)",
        "view": view_path,
        "required_inputs": [],
        "seeds": ["EX-FIND-0001#F1"],
        "queries": [],
        "retrieval_exclusions": RETRIEVAL_EXCLUSIONS,
        "mutation_scope": ["tests/route/**"],
        "prohibitions": ["do not touch anything outside mutation_scope"],
        "required_checks": ["pytest tests/route/test_task_exclusions.py -q"],
        "completion_vocabulary": ["ANSWERED", "PARTIAL", "BLOCKED"],
        "budget_profile": "synthesis",
    }
    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    for letter, items in result["sections"].items():
        for it in items:
            assert it.path != repobuilder.EXCLUDED_CODE_PATH, (letter, it.unit_id, it.path)
            assert it.path != repobuilder.EXCLUDED_PROBE_PATH, (letter, it.unit_id, it.path)
    assert result["excluded_hits"] > 0


# ---------------------------------------------------------------------------------------------------------------
# govbridge.graph.why / govbridge.graph.history
# ---------------------------------------------------------------------------------------------------------------

def test_why_findings_stage_excludes_probes_mention(fixture_repo, view_path, registry_path):
    ctx = taskctxmod.TaskContext(source="t", retrieval_exclusions=tuple(RETRIEVAL_EXCLUSIONS))

    before = whymod.why("EX-SEED", repo=str(fixture_repo.root), view_path=view_path, registry_path=registry_path,
                         task=taskctxmod.EMPTY)
    assert before["stages"]["findings"]["status"] == "PRESENT", "sanity: the mention is found before exclusion"

    after = whymod.why("EX-SEED", repo=str(fixture_repo.root), view_path=view_path, registry_path=registry_path,
                        task=ctx)
    assert after["excluded_hits"] > 0
    assert after["stages"]["findings"]["status"].startswith("MISSING")
    assert not any(repobuilder.LEAK_MENTION_PATH in (h.get("evidence_occurrence") or "")
                   for stage in after["stages"].values() for h in stage["hops"])


def test_history_excludes_probes_mention_and_discloses_count(fixture_repo, view_path, registry_path):
    ctx = taskctxmod.TaskContext(source="t", retrieval_exclusions=tuple(RETRIEVAL_EXCLUSIONS))

    before = historymod.history("EX-SEED", repo=str(fixture_repo.root), view_path=view_path,
                                 registry_path=registry_path, task=taskctxmod.EMPTY)
    assert any(repobuilder.LEAK_MENTION_PATH in (e["edge"].get("evidence_occurrence") or "")
               for e in before["entries"] if e.get("edge")), "sanity"

    after = historymod.history("EX-SEED", repo=str(fixture_repo.root), view_path=view_path,
                                registry_path=registry_path, task=ctx)
    assert after["excluded_hits"] > 0
    assert not any(repobuilder.LEAK_MENTION_PATH in (e["edge"].get("evidence_occurrence") or "")
                   for e in after["entries"] if e.get("edge"))


# ---------------------------------------------------------------------------------------------------------------
# govbridge.graph.impact -- graph hops filtered generically; code hops honestly left alone (blob:line, no path)
# ---------------------------------------------------------------------------------------------------------------

def test_impact_filters_graph_hops_by_excluded_path(fixture_repo, view_path, monkeypatch):
    from govbridge.graph import edges as edgesmod

    def fake_bfs(conn, seeds, max_depth=2):
        return {
            "EX-OTHER": [edgesmod.Edge(src="EX-SEED", type="MENTIONS", dst="EX-OTHER", derivation="EXACT_ID",
                                        evidence_occurrence="excluded/other.md@deadbeef")],
            "EX-KEPT": [edgesmod.Edge(src="EX-SEED", type="MENTIONS", dst="EX-KEPT", derivation="EXACT_ID",
                                       evidence_occurrence="included/other.md@deadbeef")],
        }

    monkeypatch.setattr(impactmod.T, "bfs", fake_bfs)
    monkeypatch.setattr(impactmod.store, "open_db", lambda: object())
    monkeypatch.setattr(impactmod.code_bridge, "build_shaped_code_connection", lambda *_a, **_kw: None)

    ctx = taskctxmod.TaskContext(source="t", retrieval_exclusions=("excluded/**",))
    result = impactmod.impact("EX-SEED", repo=str(fixture_repo.root), view_path=view_path, task=ctx)
    assert result["excluded_hits"] == 1
    # the unit key can still appear (its edge list is simply empty once every edge to it is excluded -- the same
    # "every unit in graph_hops gets a key" shape the pre-existing dict comprehension already had); what must never
    # happen is the excluded EDGE surviving into it.
    assert result["graph"]["EX-OTHER"] == []
    assert len(result["graph"]["EX-KEPT"]) == 1


# ---------------------------------------------------------------------------------------------------------------
# govbridge.authority.state
# ---------------------------------------------------------------------------------------------------------------

def test_state_get_withholds_value_for_an_excluded_alias(fixture_repo, view_path, monkeypatch):
    monkeypatch.setitem(statemod.STATE_ALIASES, "ex-excluded-test", repobuilder.STATE_EXCLUDED_PATH)
    ctx = taskctxmod.TaskContext(source="t", retrieval_exclusions=("excluded/**",))

    result = statemod.get("ex-excluded-test", "value", repo=str(fixture_repo.root), view_path=view_path, task=ctx)
    assert result.excluded is True
    assert result.excluded_hits == 1
    assert result.value is None

    # the SAME alias, no task context, still returns the real value -- exclusion is opt-in, never a new default
    # failure mode for a caller that names no task at all.
    control = statemod.get("ex-excluded-test", "value", repo=str(fixture_repo.root), view_path=view_path,
                            task=taskctxmod.EMPTY)
    assert control.excluded is False
    assert control.value == 42


def test_state_get_unexcluded_alias_is_unaffected_by_an_unrelated_task_context(fixture_repo, view_path):
    ctx = taskctxmod.TaskContext(source="t", retrieval_exclusions=("excluded/**",))
    result = statemod.get("bridge", "running_work", repo=str(fixture_repo.root), view_path=view_path, task=ctx)
    assert result.excluded is False
    assert result.excluded_hits == 0
    assert result.value == {"status": "fixture value"}


# ---------------------------------------------------------------------------------------------------------------
# govbridge.core.exact
# ---------------------------------------------------------------------------------------------------------------

def test_exact_show_excludes_and_grep_id_lookup_disclose_counts(fixture_repo, view_path, registry_path):
    ctx = taskctxmod.TaskContext(source="t", retrieval_exclusions=tuple(RETRIEVAL_EXCLUSIONS))
    repo = str(fixture_repo.root)

    shown = exactmod.show(f"{fixture_repo.commit}:{repobuilder.EXCLUDED_CODE_PATH}", view_path=view_path,
                           rules_path=str(fixture_repo.root / "config" / "corpus-rules.yaml"), repo=repo, task=ctx)
    assert shown["excluded"] is True
    assert shown["excluded_hits"] == 1
    assert "text" not in shown

    grepped = exactmod.grep("ex_target_fn", ref="main", view_path=view_path,
                             rules_path=str(fixture_repo.root / "config" / "corpus-rules.yaml"), repo=repo, task=ctx)
    assert grepped["hits"] == []
    assert grepped["excluded_hits"] >= 1

    looked_up = exactmod.id_lookup("ex_target_fn", ref="main", view_path=view_path, repo=repo, task=ctx)
    assert looked_up["mention_sites"] == []
    assert looked_up["excluded_hits"] >= 1


def test_exact_show_unexcluded_path_is_unaffected():
    ctx = taskctxmod.TaskContext(source="t", retrieval_exclusions=("excluded/**",))
    assert ctx.is_excluded("included/topic-echo.md") is False
