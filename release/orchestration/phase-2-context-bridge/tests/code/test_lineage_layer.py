"""``govbridge.code.lineage_layer`` (BR-AR-0019 REOPENED ruling): the persisted, registered, digested "lineage"
store layer for TESTS-beyond-a-direct-call (CLI dispatch, test-registry shape), DEPENDS_ON_DATA and
CITES_REQUIREMENT edges. Lives under ``govbridge/code/`` (see its own module docstring for why); tested here
because ``tests/code/**`` is this node's mutation scope and already provides the ``repo``/isolated-store fixtures
(``tests/code/conftest.py``).

Hermetic (BR-DAG-AMEND-R1-4): every test builds its OWN throwaway repo (the ``repo`` fixture, a fresh ``tmp_path``
per test), passes ``repo=`` explicitly everywhere, never chdirs, and any GOV_BRIDGE_DOMAIN override is
``monkeypatch``-scoped to one test.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import govbridge

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "fixtures" / "authority"))
import authority_repobuilder  # noqa: E402

from govbridge.code import lineage_layer as LL
from govbridge.core import corpus, gitobj


class _FakeResolvedView:
    """The one method ``lineage_layer_builder`` calls on a resolved view -- a minimal stand-in, so this file's
    tests need no real ``config/canonical-view.yaml``."""

    def __init__(self, commit: str):
        self._commit = commit

    def ref_commit(self, _name: str) -> str:
        return self._commit


def _rules(repo) -> list:
    authority_repobuilder.write(repo, "config/corpus-rules.yaml",
                                 "schema: govbridge-corpus-rules/1\nrules:\n- {id: INCLUDED, effect: INCLUDE, match: {}}\n")
    return corpus.load_rules(str(repo / "config" / "corpus-rules.yaml"))


def test_lineage_layer_registered_after_ensure_all_layer_packages_imported():
    from govbridge.core import freshness as F
    from govbridge.core import manifest as M

    F.ensure_all_layer_packages_imported()
    assert "lineage" in F.get_layer_builders()
    assert "lineage" in M._LAYER_REGISTRY


def test_lineage_layer_builder_persists_all_four_edge_kinds(repo, monkeypatch):
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))

    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "runtime/src/lib.rs",
        "// See framework/contracts/contract.md:3 for the rule.\n"
        "// Also framework/contracts/contract.md section 4 covers budgets.\n"
        "fn f() {\n"
        "    let p = \"config/corpus-rules.yaml\";\n"
        "}\n",
    )
    authority_repobuilder.write(repo, "framework/contracts/contract.md", "# Contract\n\n## 4 Budgets\ntext\n")
    authority_repobuilder.write(
        repo, "tests/fixtures/demo-registry.yaml",
        "schema: fx-registry/1\nrows:\n  - capability: FX-CAP-1\n    tests: [tests/fx/test_fx_cap.py::test_one]\n",
    )
    authority_repobuilder.write(repo, "topcli/__init__.py", "")
    authority_repobuilder.write(
        repo, "topcli/main.py",
        "def main(argv):\n"
        "    cmd, rest = argv[0], argv[1:]\n"
        "    if cmd == 'greet':\n"
        "        from topcli import greeter\n"
        "        return greeter.main(rest)\n"
        "    return 2\n",
    )
    authority_repobuilder.write(
        repo, "topcli/greeter.py",
        "import argparse\n"
        "def say_hello(name):\n"
        "    return f'hello {name}'\n"
        "def main(argv):\n"
        "    p = argparse.ArgumentParser()\n"
        "    sub = p.add_subparsers(dest='cmd', required=True)\n"
        "    s = sub.add_parser('hello')\n"
        "    s.add_argument('name')\n"
        "    args = p.parse_args(argv)\n"
        "    if args.cmd == 'hello':\n"
        "        result = say_hello(args.name)\n"
        "    print(result)\n"
        "    return 0\n",
    )
    authority_repobuilder.write(
        repo, "tests/test_via_cli.py",
        "import subprocess, sys\n"
        "def test_cli_invocation():\n"
        "    subprocess.run([sys.executable, '-m', 'topcli.main', 'greet', 'hello', 'world'])\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "lineage fixture")

    conn = sqlite3.connect(":memory:")
    stats = LL.lineage_layer_builder(conn, _FakeResolvedView(commit), rules, str(repo), from_clean=True)

    assert stats["edges_by_type"].get("DEPENDS_ON_DATA", 0) > 0
    assert stats["edges_by_type"].get("CITES_REQUIREMENT", 0) > 0
    assert stats["edges_by_type"].get("TESTS", 0) >= 2  # one CLI-dispatch row, one registry-shape row

    rows = conn.execute("SELECT src, type, dst, derivation FROM lineage_edge ORDER BY type").fetchall()
    by_type_derivation = {(r[1], r[3]) for r in rows}
    assert ("DEPENDS_ON_DATA", "EXACT_LITERAL_PATH") in by_type_derivation
    assert ("CITES_REQUIREMENT", "EXACT_COMMENT_CITATION") in by_type_derivation
    assert ("CITES_REQUIREMENT", "HEURISTIC_COMMENT_SECTION") in by_type_derivation
    assert ("TESTS", "EXACT_CLI_DISPATCH") in by_type_derivation
    assert ("TESTS", "EXACT_TEST_REGISTRY_ROW") in by_type_derivation

    digest = LL.lineage_layer_digest(conn)
    assert digest.rows == len(rows)
    assert digest.digest != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"  # not the empty hash


def test_lineage_layer_digest_reproducible_across_two_from_clean_builds(repo, monkeypatch):
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(repo, "config/id-grammar.yaml", "version: 1\n")
    authority_repobuilder.write(
        repo, "runtime/src/lib.rs",
        "fn f() {\n    let p = \"config/corpus-rules.yaml\";\n}\n",
    )
    rules = _rules(repo)
    commit = authority_repobuilder._commit(repo, "reproducibility fixture")

    digests = []
    for _ in range(2):
        conn = sqlite3.connect(":memory:")
        LL.lineage_layer_builder(conn, _FakeResolvedView(commit), rules, str(repo), from_clean=True)
        digests.append(LL.lineage_layer_digest(conn).digest)
    assert digests[0] == digests[1]


def test_lineage_layer_never_descends_into_excluded_paths(repo, monkeypatch):
    """The code layer must keep honouring corpus-rule exclusions (BR-AR-0014): a rule that EXCLUDEs a path means
    ``corpus.classify_entry`` never returns INCLUDE for it, so ``lineage_layer_builder`` -- which gates on
    ``verdict.effect != INCLUDE_EFFECT`` before reading any blob -- never derives an edge from its content."""
    monkeypatch.setattr(govbridge, "GOV_BRIDGE_DOMAIN", str(repo))
    authority_repobuilder.write(
        repo, "runtime/src/secret.rs",
        "fn f() {\n    let p = \"config/corpus-rules.yaml\";\n}\n",
    )
    authority_repobuilder.write(
        repo, "config/corpus-rules.yaml",
        "schema: govbridge-corpus-rules/1\n"
        "rules:\n"
        "- {id: EXCLUDE_SECRET, effect: EXCLUDE, match: {globs: ['runtime/src/secret.rs']}}\n"
        "- {id: INCLUDED, effect: INCLUDE, match: {}}\n",
    )
    rules = corpus.load_rules(str(repo / "config" / "corpus-rules.yaml"))
    commit = authority_repobuilder._commit(repo, "exclusion fixture")

    conn = sqlite3.connect(":memory:")
    stats = LL.lineage_layer_builder(conn, _FakeResolvedView(commit), rules, str(repo), from_clean=True)
    rows = conn.execute("SELECT * FROM lineage_edge WHERE src LIKE 'runtime/src/secret.rs%'").fetchall()
    assert rows == []
    assert stats["blobs_scanned"] == 1  # only config/corpus-rules.yaml itself (a yaml file, INCLUDEd)
