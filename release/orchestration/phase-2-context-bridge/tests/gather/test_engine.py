"""``govbridge.gather.engine`` (REPAIR_DAG.yaml node R1-GA1). Unit tests use a hermetic ``FakeRouteSet`` (fast, no
store/subprocess); the real-view tests build a tiny, synthetic Git fixture (``tests/fixtures/gather/
gather_repobuilder.py``) spanning five top-level directories, through the REAL lexical route
(``govbridge.route.real_routes``), and use ``tests/fixtures/gather/test-facets.yaml`` (a lexical-only registry) so
they never spawn the embedding subprocess. Neither uses a public demonstration query text or a run-1 answer
(REPAIR-1 rule 2), and nothing here names a Review-8 item, an F-finding or a query-class id (OC-BR-02).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from govbridge.core import taskctx as taskctxmod
from govbridge.gather import engine as enginemod
from govbridge.gather import facets as facetsmod

FIXTURES_GATHER = Path(__file__).resolve().parents[1] / "fixtures" / "gather"
sys.path.insert(0, str(FIXTURES_GATHER))
import gather_repobuilder as repobuilder  # noqa: E402
from fake_routes import FakeRouteSet, make_hit  # noqa: E402

TEST_FACETS_PATH = str(FIXTURES_GATHER / "test-facets.yaml")


@pytest.fixture(autouse=True)
def _isolated_gather_env(tmp_path, monkeypatch):
    """R1-T1: hermetic (no GOVBRIDGE_* leaked from another test, no process-cwd dependency). Defined here rather
    than in a package ``conftest.py`` so this node's changes stay exactly inside its declared mutation_scope
    (``tests/gather/test_engine.py``, ``tests/gather/test_instantiate.py``, ``tests/fixtures/gather/**``); this
    file is the only one of the two that needs store/env isolation at all (test_instantiate.py runs entirely over
    in-memory dicts)."""
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))
    facetsmod.clear_cache()
    taskctxmod.reset()
    yield
    taskctxmod.reset()
    facetsmod.clear_cache()


def _query(text="gizmoflux", id_="Q1", facets=None):
    q = {"id": id_, "text": text, "class": None, "subject": None}
    if facets is not None:
        q["facets"] = facets
    return q


# --- fixed stopping-reason vocabulary (REPAIR_DAG.yaml acceptance check 1) --------------------------------------

def test_stop_reason_is_always_one_of_the_fixed_vocabulary():
    assert enginemod.STOP_REASONS == (
        "FACETS_COVERED", "NO_UNRESOLVED_IDENTIFIERS", "MARGINAL_GAIN_ONLY_DUPLICATES", "MAX_ROUNDS",
        "BUDGET_REACHED_WITH_UNRESOLVED",
    )
    assert "top-k returned" not in enginemod.STOP_REASONS  # OD-BR-05 section 5: never a stopping reason


def test_facets_covered_when_every_facet_gets_at_least_one_item():
    routes = FakeRouteSet(lexical=[make_hit("U1", "a/x.md"), make_hit("U2", "b/y.md")])
    result = enginemod.gather(_query(facets=["purpose"]), routes, batch_size=8, threads=1)
    assert result["stop_reason"] == "FACETS_COVERED"
    assert result["telemetry"]["unresolved_facets"] == []


def test_max_rounds_stop_reason():
    # 20 lexical items, batch_size=1, max_rounds=2: after 2 rounds only 2 of 20 are gathered -- neither exhausted
    # nor at target (default target_items=16), so MAX_ROUNDS fires with the facet still unresolved.
    items = [make_hit(f"U{i}", f"dir{i}/f.md") for i in range(20)]
    routes = FakeRouteSet(lexical=items)
    result = enginemod.gather(_query(facets=["purpose"]), routes, batch_size=1, max_rounds=2, threads=1)
    assert result["stop_reason"] == "MAX_ROUNDS"
    assert "purpose" in result["telemetry"]["unresolved_facets"]


def test_marginal_gain_only_duplicates_when_a_route_keeps_returning_the_same_item():
    """A route that always claims there is another page (``next_offset`` keeps advancing) but always re-serves the
    SAME already-seen item: real progress (raw_seen growing) stops immediately, so MARGINAL_GAIN_ONLY_DUPLICATES
    must fire at the next round rather than looping until max_rounds."""
    class _StuckRoutes:
        def run(self, name, **kwargs):
            if name != "lexical":
                return []
            offset = kwargs.get("offset", 0) or 0
            info = kwargs.get("page_info_out")
            if info is not None:
                info["next_offset"] = offset + 1  # always "more to come" -- never signals exhaustion
            return [make_hit("SAME", "a/x.md")]  # but the SAME item every time, regardless of offset

    result = enginemod.gather(_query(facets=["purpose"]), _StuckRoutes(), batch_size=1, max_rounds=50, threads=1)
    assert result["stop_reason"] == "MARGINAL_GAIN_ONLY_DUPLICATES"
    assert len(result["merged"]) == 1


def test_budget_reached_with_unresolved_stop_reason(tmp_path):
    budgets_path = tmp_path / "budgets.yaml"
    budgets_path.write_text(
        "schema: govbridge-budgets/1\n"
        "profiles: {}\n"
        "gather: {max_items_per_query: 3}\n",
        encoding="utf-8",
    )
    items = [make_hit(f"U{i}", f"dir{i}/f.md") for i in range(20)]
    routes = FakeRouteSet(lexical=items)
    result = enginemod.gather(_query(facets=["purpose"]), routes, batch_size=2, max_rounds=50, threads=1,
                               budgets_path=str(budgets_path))
    assert result["stop_reason"] == "BUDGET_REACHED_WITH_UNRESOLVED"
    assert len(result["merged"]) >= 3


def test_no_unresolved_identifiers_for_an_explicit_empty_facet_override():
    routes = FakeRouteSet(lexical=[make_hit("U1", "a/x.md")])
    result = enginemod.gather(_query(facets=[]), routes, batch_size=8, threads=1)
    assert result["stop_reason"] == "NO_UNRESOLVED_IDENTIFIERS"
    assert result["merged"] == []
    assert result["facets"] == []


def test_versions_facet_is_always_reported_missing_never_silently_dropped():
    routes = FakeRouteSet(lexical=[make_hit("U1", "a/x.md")])
    result = enginemod.gather(_query(facets=["purpose", "versions"]), routes, batch_size=8, threads=1)
    versions_rows = [r for r in result["telemetry"]["per_round"] if r["facet"] == "versions"]
    assert len(versions_rows) == 1
    assert versions_rows[0]["missing"] is True
    assert "R1-GA2" in versions_rows[0]["missing_reason"] or "reconciliation" in versions_rows[0]["missing_reason"]


def test_scope_filtering_drops_out_of_scope_hits_and_pages_past_them():
    # 3 UNCLASSIFIED (out of scope for a CONTRACT-scoped facet) + 1 CONTRACT item, all in one lexical stream.
    items = [
        make_hit("U1", "a/x.md", authority_class="UNCLASSIFIED"),
        make_hit("U2", "b/y.md", authority_class="UNCLASSIFIED"),
        make_hit("U3", "c/z.md", authority_class="UNCLASSIFIED"),
        make_hit("U4", "d/w.md", authority_class="CONTRACT"),
    ]
    routes = FakeRouteSet(lexical=items)
    result = enginemod.gather(_query(facets=["requirement"]), routes, batch_size=1, max_rounds=20, threads=1)
    assert len(result["merged"]) == 1
    assert result["merged"][0]["unit_id"] == "U4"
    assert result["telemetry"]["rounds"] > 1  # had to page past 3 out-of-scope pages first


def test_identifier_extractor_hook_is_called_and_disclosed_never_acted_on():
    seen = []

    def extractor(hits):
        seen.append(list(hits))
        return ["SOME-ID"]

    routes = FakeRouteSet(lexical=[make_hit("U1", "a/x.md")])
    result = enginemod.gather(_query(facets=["purpose"]), routes, batch_size=8, threads=1,
                               identifier_extractor=extractor)
    assert seen  # the hook ran
    assert result["telemetry"]["unresolved_identifiers"] == ["SOME-ID"]  # disclosed
    # R1-GA1 never chases it: the facet was already satisfied by its own single item, and no new facet/round
    # appears just because the extractor returned something.
    assert result["stop_reason"] == "FACETS_COVERED"


def test_excluded_hits_are_disclosed_and_task_exclusions_are_honoured():
    items = [make_hit("U1", "excluded/x.md"), make_hit("U2", "included/y.md")]
    routes = FakeRouteSet(lexical=items)
    task = taskctxmod.TaskContext(source="test", retrieval_exclusions=("excluded/**",))
    # FakeRouteSet does not itself honour exclude= (it is a route stub, not the real adapter under test elsewhere --
    # tests/route/test_task_exclusions.py covers that); this asserts gather THREADS the merged exclude list and the
    # counter through to whatever routes.run() receives, which real_routes.py's own adapters then act on.
    result = enginemod.gather(_query(facets=["purpose"]), routes, task=task, batch_size=8, threads=1)
    lexical_calls = [kw for (name, kw) in routes.calls if name == "lexical"]
    assert lexical_calls and lexical_calls[0]["exclude"] == ["excluded/**"]
    assert "excluded_hits" in result


# --- deterministic merge across thread counts (REPAIR_DAG.yaml acceptance check 2) -------------------------------

def test_merge_is_byte_identical_across_thread_counts():
    lexical_items = [make_hit(f"L{i}", f"lex/{i}.md") for i in range(6)]
    code_items = [make_hit(f"C{i}", f"code/{i}.rs", route="code") for i in range(3)]
    results = {}
    for threads in (1, 4, 16):
        routes = FakeRouteSet(lexical=lexical_items, code=code_items)
        results[threads] = enginemod.gather(
            _query(facets=["purpose", "requirement", "dependencies", "dependents", "enforcement", "tests",
                            "evidence_staleness", "failed_approaches", "decisions_active", "decisions_history"]),
            routes, batch_size=8, threads=threads,
        )
    shas = {r["merged_sha256"] for r in results.values()}
    assert len(shas) == 1, f"merged_sha256 differs across thread counts: { {t: r['merged_sha256'] for t, r in results.items()} }"
    counts = {t: len(r["merged"]) for t, r in results.items()}
    assert len(set(counts.values())) == 1, counts


def test_batch_size_changes_round_count_not_the_final_evidence_set():
    lexical_items = [make_hit(f"L{i}", f"lex/{i}.md") for i in range(10)]
    small = enginemod.gather(_query(facets=["purpose"]), FakeRouteSet(lexical=lexical_items), batch_size=1,
                              max_rounds=50, threads=1)
    large = enginemod.gather(_query(facets=["purpose"]), FakeRouteSet(lexical=lexical_items), batch_size=16,
                              max_rounds=50, threads=1)
    assert small["telemetry"]["rounds"] > large["telemetry"]["rounds"]
    small_ids = sorted(h["unit_id"] for h in small["merged"])
    large_ids = sorted(h["unit_id"] for h in large["merged"])
    assert small_ids == large_ids == [f"L{i}" for i in range(10)]


# --- real view: a fixture subject spanning 5 directories, exceeding one batch (acceptance check 1) --------------

@pytest.fixture
def built_repo(tmp_path):
    from govbridge.core import freshness
    br = repobuilder.build(tmp_path)
    r = freshness.run(view_path=br.view_path, rules_path=br.rules_path, repo=str(br.root), from_clean=True)
    assert r["trigger"] == "FULL"
    return br


def test_five_directory_subject_needs_more_than_one_round_on_the_real_lexical_route(built_repo):
    from govbridge.route import real_routes

    routes = real_routes.build_real_routes(view_path=built_repo.view_path, repo=str(built_repo.root),
                                            registry_path=built_repo.registry_path)
    result = enginemod.gather(_query(text=repobuilder.TERM, facets=["purpose"]), routes, batch_size=2,
                               max_rounds=20, threads=1, facets_path=TEST_FACETS_PATH)
    assert result["telemetry"]["rounds"] > 1
    dirs = {h["occurrences"][0]["path"].split("/")[0] for h in result["merged"]}
    assert len(dirs) >= 5, dirs
    assert result["stop_reason"] in enginemod.STOP_REASONS


def test_requirement_facet_pages_past_out_of_scope_hits_to_find_the_one_contract_item(built_repo):
    from govbridge.route import real_routes

    routes = real_routes.build_real_routes(view_path=built_repo.view_path, repo=str(built_repo.root),
                                            registry_path=built_repo.registry_path)
    result = enginemod.gather(_query(text=repobuilder.TERM, facets=["requirement"]), routes, batch_size=2,
                               max_rounds=20, threads=1, facets_path=TEST_FACETS_PATH)
    assert len(result["merged"]) == 1
    assert result["merged"][0]["occurrences"][0]["path"] == repobuilder.CONTRACT_PATH
    assert result["telemetry"]["rounds"] > 1


def test_real_view_thread_determinism(built_repo):
    from govbridge.route import real_routes

    shas = set()
    for threads in (1, 4):
        routes = real_routes.build_real_routes(view_path=built_repo.view_path, repo=str(built_repo.root),
                                                registry_path=built_repo.registry_path)
        result = enginemod.gather(_query(text=repobuilder.TERM, facets=["purpose", "requirement"]), routes,
                                   batch_size=2, max_rounds=20, threads=threads, facets_path=TEST_FACETS_PATH)
        shas.add(result["merged_sha256"])
    assert len(shas) == 1


# --- the top-level `govbridge notes ...` dispatch line (routed from R1-RN/BR-AR-0017 to this node) --------------
#
# govbridge/cli.py is this node's own mutation_scope (shared-file sequence RX -> GA1 -> RS -> RA), and the ONE
# dispatch line it adds for "notes" belongs to R1-RN, whose own mutation_scope did not include cli.py
# (govbridge/notes/cli.py's own module docstring names this hand-off explicitly). tests/notes/test_cli.py is R1-RN's
# test file, outside this node's declared mutation_scope, so these dispatch tests live here instead, exercising
# govbridge.cli directly rather than editing that file.

def test_govbridge_notes_help_dispatches_to_notes_cli_in_process(capsys):
    """"``govbridge notes --help`` dispatches": ``--help`` is not a subcommand ``govbridge.notes.cli.main`` itself
    recognises (it has no argparse-based top level of its own -- its module docstring), so it falls through to that
    module's OWN "unknown subcommand" message -- proving the top-level dispatch line actually forwarded ``rest``
    into ``notescli.main(["--help"])`` rather than the top-level dispatcher itself reporting "unknown command
    'notes'" (its own, different message, for a command it does not recognise at all)."""
    from govbridge import cli as climod

    rc = climod.main(["notes", "--help"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "govbridge notes: unknown subcommand '--help'" in err
    assert "unknown command 'notes'" not in err


def test_govbridge_notes_help_dispatches_via_python_dash_m():
    """The same dispatch, exercised as a real subprocess (``python -m govbridge notes --help``), proving
    ``govbridge/__main__.py`` -> ``govbridge.cli.main`` -> ``notes`` reaches ``govbridge.notes.cli`` outside the
    test process too, and that ``govbridge notes validate``/``build`` (already covered by tests/notes/test_cli.py's
    own direct ``notescli.main`` calls) are reachable the same way."""
    from govbridge import GOV_BRIDGE_DOMAIN

    proc = subprocess.run(
        [sys.executable, "-m", "govbridge", "notes", "--help"], cwd=GOV_BRIDGE_DOMAIN, capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert "govbridge notes: unknown subcommand '--help'" in proc.stderr
