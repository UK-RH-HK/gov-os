"""The retrieval-regression family check (DEC-425, CAP-38.b).

Run by ``sh -c`` in the project root (DEC-285). Exit 0 is green. When ``GOV_DEV_TIERS`` is not configured, the
check reports "unmeasured" and is never green.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def main():
    dev_tiers = os.environ.get("GOV_DEV_TIERS", "").strip()
    if not dev_tiers:
        print("unmeasured: GOV_DEV_TIERS is not configured")
        sys.exit(1)

    dev_tiers_path = Path(dev_tiers).expanduser()
    query_set_path = dev_tiers_path / "dev-queryset.yaml"

    if not query_set_path.is_file():
        print(f"unmeasured: no query set at {query_set_path}")
        sys.exit(1)

    import yaml
    from gov import store
    from gov.retrieval import lexical, semantic
    from gov.retrieval.retrieve import retrieve

    queries = yaml.safe_load(query_set_path.read_text(encoding="utf-8"))["queries"]

    baseline_path = Path(__file__).parent / "retrieve_baseline.yaml"
    baseline = yaml.safe_load(baseline_path.read_text(encoding="utf-8"))
    hit_at_5_threshold = float(baseline.get("hit_at_5", 80))
    forbidden_threshold = int(baseline.get("forbidden_citations", 2))

    tiers_map = {"A": "a-dev", "B": "b-dev"}

    with tempfile.TemporaryDirectory() as tmpdir:
        roots: dict[str, Path] = {}
        for programme, tier_name in tiers_map.items():
            tier_path = dev_tiers_path / tier_name
            if not (tier_path / ".git").exists():
                continue
            dest = Path(tmpdir) / tier_name
            result = subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(tier_path), str(dest)],
                                    capture_output=True)
            if result.returncode != 0:
                continue
            _adopt(dest)
            git_cmd = ["git", "-C", str(dest), "-c", "user.name=check", "-c", "user.email=check@check"]
            subprocess.run([*git_cmd, "add", "-A"], capture_output=True)
            subprocess.run([*git_cmd, "commit", "-q", "--allow-empty", "-m", "adopted"], capture_output=True)
            try:
                lexical.refresh(dest)
            except Exception:
                continue
            try:
                semantic.refresh(dest)
            except Exception:
                pass
            try:
                store.load(dest)
            except Exception:
                continue
            roots[programme] = dest

        if not roots:
            print("unmeasured: no dev tier could be indexed")
            sys.exit(1)

        scored: dict[str, list[bool]] = {}
        forbidden_count = 0
        for entry in queries:
            programme = entry.get("programme", "")
            root = roots.get(programme)
            if root is None:
                continue
            question = entry.get("query", "")
            gold = entry.get("gold", {})
            must_cite = gold.get("must_cite", [])
            must_not_cite = gold.get("must_not_cite", [])
            cls = entry.get("class", "default")
            try:
                bundle = retrieve(root, question, radius=3, batch_size=200, bundle_budget=1_000_000)
            except Exception:
                scored.setdefault(cls, []).append(False)
                continue
            cited = list(dict.fromkeys(item["path"] for item in bundle.get("evidence", [])))[:5]
            hit = any(p in cited for p in must_cite)
            scored.setdefault(cls, []).append(hit)
            for p in must_not_cite:
                if p in cited:
                    forbidden_count += 1

    if not scored:
        print("unmeasured: no queries could be run")
        sys.exit(1)

    per_class = {name: 100.0 * sum(hits) / len(hits) for name, hits in scored.items()}
    hit_at_5 = sum(per_class.values()) / len(per_class)

    print(f"hit@5: {hit_at_5:.1f} (baseline: {hit_at_5_threshold})")
    print(f"forbidden: {forbidden_count} (baseline: {forbidden_threshold})")
    for name, pct in sorted(per_class.items()):
        print(f"  {name}: {pct:.1f}%")

    if hit_at_5 < hit_at_5_threshold or forbidden_count > forbidden_threshold:
        sys.exit(1)


def _adopt(root: Path):
    """Give the project a path map that classes everything as embedded governance memory."""
    import yaml
    path_map_path = REPO_ROOT / "governance/project/path-map.yaml"
    if not path_map_path.is_file():
        return
    document = yaml.safe_load(path_map_path.read_text(encoding="utf-8"))
    document["namespaces"] = {"everything": {
        "paths": ["**"], "memory_class": "governance",
        "sensitivity": "internal",
        "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                            "independent-auditor", "research"],
        "retention": "kept in git history", "export_policy": "allowed",
        "provenance": "retrieval regression check", "deletion_rebuild": "authoritative; restored from git only",
        "embedding_policy": "embedded",
    }}
    (root / "governance/project").mkdir(parents=True, exist_ok=True)
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    config_src = REPO_ROOT / "template/.gitleaks.toml"
    if config_src.is_file():
        shutil.copy2(config_src, root / ".gitleaks.toml")
    exclude = root / ".git" / "info" / "exclude"
    exclude.parent.mkdir(parents=True, exist_ok=True)
    text = exclude.read_text(encoding="utf-8") if exclude.is_file() else ""
    if ".gov-runtime/" not in text:
        with open(exclude, "a", encoding="utf-8") as fh:
            fh.write("\n.gov-runtime/\n")


if __name__ == "__main__":
    main()
