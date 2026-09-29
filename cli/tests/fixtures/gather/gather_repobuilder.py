"""A tiny synthetic Git repository builder for ``tests/gather/test_engine.py`` (REPAIR_DAG.yaml node R1-GA1).
Hermetic and fast, and not shared with any other node's fixture builder (``tests/fixtures/route/exclusions/
exclusions_repobuilder.py``, ``tests/fixtures/compile/compile_repobuilder.py``). Nothing here is Review-8/Phase-2
content (OC-BR-02); every id is GA1-*, deliberately unrelated.

The repo's evidence for the single lexical term "gizmoflux" spans FIVE top-level directories (``area_alpha`` ..
``area_epsilon``), two files each -- ten chunks in total, well beyond any one small ``--batch-size`` -- so a
``govbridge gather`` call over it needs more than one round to cover the ``purpose`` facet (REPAIR_DAG.yaml
acceptance check 1: "a fixture subject whose evidence spans 5 directories and exceeds one batch is covered after
more than one round"). One file (``area_gamma/contract.md``) is classified ``CONTRACT`` (everything else
``EVIDENCE``), so the ``requirement`` facet (scoped to ``CONTRACT``/``FROZEN_GATE_CONTRACT``) legitimately needs to
page past the other, out-of-scope hits before it finds its one in-scope item.
"""
from __future__ import annotations

import dataclasses
import subprocess
from pathlib import Path

from govbridge.authority.classes import BRIDGE_STATE_PATH

TERM = "gizmoflux"
AREAS = ("area_alpha", "area_beta", "area_gamma", "area_delta", "area_epsilon")
CONTRACT_PATH = "area_gamma/contract.md"


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


def write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


@dataclasses.dataclass
class BuiltRepo:
    root: Path
    commit: str
    view_path: str
    rules_path: str
    registry_path: str
    areas: tuple = AREAS
    term: str = TERM
    contract_path: str = CONTRACT_PATH


def build(tmp_path: Path) -> BuiltRepo:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")

    for i, area in enumerate(AREAS):
        for j in range(2):
            write(root, f"{area}/note{j}.md",
                  f"# {area} note {j}\n\n{TERM} evidence item {area}-{j}: this note explains part of the "
                  f"{TERM} behaviour, item number {i * 2 + j} of the fixture's ten total chunks.\n")
    write(root, CONTRACT_PATH,
          f"# {TERM} contract\n\nThe {TERM} contract requirement: every {TERM} consumer must acknowledge this "
          f"requirement before use.\n")

    state_path = root / BRIDGE_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "schema: bridge-orchestrator-state/1\n"
        "mandatory_bridge_inputs:\n  authority_classes: {}\n  items: []\n",
        encoding="utf-8",
    )

    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "c1")
    commit = _git(root, "rev-parse", "HEAD").stdout.strip()
    _git(root, "branch", "-f", "product", "HEAD")

    view_path = tmp_path / "canonical-view.yaml"
    view_path.write_text(
        "schema: govbridge-canonical-view/1\n"
        "view_id: gather-test-view\n"
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
        f"  - {{glob: '{CONTRACT_PATH}', class: CONTRACT}}\n"
        "  - {glob: '**/*.md', class: EVIDENCE}\n"
        "  - {glob: '**', class: UNCLASSIFIED}\n",
        encoding="utf-8",
    )

    return BuiltRepo(root=root, commit=commit, view_path=str(view_path), rules_path=str(rules_path),
                      registry_path=str(registry_path))
