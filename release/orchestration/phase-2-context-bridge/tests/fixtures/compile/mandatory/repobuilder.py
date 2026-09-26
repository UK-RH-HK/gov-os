"""A tiny, self-contained synthetic Git repository builder for R1-RM's own acceptance test
(``tests/compile/test_mandatory_fidelity.py``). Deliberately INDEPENDENT of the shared
``tests/fixtures/compile/compile_repobuilder.py`` (that module is not in this node's mutation scope, and this
fixture's whole point -- an oversize mandatory item, ``entries``/``keys``/multi-``paths`` selectors, and a
by-reference directory -- has no counterpart there). Every id is ``MF-*`` (Mandatory Fidelity), deliberately
unrelated to Review-8/Phase-2 (OC-BR-02).
"""
from __future__ import annotations

import dataclasses
import subprocess
from pathlib import Path


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {args} failed: {r.stderr}")
    return r


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# must equal config/state-aliases.yaml's `bridge` alias -- authority.classes.BRIDGE_STATE_PATH and
# authority.resolver.STATE_ALIASES["bridge"] both read that SAME real, non-fixture-overridable config value, so a
# fixture's own state file has to live at exactly this path for `state:bridge#...` to resolve it in a test repo.
BRIDGE_STATE_PATH = "release/orchestration/phase-2-context-bridge/ORCHESTRATOR_STATE.yaml"
BIG_MD_PATH = "spec/mf/BIG-RECORD.md"
ENTRIES_YAML_PATH = "spec/mf/entries.yaml"
KEYS_YAML_PATH = "spec/mf/keys.yaml"
PATH_A = "spec/mf/two-path-a.md"
PATH_B = "spec/mf/two-path-b.md"
DIR_PATH = "spec/mf/bundle"  # a by-reference directory item (no trailing slash here; the row declares it with one)


def _big_markdown(min_bytes: int = 30_000) -> str:
    """A Markdown document with many headings, generated (never hand-typed) until it exceeds ``min_bytes`` --
    node R1-RM's own "oversize mandatory item" fixture (REPAIR_PLAN.md section 3 rule 1)."""
    parts = ["# MF-BIG -- a generated, oversize fixture record\n"]
    i = 0
    total = len("".join(parts))
    while total < min_bytes:
        i += 1
        section = (
            f"\n## Part {i}\n\n"
            f"This is generated body text for part {i}, repeated to make the whole document exceed the per-item "
            f"cap deliberately, so the compiler must map it into sections rather than deliver it whole or -- the "
            f"defect this fixture exists to catch -- silently cut it off mid-sentence with no marker at all.\n"
        )
        parts.append(section)
        total += len(section)
    return "".join(parts)


def _entries_yaml(n: int = 8) -> str:
    lines = ["records:\n"]
    for i in range(1, n + 1):
        lines.append(f"- id: E-{i:04d}\n")
        lines.append(f"  text: entry number {i}, generated fixture content\n")
    return "".join(lines)


KEYS_YAML_TEXT = """alpha:
  note: the first selectable top-level key
  value: 1
beta:
  note: NOT selected by the fixture's `keys` selector -- must appear only in the remainder
  value: 2
gamma:
  note: the second selectable top-level key
  value: 3
delta:
  note: also not selected -- another remainder member
  value: 4
"""

PATH_A_TEXT = "# MF-PATHS -- primary path\n\nContent of the FIRST declared path.\n"
PATH_B_TEXT = "# MF-PATHS -- secondary path\n\nContent of the SECOND declared path -- must be delivered too, not " \
              "merely existence-checked (REPAIR_PLAN.md section 3 rule 2).\n"

DIR_FILE_1 = "one.txt"
DIR_FILE_2 = "two.md"
DIR_FILE_3 = "nested/three.txt"


@dataclasses.dataclass
class FixtureRepo:
    root: Path
    c1: str
    records_ref: str = "refs/heads/records"


def build(root: Path) -> FixtureRepo:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q", "-b", "records")

    write(root, "config/corpus-rules.yaml", """schema: govbridge-corpus-rules/1
rules:
- {id: INCLUDED, effect: INCLUDE, match: {}}
""")

    write(root, BIG_MD_PATH, _big_markdown())
    write(root, ENTRIES_YAML_PATH, _entries_yaml())
    write(root, KEYS_YAML_PATH, KEYS_YAML_TEXT)
    write(root, PATH_A, PATH_A_TEXT)
    write(root, PATH_B, PATH_B_TEXT)
    write(root, f"{DIR_PATH}/{DIR_FILE_1}", "member one\n")
    write(root, f"{DIR_PATH}/{DIR_FILE_2}", "# member two\n")
    write(root, f"{DIR_PATH}/{DIR_FILE_3}", "member three, nested\n")

    write(root, BRIDGE_STATE_PATH, f"""schema: bridge-orchestrator-state/1
mandatory_bridge_inputs:
  authority_classes:
    OWNER_DECISION: binding
    ORCHESTRATION_RECORD: current state, not authority
    EVIDENCE: measured facts
  items:
  - id: MF-BIG
    class: ORCHESTRATION_RECORD
    path: {BIG_MD_PATH}
  - id: MF-ENTRIES
    class: ORCHESTRATION_RECORD
    path: {ENTRIES_YAML_PATH}
    entries: {{under: records, start: E-0003, end: E-0006}}
  - id: MF-KEYS
    class: ORCHESTRATION_RECORD
    path: {KEYS_YAML_PATH}
    keys: [alpha, gamma]
  - id: MF-PATHS
    class: ORCHESTRATION_RECORD
    path: {PATH_A}
    paths: [{PATH_A}, {PATH_B}]
  - id: MF-DIR
    class: EVIDENCE
    path: {DIR_PATH}/
  unresolvable_probe_items:
  # an isolated, second mandatory-items list (never referenced by mandatory_bridge_inputs.items[*], so it never
  # perturbs the "everything above resolves" happy-path test) -- a `keys` selector naming a key the document does
  # not have, exercising "an unresolvable selector fails closed" on its own.
  - id: MF-UNRESOLVABLE
    class: ORCHESTRATION_RECORD
    path: {KEYS_YAML_PATH}
    keys: [alpha, no-such-key]
""")

    c1 = _commit(root, "mandatory-fidelity fixture: initial content")
    return FixtureRepo(root=root, c1=c1)


def write_canonical_view(path: Path, repo: FixtureRepo) -> None:
    path.write_text("""schema: govbridge-canonical-view/1
view_id: mf-test-view
refs:
  - name: records
    ref: refs/heads/records
    follow: tip
    role: primary
partitions:
  - name: records
    paths: ["**"]
    owner: records
    fallback: []
""", encoding="utf-8")


def write_registry(path: Path) -> None:
    path.write_text("""schema: govbridge-authority-registry/1
purpose: a minimal fixture registry for tests/fixtures/compile/mandatory -- no section anchors are needed (every
  MF-* item's class comes straight from its mandatory_bridge_inputs row).

section_anchors: []
unanchored_lines_rule: []
supersessions: []
lifecycle_overrides: []

class_rules:
  - {glob: 'spec/mf/bundle/**', class: EVIDENCE, type: fixture-bundle-member}
  - {glob: '**', class: UNCLASSIFIED}
""", encoding="utf-8")


def make_task_spec(view_path: str, required_inputs=None, budget_profile: str = "bounded-builder") -> dict:
    return {
        "schema": "govbridge-task-spec/1", "task_id": "T-MF-1", "role": "test",
        "objective": "compile a packet over the mandatory-fidelity fixture corpus",
        "view": view_path,
        "required_inputs": required_inputs if required_inputs is not None else [
            {"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"},
        ],
        "seeds": [], "queries": [],
        "mutation_scope": ["tests/compile/**"],
        "prohibitions": ["do not touch anything outside mutation_scope"],
        "required_checks": ["pytest tests/compile -q"],
        "completion_vocabulary": ["ANSWERED", "PARTIAL", "BLOCKED"],
        "budget_profile": budget_profile,
    }
