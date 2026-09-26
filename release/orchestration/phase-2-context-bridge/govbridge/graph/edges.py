"""Graph node/edge shapes (ARCHITECTURE.md section 6.1).

Nodes are the units of section 2: occurrence (file@ref), section, record (by id), symbol, test (a symbol with
is_test), commit (only commits records reference, plus the view commits) and finding (a record-local id defined
inside a review record). An edge is ``(src, type, dst, derivation, evidence_occurrence, evidence_line)``; derivation
is EXACT_* or HEURISTIC_*, and a heuristic edge is never rendered without its label.
"""
from __future__ import annotations

import dataclasses
from typing import Optional

# edge type constants (ARCHITECTURE.md section 6.1's table, verbatim names)
DEFINES = "DEFINES"
MENTIONS = "MENTIONS"
CITES_PATH = "CITES_PATH"
CITES_LINE = "CITES_LINE"
CITES_COMMIT = "CITES_COMMIT"
SUPERSEDES = "SUPERSEDES"
AMENDS = "AMENDS"
EXTENDS = "EXTENDS"
CONTAINS = "CONTAINS"
CALLS = "CALLS"
READS_KEY = "READS_KEY"
TESTS = "TESTS"
EVIDENCE_MAP = "EVIDENCE_MAP"
CODE_CITES = "CODE_CITES"
SYMBOL_MENTION = "SYMBOL_MENTION"
CHANGED_IN = "CHANGED_IN"
INTRODUCED_IN = "INTRODUCED_IN"
DELETED_IN = "DELETED_IN"
RELATION_CUE = "RELATION_CUE"
# R1-RL additions (REPAIR_PLAN.md section 4, REPAIR_DAG.yaml node R1-RL): code->data, code->requirement, and the
# two generic TESTS sources beyond a direct in-test call (a CLI-driven test, a schema/shape-recognised registry).
DEPENDS_ON_DATA = "DEPENDS_ON_DATA"
CITES_REQUIREMENT = "CITES_REQUIREMENT"

# derivation labels
EXACT_DEFINITION = "EXACT_DEFINITION"
EXACT_ID = "EXACT_ID"
HEURISTIC_LOCAL_ID = "HEURISTIC_LOCAL_ID"
EXACT_PATH = "EXACT_PATH"
HEURISTIC_SUFFIX = "HEURISTIC_SUFFIX"
EXACT_COMMIT = "EXACT_COMMIT"
EXACT_METADATA = "EXACT_METADATA"
REGISTRY_CITED = "REGISTRY_CITED"
EXACT_SPAN = "EXACT_SPAN"
EXACT_QUALIFIED = "EXACT_QUALIFIED"
HEURISTIC_NAME = "HEURISTIC_NAME"
EXACT_GIT = "EXACT_GIT"
EXACT_PARSE = "EXACT_PARSE"
HEURISTIC_CUE = "HEURISTIC_CUE"
# R1-RL additions
EXACT_LITERAL_PATH = "EXACT_LITERAL_PATH"          # a single string literal that is itself a tracked repo path
HEURISTIC_JOINED_PATH = "HEURISTIC_JOINED_PATH"    # two or more adjacent string-literal fragments joined by '/'
EXACT_COMMENT_CITATION = "EXACT_COMMENT_CITATION"  # a <doc path>[:line] citation inside a code comment
HEURISTIC_COMMENT_SECTION = "HEURISTIC_COMMENT_SECTION"  # a <doc path> section N / §N citation in a comment
HEURISTIC_SECTION_UNRESOLVED = "HEURISTIC_SECTION_UNRESOLVED"  # the document resolved; no heading numbered N was
                                                                # found there -- an edge to the DOCUMENT, never
                                                                # silently dropped (BR-AR-0019 reopening, Gap 1)
EXACT_CLI_DISPATCH = "EXACT_CLI_DISPATCH"          # a subprocess CLI invocation resolved to its exact handler fn
HEURISTIC_CLI_DISPATCH = "HEURISTIC_CLI_DISPATCH"  # ... resolved only to the owning module/subcommand pair
EXACT_TEST_REGISTRY_ROW = "EXACT_TEST_REGISTRY_ROW"  # a row of a schema/shape-recognised test registry
# BR-AR-0019 reopening, Gap 2: a Rust integration test that spawns the product's clap-derive binary.
EXACT_RUST_CLI_DISPATCH = "EXACT_RUST_CLI_DISPATCH"  # resolved to the innermost handler call a match arm names
HEURISTIC_RUST_CLI_DISPATCH_OUTER_ARM = "HEURISTIC_RUST_CLI_DISPATCH_OUTER_ARM"  # resolved only to the outer
                                                      # enum::variant a nested subcommand could not be walked past
# code-route labels reused verbatim from ARCHITECTURE.md section 4.6 (B3's vocabulary; B5 uses them only to LABEL
# edges read from B3's table schema, never to invent a resolution of its own)
CODE_ROUTE_LABELS = (
    "EXACT_PATH", "HEURISTIC_TYPE_PATH", "HEURISTIC_SAME_FILE", "HEURISTIC_UNIQUE_NAME", "HEURISTIC_AMBIGUOUS",
    "UNRESOLVED_EXTERNAL", "MACRO", "HEURISTIC_MACRO_TOKEN",
)


@dataclasses.dataclass(frozen=True)
class Edge:
    src: str
    type: str
    dst: str
    derivation: str
    evidence_occurrence: Optional[str]  # "path@commit" or "path@commit:L1-L2"
    evidence_line: Optional[int] = None
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class DerivedItem:
    """What the graph returns (never a MandatoryItem -- ARCHITECTURE.md section 5.3 rule 1). Wraps one or more
    edges that justify why this unit is being surfaced, plus the unit's own authority class/lifecycle (from
    govbridge.authority, computed but never upgraded here)."""
    unit: str
    kind: str  # "record" | "symbol" | "occurrence" | "commit" | "finding"
    edges: tuple  # (Edge, ...) -- the path/hop(s) that reached this unit
    cls: Optional[str] = None
    lifecycle: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "unit": self.unit, "kind": self.kind, "cls": self.cls, "lifecycle": self.lifecycle,
            "edges": [e.to_dict() for e in self.edges],
        }
