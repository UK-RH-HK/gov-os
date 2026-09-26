"""BR-DAG-AMEND-R1-17 reopening (items 5 and 6): "BR-DAG-AMEND-R1-15 covers every query command, not only gather."

Two scenarios, each over a small fixture repo (one lexical decision record, one Rust module with a function and a
caller, one authority registry), for EVERY query command that can reach the code route/layer -- ``why``, ``impact``,
``history``, ``compile``, ``gather`` (every route active), and ``govbridge.code.symbols``'s own ``callers``/
``definitions``:

(a) a store built from clean (every layer, including code) then made genuinely read-only at the FILE level AND its
    DIRECTORY level (chmod'd 0o444/0o555): each command SUCCEEDS, and the store file's sha256 is byte-identical
    before and after every one of them.
(b) a store built from clean WITHOUT the code layer (the canonical view's own refs declare an explicit ``layers``
    list that omits "code" -- ``govbridge.code.build.eager_ref_names``' own generic admission rule, never a
    special-cased ref name), then ALSO made file+directory read-only: ``impact``, ``compile``, ``gather`` (seeded
    so its code facet actually runs) and ``govbridge.code.symbols.callers``/``definitions`` each raise the typed
    :class:`govbridge.code.symbols.StoreNeedsRebuild`, and the store file's sha256 stays unchanged even in this
    failure path. ``why``/``history`` never touch the code layer at all (confirmed by inspection: neither imports
    ``govbridge.code``/``govbridge.graph.code_bridge``), so they succeed in both scenarios, unaffected either way.

    ``compile``'s own two record-citation-derivation call sites (``govbridge.compile.packet.Compiler.
    code_seeds_for``/``.code_conn``, out of this node's mutation scope) DO still swallow ``StoreNeedsRebuild``
    internally -- a pre-existing "honest MISSING, never an error" contract for deriving EXTRA code seeds from a
    record's own citations, which must not break the whole seed pass. That is not what makes ``compile`` raise
    here: ``compile_packet``'s own MAIN per-seed code-route call (``c.routes.run("code", seeds=seed_names, ...)``,
    unconditional for every seed, never wrapped in any try/except at all in ``packet.py``) is what propagates it,
    confirmed empirically (not by inspection alone -- see ``test_compile_raises_...`` below) rather than assumed
    from ``code_seeds_for``'s own separate, still-swallowing behaviour.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

import pytest

from govbridge.authority.classes import BRIDGE_STATE_PATH
from govbridge.code import symbols as codesymbols
from govbridge.core import freshness, store as storemod
from govbridge.route import real_routes


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))


DECISION_PATH = "spec/decisions/D-QCR-0001.yaml"
CODE_PATH = "runtime/src/qcr.rs"


def _build_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")

    (root / "spec" / "decisions").mkdir(parents=True)
    (root / DECISION_PATH).write_text(
        "id: D-QCR-0001\nstatus: ACTIVE\ntitle: a fixture decision about query command read-only behaviour\n",
        encoding="utf-8",
    )
    (root / "runtime" / "src").mkdir(parents=True)
    (root / CODE_PATH).write_text(
        "pub fn qcr_target_fn() -> bool {\n    true\n}\n\n"
        "fn qcr_caller_fn() -> bool {\n    qcr_target_fn()\n}\n",
        encoding="utf-8",
    )

    state_path = root / BRIDGE_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "schema: bridge-orchestrator-state/1\n"
        "mandatory_bridge_inputs:\n  authority_classes: {}\n  items: []\n",
        encoding="utf-8",
    )

    (root / "config").mkdir(parents=True, exist_ok=True)
    (root / "config" / "corpus-rules.yaml").write_text(
        "schema: govbridge-corpus-rules/1\nrules:\n  - {id: INCLUDED, effect: INCLUDE, match: {}}\n",
        encoding="utf-8",
    )

    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c1")
    _git(root, "branch", "-f", "product", "HEAD")
    return root


def _write_registry(tmp_path: Path) -> str:
    registry_path = tmp_path / "authority-registry.yaml"
    registry_path.write_text(
        "schema: govbridge-authority-registry/1\n"
        "class_rules:\n"
        "  - {glob: 'spec/decisions/*.yaml', class: ARCHITECTURE_DECISION}\n"
        "  - {glob: 'runtime/**', class: EVIDENCE}\n"
        "  - {glob: '**', class: UNCLASSIFIED}\n",
        encoding="utf-8",
    )
    return str(registry_path)


def _write_view(tmp_path: Path, include_code_layer: bool) -> str:
    """``include_code_layer=False`` gives every ref an explicit ``layers`` list that omits "code" -- the same
    generic admission rule ``govbridge.code.build.eager_ref_names`` already reads (an explicit list, or role !=
    history when omitted), never a special-cased ref name -- so the code_layer_builder runs (ensuring its own
    schema, per its own unconditional ``codestore.ensure_schema`` call) but reaches zero refs, indexing nothing."""
    view_path = tmp_path / "canonical-view.yaml"
    layers = "" if include_code_layer else "\n    layers: [lexical, semantic, exact]"
    view_path.write_text(
        "schema: govbridge-canonical-view/1\n"
        "view_id: qcr-test-view\n"
        "refs:\n"
        f"  - name: records\n    ref: refs/heads/main\n    follow: tip\n    role: primary{layers}\n"
        f"  - name: product\n    ref: refs/heads/product\n    follow: tip\n    role: product{layers}\n"
        "partitions:\n"
        "  - {name: catchall, paths: ['**'], owner: records, fallback: [product]}\n",
        encoding="utf-8",
    )
    return str(view_path)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _task_spec(view_path: str) -> dict:
    return {
        "schema": "govbridge-task-spec/1", "task_id": "T-QCR-1", "role": "test",
        "objective": "compile a packet exercising the code route, for the R1-XC read-only query-commands test",
        "view": view_path,
        "required_inputs": [],
        "seeds": ["qcr_target_fn"],
        "queries": [{"id": "q1", "text": "fixture decision about query command", "routes": ["lexical"]}],
        "mutation_scope": ["tests/route/**"],
        "prohibitions": ["do not touch anything outside mutation_scope"],
        "required_checks": ["pytest tests/route -q"],
        "completion_vocabulary": ["ANSWERED", "PARTIAL", "BLOCKED"],
        "budget_profile": "synthesis",
    }


def _all_route_facets(tmp_path: Path) -> str:
    p = tmp_path / "all-route-facets.yaml"
    p.write_text(
        "schema: govbridge-facets/1\n"
        "purpose: minimal all-route facet registry for the R1-XC query-commands read-only reopening test\n"
        "default_batch_size: 8\n"
        "default_max_rounds: 5\n"
        "default_threads: 1\n"
        "default_target_items: 8\n"
        "facets:\n"
        "  impl:\n"
        "    routes: [code]\n"
        "    extra_terms: []\n"
        "    min_share: 0.05\n"
        "class_facets: {}\n",
        encoding="utf-8",
    )
    return str(p)


def test_every_query_command_succeeds_against_a_file_and_directory_read_only_store(tmp_path, monkeypatch):
    """Scenario (a): a fully-built store (every layer, including code), then chmod'd 0o444/0o555. Every command
    that can reach the code route succeeds, and none of them writes a single byte to the store file."""
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)  # the real, shared model cache (module docstring)

    repo_root = _build_repo(tmp_path)
    view_path = _write_view(tmp_path, include_code_layer=True)
    registry_path = _write_registry(tmp_path)
    rules_path = str(repo_root / "config" / "corpus-rules.yaml")

    r = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)
    assert r["trigger"] == "FULL"

    store_dir = storemod.store_root()
    db_path = storemod.db_path(store_dir)
    before_sha = _sha256_file(db_path)

    os.chmod(db_path, 0o444)
    os.chmod(store_dir, 0o555)
    try:
        from govbridge.compile import packet as packetmod
        from govbridge.gather import engine as enginemod
        from govbridge.graph import history as historymod
        from govbridge.graph import impact as impactmod
        from govbridge.graph import why as whymod

        why_result = whymod.why("D-QCR-0001", repo=str(repo_root), view_path=view_path, registry_path=registry_path)
        assert why_result is not None

        impact_result = impactmod.impact("qcr_target_fn", repo=str(repo_root), view_path=view_path)
        assert impact_result is not None

        history_result = historymod.history("D-QCR-0001", repo=str(repo_root), view_path=view_path,
                                             registry_path=registry_path)
        assert history_result is not None

        routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
        compile_result = packetmod.compile_packet(_task_spec(view_path), routes=routes, repo=str(repo_root),
                                                   registry_path=registry_path)
        assert compile_result["status"] == packetmod.STATUS_OK

        gather_query = {"id": "Q1", "text": "qcr_target_fn", "class": None, "subject": None, "facets": ["impl"]}
        gather_result = enginemod.gather(gather_query, routes, seeds=["qcr_target_fn"], batch_size=8, max_rounds=5,
                                          threads=1, facets_path=_all_route_facets(tmp_path))
        assert gather_result["stop_reason"] in enginemod.STOP_REASONS
        code_hits = [h for h in gather_result["merged"] if h["route"] == "code"]
        assert code_hits, "the code facet found nothing at all -- this proves nothing about the read-only path"

        callers_result = codesymbols.callers("qcr_target_fn", "product", repo=str(repo_root))
        assert callers_result["callers"]

        definitions_result = codesymbols.definitions("qcr_target_fn", "product", repo=str(repo_root))
        assert definitions_result["definitions"]
    finally:
        os.chmod(store_dir, 0o755)
        os.chmod(db_path, 0o644)

    after_sha = _sha256_file(db_path)
    assert after_sha == before_sha, "a query command wrote to the store file"


def test_code_dependent_commands_raise_store_needs_rebuild_when_the_code_layer_is_missing(tmp_path, monkeypatch):
    """Scenario (b): a store built from clean WITHOUT the code layer (every ref's own ``layers`` list omits
    "code"), then ALSO chmod'd 0o444/0o555. impact/gather(code)/callers/definitions each raise the typed
    StoreNeedsRebuild -- never a silent empty result, never a write."""
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)

    repo_root = _build_repo(tmp_path)
    view_path = _write_view(tmp_path, include_code_layer=False)
    registry_path = _write_registry(tmp_path)
    rules_path = str(repo_root / "config" / "corpus-rules.yaml")

    r = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)
    assert r["trigger"] == "FULL"

    store_dir = storemod.store_root()
    db_path = storemod.db_path(store_dir)
    before_sha = _sha256_file(db_path)

    os.chmod(db_path, 0o444)
    os.chmod(store_dir, 0o555)
    try:
        from govbridge.compile import packet as packetmod
        from govbridge.gather import engine as enginemod
        from govbridge.graph import impact as impactmod

        with pytest.raises(codesymbols.StoreNeedsRebuild):
            impactmod.impact("qcr_target_fn", repo=str(repo_root), view_path=view_path)

        routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)

        with pytest.raises(codesymbols.StoreNeedsRebuild):
            packetmod.compile_packet(_task_spec(view_path), routes=routes, repo=str(repo_root),
                                      registry_path=registry_path)

        gather_query = {"id": "Q1", "text": "qcr_target_fn", "class": None, "subject": None, "facets": ["impl"]}
        with pytest.raises(codesymbols.StoreNeedsRebuild):
            enginemod.gather(gather_query, routes, seeds=["qcr_target_fn"], batch_size=8, max_rounds=5, threads=1,
                              facets_path=_all_route_facets(tmp_path))

        with pytest.raises(codesymbols.StoreNeedsRebuild):
            codesymbols.callers("qcr_target_fn", "product", repo=str(repo_root))

        with pytest.raises(codesymbols.StoreNeedsRebuild):
            codesymbols.definitions("qcr_target_fn", "product", repo=str(repo_root))
    finally:
        os.chmod(store_dir, 0o755)
        os.chmod(db_path, 0o644)

    after_sha = _sha256_file(db_path)
    assert after_sha == before_sha, "a raising query command still wrote to the store file"


def test_why_and_history_never_touch_the_code_layer_at_all(tmp_path, monkeypatch):
    """why()/history() succeed identically whether or not the code layer was ever built -- confirmed here (not
    just by inspection): neither one raises StoreNeedsRebuild, since neither ever calls into
    govbridge.code/govbridge.graph.code_bridge in the first place."""
    monkeypatch.delenv("GOV_BRIDGE_HOME", raising=False)

    repo_root = _build_repo(tmp_path)
    view_path = _write_view(tmp_path, include_code_layer=False)
    registry_path = _write_registry(tmp_path)
    rules_path = str(repo_root / "config" / "corpus-rules.yaml")
    freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)

    from govbridge.graph import history as historymod
    from govbridge.graph import why as whymod

    why_result = whymod.why("D-QCR-0001", repo=str(repo_root), view_path=view_path, registry_path=registry_path)
    assert why_result is not None
    history_result = historymod.history("D-QCR-0001", repo=str(repo_root), view_path=view_path,
                                         registry_path=registry_path)
    assert history_result is not None


def test_compile_raises_store_needs_rebuild_when_the_code_layer_is_missing(tmp_path, monkeypatch):
    """compile_packet's own MAIN per-seed code-route call (``c.routes.run("code", seeds=seed_names, ...)``,
    unconditional for every task-spec seed, never wrapped in any try/except in govbridge/compile/packet.py) raises
    StoreNeedsRebuild through the SAME route code_route's own re-raise (open issue 2) puts in place -- confirmed
    directly here, on a normal (writable) store, isolating this from the file+directory read-only scenario the
    other tests in this module already cover. compile's SEPARATE record-citation derivation
    (Compiler.code_seeds_for/.code_conn) still swallows the same error internally for ITS OWN, different purpose
    (deriving EXTRA seeds from a record's citations) -- that swallow does not prevent this one, unwrapped call
    from raising."""
    repo_root = _build_repo(tmp_path)
    view_path = _write_view(tmp_path, include_code_layer=False)
    registry_path = _write_registry(tmp_path)
    rules_path = str(repo_root / "config" / "corpus-rules.yaml")
    freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)

    from govbridge.compile import packet as packetmod

    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    with pytest.raises(codesymbols.StoreNeedsRebuild):
        packetmod.compile_packet(_task_spec(view_path), routes=routes, repo=str(repo_root),
                                  registry_path=registry_path)
