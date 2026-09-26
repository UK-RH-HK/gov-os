"""A tiny synthetic Git repository builder for ``tests/route/test_task_exclusions.py`` (REPAIR-1 node R1-RX,
OBS-BR-08). Hermetic and fast, and not shared with any other node's fixture builder (``tests/fixtures/authority/
authority_repobuilder.py``, ``tests/fixtures/compile/compile_repobuilder.py``): this node's own control over its
own class coverage. Nothing here is Review-8/Phase-2 content (OC-BR-02); every id is EX-*, deliberately unrelated.

The repo carries an ``excluded/`` directory and a ``probes/`` directory that a test's ``retrieval_exclusions``
(``["excluded/**", "probes/**"]``) is meant to exclude, plus everything ``govbridge.core.taskctx``'s R1-RX wiring
needs to exercise every listed surface on ONE fixture:

* ``excluded/x.rs`` -- a code module (target/helper/caller/test) cited by an INCLUDED finding record, for the
  compiler's seed code route (RC-8's first named compile call site);
* ``excluded/topic.md`` -- the BEST lexical/semantic match for the query text "zzyzx quartz protocol details"
  (the acceptance check's own scenario: "a fixture repo whose excluded directory holds the best... match");
  ``included/topic-echo.md`` is a weaker match, present so a search still returns something once the excluded hit
  is dropped;
* ``probes/leak.md`` -- mentions ``EX-SEED`` (defined in an included decision record) from a directory ``why()``'s
  own findings stage recognises by prefix (``EVIDENCE_DIRS = ("probes", "telemetry")``), for ``why``/``history``;
* ``excluded/state.yaml`` -- a small structured document for ``govbridge state get`` (via a test-installed alias);
* ``ORCHESTRATOR_STATE.yaml`` (at ``govbridge.authority.classes.BRIDGE_STATE_PATH``, resolved through the fixed
  ``state:bridge#...`` alias every ``required_inputs`` row of this shape resolves through) carries one
  ``OWNER_DIRECTION_TO_TEST`` item (``EX-DIRECTION``), so a real compile places it in D.2 and exercises the
  compiler's SECOND named call site, the "evidence both ways" templates.
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


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD").stdout.strip()


def write(root: Path, rel: str, content: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


DIRECTION_PATH = "spec/decisions/EX-DIRECTION.md"
FIND_PATH = "spec/reports/EX-FIND-0001.md"
EXCLUDED_CODE_PATH = "excluded/x.rs"
EXCLUDED_PROBE_PATH = "excluded/probe.md"
SEED_DEF_PATH = "spec/decisions/EX-SEED.yaml"
LEAK_MENTION_PATH = "probes/leak.md"
LEXICAL_BEST_PATH = "excluded/topic.md"
LEXICAL_WEAK_PATH = "included/topic-echo.md"
STATE_EXCLUDED_PATH = "excluded/state.yaml"

RETRIEVAL_EXCLUSIONS = ["excluded/**", "probes/**"]

DIRECTION_TEXT = """# EX-DIRECTION -- a fixture direction, not yet authority

> NOT YET AUTHORITY.
"""

FIND_TEXT = """# EX-FIND-0001 -- a fixture finding record (mirrors BR-HO-0015's own G-derivation shape)

| Field | Value |
|---|---|
| Id | **EX-FIND-0001** |

## F1

This finding cites `excluded/x.rs:2` (the line inside the target function's body), the backticked symbol
`ex_helper_fn`, and the supporting evidence probe `excluded/probe.md:1`.
"""

CODE_TEXT = """// ex_target_module: fixture rust module for R1-RX's seed-code-route exclusion test
pub fn ex_target_fn() -> bool {
    ex_helper_fn()
}

pub fn ex_helper_fn() -> bool {
    true
}

pub fn ex_caller_of_target() -> bool {
    ex_target_fn()
}

#[test]
fn ex_test_target_fn() {
    let _ = ex_target_fn();
}
"""

PROBE_TEXT = """# EX-PROBE-0001 -- fixture evidence probe (excluded)

exzzy_probe_body: this is the probe body the finding record cites.
"""

SEED_DEF_TEXT = "id: EX-SEED\nstatus: ACTIVE\n"

LEAK_MENTION_TEXT = "This probe mentions EX-SEED as supporting evidence, from an excluded directory.\n"

LEXICAL_BEST_TEXT = """# the zzyzx quartz protocol

Full details of the zzyzx quartz protocol live here: zzyzx quartz zzyzx quartz zzyzx quartz.
"""

LEXICAL_WEAK_TEXT = """# an echo, elsewhere

A passing mention of the zzyzx quartz protocol, in an included file.
"""

STATE_EXCLUDED_TEXT = "value: 42\n"


@dataclasses.dataclass
class FixtureRepo:
    root: Path
    commit: str
    records_ref: str = "refs/heads/main"
    product_ref: str = "refs/heads/product"


def build(root: Path) -> FixtureRepo:
    root.mkdir(parents=True, exist_ok=True)
    _git(root, "init", "-q", "-b", "main")

    write(root, BRIDGE_STATE_PATH, """schema: bridge-orchestrator-state/1
mandatory_bridge_inputs:
  authority_classes:
    OWNER_DIRECTION_TO_TEST: a direction not yet authority
  items:
  - id: EX-DIRECTION
    class: OWNER_DIRECTION_TO_TEST
    path: """ + DIRECTION_PATH + """
running_work:
  status: fixture value
""")
    write(root, DIRECTION_PATH, DIRECTION_TEXT)
    write(root, FIND_PATH, FIND_TEXT)
    write(root, EXCLUDED_CODE_PATH, CODE_TEXT)
    write(root, EXCLUDED_PROBE_PATH, PROBE_TEXT)
    write(root, SEED_DEF_PATH, SEED_DEF_TEXT)
    write(root, LEAK_MENTION_PATH, LEAK_MENTION_TEXT)
    write(root, LEXICAL_BEST_PATH, LEXICAL_BEST_TEXT)
    write(root, LEXICAL_WEAK_PATH, LEXICAL_WEAK_TEXT)
    write(root, STATE_EXCLUDED_PATH, STATE_EXCLUDED_TEXT)
    write(root, "config/corpus-rules.yaml",
          "schema: govbridge-corpus-rules/1\nrules:\n- {id: INCLUDED, effect: INCLUDE, match: {}}\n")

    commit = _commit(root, "fixture c1: initial content")
    _git(root, "branch", "-f", "product", "HEAD")
    return FixtureRepo(root=root, commit=commit)


def write_canonical_view(path: Path) -> None:
    path.write_text(
        "schema: govbridge-canonical-view/1\n"
        "view_id: ex-exclusions-test-view\n"
        "refs:\n"
        "  - {name: records, ref: refs/heads/main, follow: tip, role: primary}\n"
        "  - {name: product, ref: refs/heads/product, follow: tip, role: product}\n"
        "partitions:\n"
        "  - {name: catchall, paths: ['**'], owner: records, fallback: [product]}\n",
        encoding="utf-8",
    )


def write_registry(path: Path) -> None:
    path.write_text(
        "schema: govbridge-authority-registry/1\n"
        "class_rules:\n"
        f"  - {{glob: '{EXCLUDED_CODE_PATH}', class: EVIDENCE}}\n"
        f"  - {{glob: '{EXCLUDED_PROBE_PATH}', class: EVIDENCE}}\n"
        "  - {glob: 'spec/reports/**', class: EVIDENCE}\n"
        "  - {glob: 'spec/decisions/**', class: ARCHITECTURE_DECISION}\n"
        "  - {glob: '**', class: UNCLASSIFIED}\n",
        encoding="utf-8",
    )
