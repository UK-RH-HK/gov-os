"""BR-DAG-AMEND-R1-5 regression test.

``python -m govbridge.core.freshness rebuild --from-clean`` runs THIS FILE as a second, separate module object
("__main__") -- distinct from the CANONICAL ``govbridge.core.freshness`` module every sibling package (lexical,
semantic, code, authority, graph) imports and registers its own layer builder against
(``register_layer_builder``). Before R1-XC, the ``-m`` invocation's own ``_LAYER_BUILDERS`` dict held only "core"
(registered by that copy's own bottom-of-file call), so a bare ``-m govbridge.core.freshness rebuild --from-clean``
silently rebuilt only the "core" layer, while ``python -m govbridge index rebuild --from-clean`` (the top-level
CLI, which always imports ``govbridge.core.freshness`` by its dotted name) built every registered layer.

This test runs BOTH entry points, from-clean, against the SAME fixture repo/view, into separate stores, and
compares their resulting build manifests' ``layers`` dict (name -> {rows, digest, ...}) for equality. Run against
the pre-fix ``govbridge/core/freshness.py`` this fails (the ``-m`` store's non-"core" layers are all digests of an
empty table -- zero rows -- while the CLI store's are not); against the fixed file both manifests are identical.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

DOMAIN = Path(__file__).resolve().parents[2]


def _run(cmd: list, env: dict, cwd: Path) -> subprocess.CompletedProcess:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), env=env, timeout=120)
    assert r.returncode == 0, f"{cmd} failed: rc={r.returncode}\nstdout={r.stdout}\nstderr={r.stderr}"
    return r


def _manifest_layers(store_dir: Path) -> dict:
    manifest = json.loads((store_dir / "manifest.json").read_text(encoding="utf-8"))
    return manifest["manifest"]["layers"]


def test_module_entrypoint_and_top_level_cli_build_the_same_layer_set_and_digests(
    tmp_path, fixture_repo, view_path, rules_path
):
    base_env = dict(os.environ)
    base_env.pop("GOVBRIDGE_STORE", None)
    base_env["GOV_BRIDGE_HOME"] = str(tmp_path / "home")  # never the developer's real, shared cache
    base_env["PYTHONPATH"] = str(DOMAIN) + os.pathsep + base_env.get("PYTHONPATH", "")

    store_m = tmp_path / "store-module-entrypoint"
    store_cli = tmp_path / "store-top-level-cli"
    repo_root = fixture_repo.root

    env_m = dict(base_env)
    env_m["GOVBRIDGE_STORE"] = str(store_m)
    _run(
        [sys.executable, "-m", "govbridge.core.freshness", "rebuild", "--view", view_path, "--rules", rules_path,
         "--from-clean"],
        env=env_m, cwd=repo_root,
    )

    env_cli = dict(base_env)
    env_cli["GOVBRIDGE_STORE"] = str(store_cli)
    _run(
        [sys.executable, "-m", "govbridge", "index", "rebuild", "--view", view_path, "--rules", rules_path,
         "--from-clean"],
        env=env_cli, cwd=repo_root,
    )

    layers_m = _manifest_layers(store_m)
    layers_cli = _manifest_layers(store_cli)

    assert set(layers_m) == set(layers_cli), (sorted(layers_m), sorted(layers_cli))
    assert layers_m == layers_cli, (
        "the -m entry point built a different layer set/digest than the top-level CLI -- "
        f"m={layers_m} cli={layers_cli}"
    )
    # A real regression must show REAL, non-trivial content agreeing, not two empty layers agreeing vacuously:
    # tests/fixtures/core/repobuilder.py's fixture repo carries a real .rs file (runtime/src/init.rs), and every
    # non-history ref there admits every layer by default (no explicit `layers:` restriction) -- so the "code"
    # layer (govbridge.code.build.code_layer_builder) has real rows in BOTH stores once actually built.
    assert layers_cli.get("code", {}).get("rows", 0) > 0, layers_cli.get("code")
    assert layers_m.get("code", {}).get("rows", 0) > 0, layers_m.get("code")
