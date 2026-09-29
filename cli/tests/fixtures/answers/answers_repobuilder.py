"""A tiny synthetic Git repository builder for ``tests/answers/*`` (REPAIR_DAG.yaml node R1-RA). Hermetic, fast,
and not shared with any other node's own fixture builder (``tests/fixtures/gather/gather_repobuilder.py``,
``tests/fixtures/route/exclusions/exclusions_repobuilder.py``, ...). Nothing here is Review-8/Phase-2 content
(OC-BR-02); every id/name is ``RA``/``ra_``-prefixed, deliberately unrelated, and used ONLY as fixture data.

One commit on one branch (``main``), referenced TWICE in the canonical view -- once as ``records``/role ``primary``
and once as ``product``/role ``product`` -- so both of ``govbridge.answers.cite``'s own default-commit conventions
(id-grammar/doc-anchor/Python resolve against the primary/"records" ref; Rust resolves against the product ref,
ARCHITECTURE.md section 4.6) resolve against the SAME fixture content without needing two divergent histories.

Real input shapes this repo carries (REPAIR_DAG.yaml node R1-RA, "REAL INPUT SHAPES"):

* ``ra_unique_fn`` -- a free Rust fn, uniquely named (bare-name resolution).
* ``ra_shared_fn`` -- defined TWICE, once inside each of two different ``mod`` blocks. The tree-sitter adapter
  stores a mod-nested fn's ``qualified_name`` as its BARE name only (no module-path tracking beyond an ``impl``
  block's own ``Type::method`` case -- ``govbridge.code.adapters.rust_treesitter``'s own module docstring), so
  ``ra_mod_one::ra_shared_fn``/``ra_mod_two::ra_shared_fn`` are genuinely AMBIGUOUS by trailing-segment resolution.
* ``test_ra_python_unique`` -- a Python ``def``, uniquely named, for exact-route resolution.
* ``test_ra_python_dup`` -- defined in TWO different Python files, for the Python AMBIGUOUS case.
* ``D-RA-0001``/``D-RA-0002`` -- an id-grammar id defined by a YAML top-level ``id:`` key, once in ordinary BLOCK
  style, once in FLOW style (``{id: ..., ...}`` on one line) -- both parse to the same shape once composed, so both
  exercise ``govbridge.authority.lifecycle.find_definition``'s SAME code path from genuinely different source
  syntax.
* ``RA-L-0001`` -- an id-grammar id defined by a level-2 Markdown heading (``DR-MD-LEDGER-HEADING``).
* ``docs/RA_GUIDE.md`` -- a numbered-heading Markdown document (for ``<doc> §N`` anchor resolution, and as the
  DOC_LEVEL_CITATION fixture's own sectioned document).
* ``docs/RA_DUP.md`` -- two headings sharing the SAME leading number (``## 3. ...`` twice), for the doc-anchor
  AMBIGUOUS case.
"""
from __future__ import annotations

import dataclasses
import subprocess
from pathlib import Path

from govbridge.authority.classes import BRIDGE_STATE_PATH

RUST_PATH = "runtime/src/ra_module.rs"
PY_UNIQUE_PATH = "tests_fixture_data/ra_python_unique_test.py"
PY_DUP_PATH_1 = "tests_fixture_data/ra_python_dup_one_test.py"
PY_DUP_PATH_2 = "tests_fixture_data/ra_python_dup_two_test.py"
DECISION_BLOCK_PATH = "spec/decisions/D-RA-0001.yaml"
DECISION_FLOW_PATH = "spec/decisions/D-RA-0002.yaml"
LEDGER_PATH = "docs/RA_LEDGER.md"
GUIDE_PATH = "docs/RA_GUIDE.md"
DUP_HEADING_PATH = "docs/RA_DUP.md"


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


def _write(root: Path, rel: str, content: str) -> None:
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


def build(tmp_path: Path) -> BuiltRepo:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "t")

    _write(root, RUST_PATH,
           "pub fn ra_unique_fn() -> bool {\n"
           "    true\n"
           "}\n\n"
           "mod ra_mod_one {\n"
           "    pub fn ra_shared_fn() -> bool {\n"
           "        true\n"
           "    }\n"
           "}\n\n"
           "mod ra_mod_two {\n"
           "    pub fn ra_shared_fn() -> bool {\n"
           "        false\n"
           "    }\n"
           "}\n")

    _write(root, PY_UNIQUE_PATH, "def test_ra_python_unique():\n    assert True\n")
    _write(root, PY_DUP_PATH_1, "def test_ra_python_dup():\n    assert True\n")
    _write(root, PY_DUP_PATH_2, "def test_ra_python_dup():\n    assert False\n")

    _write(root, DECISION_BLOCK_PATH,
           "id: D-RA-0001\nstatus: ACTIVE\ntitle: a fixture decision in block-style YAML\n")
    _write(root, DECISION_FLOW_PATH,
           "{id: D-RA-0002, status: ACTIVE, title: a fixture decision written in YAML flow style}\n")

    _write(root, LEDGER_PATH,
           "# RA fixture ledger\n\n"
           "## RA-L-0001 -- a fixture ledger-style heading definition\n\n"
           "Some fixture body text for RA-L-0001.\n")

    _write(root, GUIDE_PATH,
           "# RA fixture guide\n\n"
           "## 1. Overview\n\n"
           "Overview prose mentioning ra_unique_fn as a named identifier for lint testing.\n\n"
           "## 2. Details\n\n"
           "### 2.1 Sub Detail\n\n"
           "More prose about ra_unique_fn here, for the doc anchor test.\n")

    _write(root, DUP_HEADING_PATH,
           "# RA duplicate heading numbers\n\n"
           "## 3. First Copy\n\n"
           "Some text.\n\n"
           "## 3. Second Copy\n\n"
           "Other text.\n")

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
    commit = _git(root, "rev-parse", "HEAD").stdout.strip()

    registry_path = tmp_path / "authority-registry.yaml"
    registry_path.write_text(
        "schema: govbridge-authority-registry/1\n"
        "class_rules:\n"
        "  - {glob: 'spec/decisions/*.yaml', class: ARCHITECTURE_DECISION}\n"
        "  - {glob: 'runtime/**', class: EVIDENCE}\n"
        "  - {glob: '**', class: UNCLASSIFIED}\n",
        encoding="utf-8",
    )

    view_path = tmp_path / "canonical-view.yaml"
    view_path.write_text(
        "schema: govbridge-canonical-view/1\n"
        "view_id: ra-fixture-view\n"
        "refs:\n"
        "  - name: records\n    ref: refs/heads/main\n    follow: tip\n    role: primary\n"
        "    layers: [exact, lexical, semantic, code]\n"
        "  - name: product\n    ref: refs/heads/main\n    follow: tip\n    role: product\n"
        "    layers: [exact, lexical, semantic, code]\n"
        "partitions:\n"
        "  - {name: catchall, paths: ['**'], owner: records, fallback: [product]}\n",
        encoding="utf-8",
    )

    return BuiltRepo(root=root, commit=commit, view_path=str(view_path),
                      rules_path=str(root / "config" / "corpus-rules.yaml"), registry_path=str(registry_path))
