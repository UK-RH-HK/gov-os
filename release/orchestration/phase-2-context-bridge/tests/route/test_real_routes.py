"""``govbridge.route.real_routes`` (B6 open issue "the real B2/B3/B4 routes are not wired", closed by
I1/BR-AR-0009): the adapters translating the real lexical/semantic/code/exact routes into
``govbridge.route.router.RouteHit``, with REAL authority classification wired in (B4/BR-AR-0006 OI-3). A small,
self-contained fixture repo (never Review-8/Phase-2 content -- OC-BR-02): one YAML decision record and one Rust
function, classified through a minimal, purpose-built registry (``class_rules`` only -- distinct from every other
node's fixture registry, so this test never depends on their section_anchors verifying against THIS repo)."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from govbridge.authority.classes import BRIDGE_STATE_PATH
from govbridge.core import freshness
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


def _build_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")

    (root / "spec" / "decisions").mkdir(parents=True)
    (root / "spec" / "decisions" / "D-0001.yaml").write_text(
        "id: D-0001\nstatus: ACTIVE\ntitle: a fixture decision about routing adapters\n", encoding="utf-8"
    )
    (root / "runtime" / "src").mkdir(parents=True)
    (root / "runtime" / "src" / "mod.rs").write_text("pub fn example_route_fn() {}\n", encoding="utf-8")

    state_path = root / BRIDGE_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "schema: bridge-orchestrator-state/1\n"
        "mandatory_bridge_inputs:\n  authority_classes: {}\n  items: []\n",
        encoding="utf-8",
    )

    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c1")
    _git(root, "branch", "-f", "product", "HEAD")
    return root


def _write_configs(tmp_path: Path) -> tuple:
    view_path = tmp_path / "canonical-view.yaml"
    view_path.write_text(
        "schema: govbridge-canonical-view/1\n"
        "view_id: rt-test-view\n"
        "refs:\n"
        "  - {name: records, ref: refs/heads/main, follow: tip, role: primary}\n"
        "  - {name: product, ref: refs/heads/product, follow: tip, role: product}\n"
        "partitions:\n"
        "  - {name: catchall, paths: ['**'], owner: records, fallback: [product]}\n",
        encoding="utf-8",
    )
    rules_path = tmp_path / "corpus-rules.yaml"
    rules_path.write_text(
        "schema: govbridge-corpus-rules/1\n"
        "rules:\n"
        "  - {id: INCLUDED, effect: INCLUDE, match: {}}\n",
        encoding="utf-8",
    )
    registry_path = tmp_path / "authority-registry.yaml"
    registry_path.write_text(
        "schema: govbridge-authority-registry/1\n"
        "class_rules:\n"
        "  - {glob: 'spec/decisions/*.yaml', class: ARCHITECTURE_DECISION}\n"
        "  - {glob: 'runtime/**', class: EVIDENCE}\n"
        "  - {glob: '**', class: UNCLASSIFIED}\n",
        encoding="utf-8",
    )
    return str(view_path), str(rules_path), str(registry_path)


def test_lexical_route_hits_carry_real_classification(tmp_path):
    repo_root = _build_repo(tmp_path)
    view_path, rules_path, registry_path = _write_configs(tmp_path)

    r = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)
    assert r["trigger"] == "FULL"

    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    hits = routes.lexical(text='"fixture decision"', k=5)
    assert hits
    assert any(h.authority_class == "ARCHITECTURE_DECISION" for h in hits), [h.authority_class for h in hits]
    assert all(h.lifecycle is not None for h in hits)
    assert all(h.delivery == "RETRIEVED" for h in hits)


def test_code_route_hits_carry_real_classification_and_real_definitions(tmp_path):
    repo_root = _build_repo(tmp_path)
    view_path, rules_path, registry_path = _write_configs(tmp_path)

    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    hits = routes.code(seeds=["example_route_fn"])
    assert hits
    definition_hits = [h for h in hits if h.unit_kind == "symbol"]
    assert definition_hits
    assert definition_hits[0].authority_class == "EVIDENCE"
    assert definition_hits[0].occurrences[0].path == "runtime/src/mod.rs"
    assert definition_hits[0].delivery == "RETRIEVED"


def test_exact_route_hits_carry_real_classification(tmp_path):
    repo_root = _build_repo(tmp_path)
    view_path, rules_path, registry_path = _write_configs(tmp_path)

    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    hits = routes.exact(text="example_route_fn")
    assert hits
    assert any(h.authority_class == "EVIDENCE" for h in hits), [h.authority_class for h in hits]


def test_safe_fts_query_never_raises_on_punctuated_free_text():
    from govbridge.route.real_routes import _safe_fts_query

    assert _safe_fts_query("consumers, dependents and uses of F1-DIRECTION") == (
        '"consumers" OR "dependents" OR "and" OR "uses" OR "of" OR "F1" OR "DIRECTION"'
    )
    assert _safe_fts_query('"already_quoted_phrase"') == '"already_quoted_phrase"'
    assert _safe_fts_query("") == '""'
    assert _safe_fts_query(None) == '""'


def test_lexical_route_survives_a_comma_bearing_free_text_query(tmp_path):
    repo_root = _build_repo(tmp_path)
    view_path, rules_path, registry_path = _write_configs(tmp_path)
    from govbridge.core import freshness
    freshness.run(view_path=view_path, rules_path=rules_path, repo=str(repo_root), from_clean=True)

    routes = real_routes.build_real_routes(view_path=view_path, repo=str(repo_root), registry_path=registry_path)
    # this exact shape (a comma in free text) is what ARCHITECTURE.md section 7.3's "evidence both ways" query
    # templates produce, and what broke fts5 before _safe_fts_query existed.
    hits = routes.lexical(text="consumers, dependents and uses of example_route_fn", k=5)
    assert isinstance(hits, list)  # must not raise
