"""A tiny, self-contained synthetic Git repository builder for BR-DAG-AMEND-R1-1's own regression test
(``tests/compile/test_verify_recorded_view.py``). Deliberately independent of both
``tests/fixtures/compile/compile_repobuilder.py`` and ``tests/fixtures/compile/mandatory/repobuilder.py`` -- this
fixture's whole point is a MOVING ``records`` tip (a second commit landing on it after a packet has already been
compiled), and no other fixture builder needs that shape. Every id is ``RV-*`` (Recorded View), unrelated to
Review-8/Phase-2 (OC-BR-02).
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


# must equal config/state-aliases.yaml's `bridge` alias -- see tests/fixtures/compile/mandatory/repobuilder.py's
# own comment on the same constraint.
BRIDGE_STATE_PATH = "release/orchestration/phase-2-context-bridge/ORCHESTRATOR_STATE.yaml"
RECORD_PATH = "spec/rv/RV-0001.md"
NEW_RECORD_PATH = "spec/rv/RV-0002.md"

RECORD_TEXT = "# RV-0001 -- a generic fixture owner record\n\nBody text for RV-0001.\n"
NEW_RECORD_TEXT = "# RV-0002 -- a NEW mandatory owner record, committed AFTER the packet\n\nBody text for RV-0002.\n"


def _state_yaml(items: list) -> str:
    lines = ["schema: bridge-orchestrator-state/1\n", "mandatory_bridge_inputs:\n", "  items:\n"]
    for item_id, path in items:
        lines.append(f"  - id: {item_id}\n")
        lines.append("    class: OWNER_DECISION\n")
        lines.append(f"    path: {path}\n")
    return "".join(lines)


@dataclasses.dataclass
class FixtureRepo:
    root: Path
    c1: str
    records_ref: str = "refs/heads/records"


def build(root: Path) -> FixtureRepo:
    """One commit, ONE mandatory owner record (``RV-0001``) declared in state -- the view a packet is first
    compiled against."""
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q", "-b", "records")
    write(root, "config/corpus-rules.yaml", """schema: govbridge-corpus-rules/1
rules:
- {id: INCLUDED, effect: INCLUDE, match: {}}
""")
    write(root, RECORD_PATH, RECORD_TEXT)
    write(root, BRIDGE_STATE_PATH, _state_yaml([("RV-0001", RECORD_PATH)]))
    c1 = _commit(root, "recorded-view fixture: initial content (RV-0001 only)")
    return FixtureRepo(root=root, c1=c1)


def add_new_mandatory_record(repo: FixtureRepo) -> str:
    """Commits a SECOND mandatory owner record (``RV-0002``) onto the SAME ``records`` branch, added to
    ``mandatory_bridge_inputs.items`` alongside RV-0001 -- exactly the run-1/RG scenario this amendment repairs
    ("OD-BR-03..06 became mandatory after run-1"). Returns the new commit id."""
    write(repo.root, NEW_RECORD_PATH, NEW_RECORD_TEXT)
    write(repo.root, BRIDGE_STATE_PATH, _state_yaml([("RV-0001", RECORD_PATH), ("RV-0002", NEW_RECORD_PATH)]))
    return _commit(repo.root, "add a new mandatory owner record AFTER the packet was compiled")


def write_canonical_view(path: Path, repo: FixtureRepo) -> None:
    path.write_text("""schema: govbridge-canonical-view/1
view_id: rv-test-view
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
purpose: a minimal fixture registry for tests/fixtures/compile/recorded_view -- no anchors needed.
section_anchors: []
unanchored_lines_rule: []
supersessions: []
lifecycle_overrides: []
class_rules:
  - {glob: '**', class: UNCLASSIFIED}
""", encoding="utf-8")


def make_task_spec(view_path: str, budget_profile: str = "bounded-builder") -> dict:
    return {
        "schema": "govbridge-task-spec/1", "task_id": "T-RV-1", "role": "test",
        "objective": "compile a packet, then re-verify it after the view has moved on",
        "view": view_path,
        "required_inputs": [
            {"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"},
        ],
        "seeds": [], "queries": [],
        "mutation_scope": ["tests/compile/**"],
        "prohibitions": ["do not touch anything outside mutation_scope"],
        "required_checks": ["pytest tests/compile -q"],
        "completion_vocabulary": ["ANSWERED", "PARTIAL", "BLOCKED"],
        "budget_profile": budget_profile,
    }
