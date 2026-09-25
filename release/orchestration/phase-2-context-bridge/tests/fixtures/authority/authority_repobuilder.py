"""A tiny synthetic Git repository builder used by tests/authority/** and tests/graph/**. Hermetic and fast: no
dependency on the real, multi-thousand-file Governance OS tree. Mirrors just enough of the real repo's SHAPE
(a bridge-domain ORCHESTRATOR_STATE.yaml, a section-scoped owner-decision-like record, a decision-like record with
supersession metadata, a ledger, an owner-authorisation-like record superseded in part, a lesson/research record, a
withdrawn evidence record, a code file with a doc-comment citation, and a fixtures/ copy) for the id grammar,
registry, resolver, lifecycle and graph derivation to exercise generically -- nothing here is Review-8/Phase-2
content (OC-BR-02); the names are deliberately unrelated (FX-* / X-L-* / OA-X-01 / ...).
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


BRIDGE_STATE_PATH = "release/orchestration/phase-2-context-bridge/ORCHESTRATOR_STATE.yaml"
DISPOSITION_PATH = "release/orchestration/fx/GATES/OWNER-DECISION-FX-0010A-B-DISPOSITION.md"
DECISION_A_PATH = "spec/decisions/FX-0001.yaml"
DECISION_B_PATH = "spec/decisions/FX-0002.yaml"
LEDGER_PATH = "release/orchestration/fx/PHASE_LEDGER.md"
OWNER_AUTH_PATH = "release/orchestration/fx/GATES/OWNER-AUTHORISATION-FX-0006-BOUNDED-ROUND.md"
SUPERSEDING_PATH = "release/orchestration/fx/GATES/OWNER-DECISION-FX-0007-STOP-CONDITION.md"
LESSON_PATH = "spec/research/FX-RES-0001.md"
WITHDRAWN_PATH = "release/orchestration/fx/RESEARCH/FX-WITHDRAWN-0001.md"
CODE_PATH = "runtime/src/fx_module.rs"
FIXTURE_COPY_PATH = "fixtures/greenfield/spec/decisions/FX-0001.yaml"

DISPOSITION_TEXT = """# OWNER-DECISION-FX-0010A / 0010B -- generic disposition fixture

| Field | Value |
|---|---|
| Record | Owner decision (fixture, 2026-01-01) |
| Ids | **FX-0010A** (first item), **FX-0010B** (second item) |
| Status | IN FORCE |

## FX-0010A -- first anchored section

Body text for the first section.

## FX-0010B -- second anchored section

Body text for the second section.

## FX-DIRECTION -- a direction, not yet authority

> NOT YET AUTHORITY.

## FX-HYPOTHESIS -- a hypothesis, not yet classified

> NOT YET CLASSIFIED.
"""

OWNER_AUTH_TEXT = """# OWNER-AUTHORISATION-FX-0006 -- one bounded round

| Field | Value |
|---|---|
| Record | Owner authorisation (fixture) |
| Id | **OA-FX-06** |
| Status | IN FORCE for the fixture round |

## What was authorised

One bounded round, generic fixture text.
"""

SUPERSEDING_TEXT = """# OWNER-DECISION-FX-0007 -- stop condition fixture

| Field | Value |
|---|---|
| Record | Owner decision (fixture) |
| Id | **OD-FX-07** |
| Status | IN FORCE |
| Authorises | continuation **beyond** OA-FX-06's previous stop condition |
"""

LEDGER_TEXT = """# Fixture phase ledger

## X-L-0001

First ledger entry.

## X-L-0002

Second ledger entry, mentions FX-0001 and reopens FX-0002.
"""

LESSON_TEXT = """# FX-RES-0001 -- a research record (fixture evidence for FX-0001)

| Field | Value |
|---|---|
| Record | Research (fixture) |
| Id | FX-RES-0001 |

This research record mentions FX-0001 as evidence.
"""

WITHDRAWN_TEXT = """# FX-WITHDRAWN-0001 -- a withdrawn finding (fixture)

| Field | Value |
|---|---|
| Status | **WITHDRAWN 2026-01-02 -- the finding was wrong.** |
"""

CODE_TEXT = """// fx_module: implements the fixture rule (FX-0001, candidate class 1)
pub fn fx_rule() -> bool {
    true
}
"""


@dataclasses.dataclass
class FixtureRepo:
    root: Path
    c1: str
    c2: str
    records_ref: str = "refs/heads/records"
    product_ref: str = "refs/heads/product"
    evidence_ref: str = "refs/heads/evidence"


def build(root: Path) -> FixtureRepo:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q", "-b", "records")

    write(root, BRIDGE_STATE_PATH, """schema: bridge-orchestrator-state/1
mandatory_bridge_inputs:
  authority_classes:
    OWNER_DECISION: binding
    OWNER_DIRECTION_TO_TEST: a direction not yet authority
    HYPOTHESIS_TO_TEST: a hypothesis with no classificatory force
    HYPOTHESIS_RELEVANT_OBSERVATION: observation only
    EVIDENCE: measured facts
    EVIDENCE_WITHDRAWN: retained evidence of a withdrawn claim
    ORCHESTRATION_RECORD: current state, not authority
  items:
  - id: FX-0010A
    class: OWNER_DECISION
    path: """ + DISPOSITION_PATH + """
  - id: FX-0010B
    class: OWNER_DECISION
    path: """ + DISPOSITION_PATH + """
  - id: FX-DIRECTION
    class: OWNER_DIRECTION_TO_TEST
    path: """ + DISPOSITION_PATH + """
  - id: FX-HYPOTHESIS
    class: HYPOTHESIS_TO_TEST
    path: """ + DISPOSITION_PATH + """
owner_records:
- id: OA-FX-06
  path: """ + OWNER_AUTH_PATH + """
running_work:
  status: fixture value
""")
    write(root, DISPOSITION_PATH, DISPOSITION_TEXT)
    write(root, DECISION_A_PATH, "id: FX-0001\nstatus: SUPERSEDED\nsuperseded_by: FX-0002\n")
    write(root, DECISION_B_PATH, "id: FX-0002\nstatus: ACTIVE\nsupersedes: [FX-0001]\n")
    write(root, LEDGER_PATH, LEDGER_TEXT)
    write(root, OWNER_AUTH_PATH, OWNER_AUTH_TEXT)
    write(root, SUPERSEDING_PATH, SUPERSEDING_TEXT)
    write(root, LESSON_PATH, LESSON_TEXT)
    write(root, WITHDRAWN_PATH, WITHDRAWN_TEXT)
    write(root, CODE_PATH, CODE_TEXT)
    write(root, FIXTURE_COPY_PATH, "id: FX-0001\nstatus: ACTIVE\n")
    write(root, "config/corpus-rules.yaml", """schema: govbridge-corpus-rules/1
rules:
- {id: INCLUDED, effect: INCLUDE, match: {}}
""")

    c1 = _commit(root, "fixture c1: initial content")

    write(root, DISPOSITION_PATH, DISPOSITION_TEXT + "\n<!-- c2 touch -->\n")
    c2 = _commit(root, "fixture c2: touch disposition")

    _git(root, "branch", "-f", "product", "HEAD")
    _git(root, "branch", "-f", "evidence", "HEAD")

    return FixtureRepo(root=root, c1=c1, c2=c2)


def write_canonical_view(path: Path, repo: FixtureRepo) -> None:
    path.write_text(f"""schema: govbridge-canonical-view/1
view_id: fx-test-view
refs:
  - name: records
    ref: refs/heads/records
    follow: tip
    role: primary
  - name: product
    ref: refs/heads/product
    follow: tip
    role: product
  - name: evidence
    ref: refs/heads/evidence
    follow: tip
    role: evidence
  - name: history
    ref_glob: refs/heads/history/*
    follow: tip
    role: history
partitions:
  - name: records
    paths: ["**"]
    owner: records
    fallback: [product, evidence, history]
""", encoding="utf-8")
