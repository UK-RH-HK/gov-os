"""A synthetic Git fixture for ``tests/gather/test_followup.py`` (REPAIR_DAG.yaml node R1-GA2). Hermetic, and not
shared with any other node's fixture builder (mirrors ``tests/fixtures/gather/gather_repobuilder.py``'s own idiom,
never edits it). Nothing here is Review-8/Phase-2 content, and no id/symbol here is drawn from the Review-8 chains
or from this repair's own node ids (OC-BR-02) -- every id below is ``ZK-*``, deliberately unrelated.

REAL INPUT SHAPES this fixture reproduces, synthetically (R1-T2 item 4):

* an id-grammar id (``ZK-0001``) in a Markdown heading title, citing another one (``ZK-0002``) defined elsewhere;
* a YAML file using BOTH block and flow style ids;
* a function (``compute_zed``) whose only test (``test_compute_zed``) lives in a different top-level directory --
  Rust, since ``govbridge.code.symbols`` (the "code" layer) parses ``.rs`` blobs only, so a Python fn/test pair
  would be invisible to the code route's direct-call TESTS resolution entirely (see the checkpoint's own
  ``open_issues``/``findings``);
* a Rust ``mod::fn`` test path (``mod_a::test_widget``, module-free at the code layer) mentioned as plain text;
* a joined path literal (``"area_data" / "values.yaml"``) inside a ``tools/`` (a CODE_DIRS prefix) Python file;
* a ``///`` comment requirement citation (``area_doc.md section 2``) inside a ``runtime/`` (CODE_DIRS) Rust file;
* a 40-hex and a short commit hash, mentioned in prose;
* a three-ref view where the SAME path (``area_shared/shared.md``) carries a DIFFERENT blob at each of
  ``records``/``product``/``evidence``, with a ``product``-owned partition (REAL INPUT SHAPES item 6).
"""
from __future__ import annotations

import dataclasses
import subprocess
from pathlib import Path

from govbridge.authority.classes import BRIDGE_STATE_PATH


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


def write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


@dataclasses.dataclass
class BuiltRepo:
    root: Path
    records_commit: str
    product_commit: str
    evidence_commit: str
    view_path: str
    rules_path: str
    registry_path: str
    # identifiers a test resolves, by name -- never the literal string repeated at every call site.
    id_defined_elsewhere = "ZK-0002"
    id_citing = "ZK-0001"
    id_flow_style = "ZK-0004"
    symbol_name = "compute_zed"
    test_name = "test_compute_zed"
    rust_test_path = "mod_a::test_widget"
    rust_test_bare_name = "test_widget"
    joined_data_path = "area_data/values.yaml"
    requirement_doc = "area_doc.md"
    requirement_section = "2"
    commit_hash_40 = "0123456789abcdef0123456789abcdef01234567"
    commit_hash_short = "abc1234"
    shared_path = "area_shared/shared.md"


def build(tmp_path: Path) -> BuiltRepo:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")

    # (1) an id-grammar id, in a Markdown heading title, that CITES another one defined elsewhere.
    write(root, "area_one/RECORD-CITES.md",
          "# ZK-0001 citing record\n\n"
          "This record explains a rule. See ZK-0002 for the related definition, defined in a different directory.\n")
    write(root, "area_two/RECORD-DEFINED.md",
          "# ZK-0002 elsewhere\n\nThis is the record ZK-0001 cites, kept in its own top-level directory.\n")

    # (1b) block AND flow style YAML ids.
    write(root, "area_two/state.yaml",
          "schema: fx-state/1\n"
          "block_item:\n"
          "  id: ZK-0003\n"
          "  note: block style\n"
          "flow_item: {id: ZK-0004, note: flow style}\n")

    # (2) a function whose only test lives in a DIFFERENT top-level directory -- Rust, since govbridge.code's own
    # eager/lazy indexing (govbridge.code.symbols.ensure_indexed) parses ".rs" blobs only (Python is a separate,
    # not-yet-wired adapter -- tree_sitter_rust is the one this domain's "code" layer actually builds against), so
    # a real direct-call TESTS edge (derive.tests_of, queried through the code route's own include_tests) needs a
    # Rust fn/#[test] pair to be reachable at all.
    write(root, "area_three/lib.rs", "fn compute_zed() -> i32 {\n    42\n}\n")
    write(root, "area_four/tests/test_lib.rs",
          "#[test]\nfn test_compute_zed() {\n    assert_eq!(compute_zed(), 42);\n}\n")

    # (3) a Rust mod::fn test path, module-free at the code layer -- mentioned as plain prose text elsewhere, so a
    # text-based identifier extractor finds it without needing the lineage layer at all; the code layer's own
    # qualified_name for it is bare ("test_widget"), so resolving the FULL "mod_a::test_widget" text must fall back
    # to the trailing segment.
    write(root, "area_five/NOTES.md",
          "# Notes\n\nThe harness test mod_a::test_widget covers the widget contract end to end.\n")
    write(root, "runtime/harness.rs",
          "//! harness tests\n"
          "mod mod_a {\n"
          "    #[test]\n"
          "    fn test_widget() {\n"
          "        assert!(true);\n"
          "    }\n"
          "}\n")

    # (4) a joined path literal inside a CODE_DIRS file ("tools/"), naming a real tracked data file.
    write(root, "area_data/values.yaml", "values: [1, 2, 3]\n")
    write(root, "tools/loader.py",
          "import os\n\n\n"
          "def load_values():\n"
          "    path = os.path.join(\"area_data\", \"values.yaml\")\n"
          "    return path\n")

    # (5) a comment requirement citation inside a CODE_DIRS Rust file ("runtime/"), resolved to a numbered heading.
    write(root, "area_doc.md", "# Doc\n\n## 2 Budget rule\n\nEvery consumer must acknowledge the budget rule.\n")
    write(root, "runtime/engine.rs",
          "/// See area_doc.md section 2 for the budget rule.\n"
          "fn enforce() {}\n")

    # (6) commit hashes mentioned in prose (40-hex and short).
    write(root, "area_six/CHANGELOG.md",
          "# Changelog\n\n"
          "Fixed in 0123456789abcdef0123456789abcdef01234567 (short form abc1234).\n")

    # (7) a superseded record, for the merge-layer authority/lifecycle test (kept generic; the authority
    # classification itself is exercised in tests/gather/test_merge.py's own synthetic RouteHit, not re-derived
    # here from a real classifier pass).
    write(root, "area_seven/OLD-RECORD.md", "# ZK-0005 old record\n\nSTATUS: SUPERSEDED.\n")

    write(root, "area_shared/shared.md", "records value\n")

    state_path = root / BRIDGE_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "schema: bridge-orchestrator-state/1\n"
        "mandatory_bridge_inputs:\n  authority_classes: {}\n  items: []\n",
        encoding="utf-8",
    )

    records_commit = _commit(root, "c1: records content")

    _git(root, "branch", "-f", "product", "HEAD")
    _git(root, "checkout", "-q", "product")
    write(root, "area_shared/shared.md", "product value\n")
    product_commit = _commit(root, "c2: product diverges on area_shared/shared.md")

    _git(root, "checkout", "-q", "main")
    _git(root, "branch", "-f", "evidence", "HEAD")
    _git(root, "checkout", "-q", "evidence")
    write(root, "area_shared/shared.md", "evidence value\n")
    evidence_commit = _commit(root, "c3: evidence diverges on area_shared/shared.md")

    _git(root, "checkout", "-q", "main")

    view_path = tmp_path / "canonical-view.yaml"
    view_path.write_text(
        "schema: govbridge-canonical-view/1\n"
        "view_id: followup-test-view\n"
        "refs:\n"
        "  - {name: records, ref: refs/heads/main, follow: tip, role: primary,\n"
        "     layers: [exact, lexical, records, graph, semantic, code]}\n"
        "  - {name: product, ref: refs/heads/product, follow: tip, role: product,\n"
        "     layers: [exact, lexical, records, graph, semantic, code]}\n"
        "  - {name: evidence, ref: refs/heads/evidence, follow: tip, role: evidence,\n"
        "     layers: [exact, lexical, records, graph, semantic, code]}\n"
        "partitions:\n"
        "  - {name: shared, paths: ['area_shared/**'], owner: product, fallback: [records, evidence]}\n"
        "  - {name: catchall, paths: ['**'], owner: records, fallback: [product, evidence]}\n",
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
        "  - {glob: 'area_seven/**', class: EVIDENCE}\n"
        "  - {glob: '**', class: EVIDENCE}\n",
        encoding="utf-8",
    )

    return BuiltRepo(root=root, records_commit=records_commit, product_commit=product_commit,
                      evidence_commit=evidence_commit, view_path=str(view_path), rules_path=str(rules_path),
                      registry_path=str(registry_path))


def build_ambiguous_rust_test(tmp_path: Path):
    """A second, SEPARATE single-ref repo whose bare code-layer symbol name ``test_widget`` is defined TWICE, in
    two different modules -- REAL INPUT SHAPES item 2: "with a distinct heuristic label where the full path is not
    unique". Kept apart from :func:`build`'s own repo so the main fixture's own trailing-segment resolution stays
    UNAMBIGUOUS (exactly one ``test_widget``)."""
    root = tmp_path / "ambiguous-repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")
    write(root, "one/a.rs", "mod mod_a {\n    #[test]\n    fn test_widget() {\n        assert!(true);\n    }\n}\n")
    write(root, "two/b.rs", "mod mod_b {\n    #[test]\n    fn test_widget() {\n        assert!(true);\n    }\n}\n")
    state_path = root / BRIDGE_STATE_PATH
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        "schema: bridge-orchestrator-state/1\nmandatory_bridge_inputs:\n  authority_classes: {}\n  items: []\n",
        encoding="utf-8",
    )
    commit = _commit(root, "c1: two same-named test_widget symbols")

    # the code route only ever resolves seeds against the ref whose role is "product"
    # (govbridge.route.real_routes._product_commit) -- a second ref pointed at the SAME commit, purely so this
    # single-branch fixture has one, exactly like config/canonical-view.yaml's real product/records pair.
    view_path = tmp_path / "ambiguous-canonical-view.yaml"
    view_path.write_text(
        "schema: govbridge-canonical-view/1\nview_id: followup-ambiguous-view\nrefs:\n"
        "  - {name: records, ref: refs/heads/main, follow: tip, role: primary,\n"
        "     layers: [exact, lexical, records, graph, semantic, code]}\n"
        "  - {name: product, ref: refs/heads/main, follow: tip, role: product,\n"
        "     layers: [exact, lexical, records, graph, semantic, code]}\n"
        "partitions:\n  - {name: catchall, paths: ['**'], owner: records, fallback: [product]}\n",
        encoding="utf-8",
    )
    rules_path = tmp_path / "ambiguous-corpus-rules.yaml"
    rules_path.write_text("schema: govbridge-corpus-rules/1\nrules:\n  - {id: INCLUDED, effect: INCLUDE, match: {}}\n",
                           encoding="utf-8")
    registry_path = tmp_path / "ambiguous-authority-registry.yaml"
    registry_path.write_text("schema: govbridge-authority-registry/1\nclass_rules:\n  - {glob: '**', class: EVIDENCE}\n",
                              encoding="utf-8")

    return BuiltRepo(root=root, records_commit=commit, product_commit=commit, evidence_commit=commit,
                      view_path=str(view_path), rules_path=str(rules_path), registry_path=str(registry_path))
