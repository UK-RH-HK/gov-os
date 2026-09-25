"""``govbridge.core.view.classify_occurrence``'s ``CANONICAL_FALLBACK`` branch (B1 open issue OI-6, routed to
I1/BR-AR-0009: "CANONICAL_FALLBACK has no fixture test" -- B1's own shared fixture repo's linear history made a
clean "absent at the owner, present at a named non-history fallback" case awkward to construct without a second
root; this is that fixture, self-contained, so tests/fixtures/core/repobuilder.py (shared by many other tests)
stays untouched). New test file; no existing test is modified.

Shape: a "product" partition owned by a ref pinned at c1; a path that does NOT exist at c1 but DOES exist at c2,
where c2 is exactly what the "evidence" ref (product's first fallback) is pinned to. Querying that path AT c2
(evidence's own pinned commit) must classify CANONICAL_FALLBACK: absent at the owner, present at a named,
non-history fallback ref, queried at that fallback's own commit (never SAME_AS_CANONICAL/HISTORICAL_VERSION,
which both require a queried commit that is NOT the fallback's own -- and never HISTORY_ONLY, which is reserved
for a path found only through the history glob)."""
from __future__ import annotations

import subprocess
from pathlib import Path

from govbridge.core import view as viewmod


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def _build_repo(root: Path) -> tuple:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q", "-b", "records")
    (root / "runtime").mkdir()
    (root / "runtime" / "a.rs").write_text("fn a() {}\n", encoding="utf-8")
    c1 = _commit(root, "c1: product partition seed")
    _git(root, "branch", "product")  # pinned at c1 -- the owner, but WITHOUT runtime/b.rs

    (root / "runtime" / "b.rs").write_text("fn b() {}\n", encoding="utf-8")  # absent at c1, present from c2 on
    c2 = _commit(root, "c2: adds runtime/b.rs (records moves; product does not)")
    _git(root, "branch", "evidence")  # pinned at c2 -- product's first fallback

    return c1, c2


def _view_config(root: Path, c1: str, c2: str) -> viewmod.ViewConfig:
    doc = {
        "view_id": "fallback-test-view",
        "refs": [
            {"name": "records", "ref": "refs/heads/records", "follow": "tip", "role": "primary"},
            {"name": "product", "ref": "refs/heads/product", "follow": "pinned", "pinned_commit": c1,
             "role": "product"},
            {"name": "evidence", "ref": "refs/heads/evidence", "follow": "pinned", "pinned_commit": c2,
             "role": "evidence"},
        ],
        "partitions": [
            {"name": "product", "paths": ["runtime/**"], "owner": "product", "fallback": ["evidence", "history"]},
            {"name": "records", "paths": ["**"], "owner": "records", "fallback": ["product", "evidence", "history"]},
        ],
    }
    return viewmod.ViewConfig(view_id=doc["view_id"],
                               refs=[viewmod.RefSpec(name=r["name"], ref=r.get("ref"), ref_glob=r.get("ref_glob"),
                                                      follow=r["follow"], pinned_commit=r.get("pinned_commit"),
                                                      role=r.get("role", r["name"])) for r in doc["refs"]],
                               partitions=[viewmod.Partition(name=p["name"], owner=p["owner"],
                                                              fallback=p["fallback"], paths=p["paths"])
                                           for p in doc["partitions"]],
                               raw=doc)


def test_canonical_fallback_when_absent_at_owner_present_at_a_named_fallback(tmp_path):
    repo_root = tmp_path / "repo"
    c1, c2 = _build_repo(repo_root)
    config = _view_config(repo_root, c1, c2)
    resolved = viewmod.resolve_view(config, repo=str(repo_root))

    # querying "runtime/b.rs" AT c2 -- exactly the commit the "evidence" fallback ref is pinned to.
    result = resolved.classify_occurrence("runtime/b.rs", c2)
    assert result.status == viewmod.VS_CANONICAL_FALLBACK
    assert result.canonical_ref == "evidence"
    assert result.canonical_commit == c2

    # sanity: absent everywhere (owner AND every fallback) truly is ABSENT, not fallback.
    result_absent = resolved.classify_occurrence("runtime/does-not-exist.rs", c2)
    assert result_absent.status == viewmod.VS_ABSENT

    # sanity: present at the owner itself classifies CANONICAL, not fallback.
    result_owner = resolved.classify_occurrence("runtime/a.rs", c1)
    assert result_owner.status == viewmod.VS_CANONICAL
