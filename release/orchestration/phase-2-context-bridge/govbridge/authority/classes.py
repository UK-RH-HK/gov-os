"""The authority class ladder and non-ladder classes (ARCHITECTURE.md section 5.1) -- a code CONSTANT
(ARCHITECTURE.md section 5.3 rule 3: "The class table in section 5.1 is a constant in authority/classes.py").

The non-ladder class NAMES are copied verbatim from ORCHESTRATOR_STATE.yaml -> mandatory_bridge_inputs.authority_classes
(seven names: OWNER_DECISION plus six non-ladder-only classes -- OWNER_DECISION is also the ladder's rank-1 class,
which is why it appears in both places in the state file's own vocabulary and here). ``load_state_authority_classes``
reads that dict from the bridge's own state file at its canonical occurrence, and ``diff_against_state`` is what
tests/authority/test_classes_match_state.py uses to assert equality (never hard-copy the list without that test).
"""
from __future__ import annotations

import dataclasses
from typing import Optional

from govbridge.core import gitobj, view as viewmod
from govbridge.core.yamlutil import load_yaml_text

# admissible_in_d1: True, False, or the literal string "ADJUDICATIONS_ONLY" for ORCHESTRATION_RECORD's conditional
# admissibility ("only adjudications, labelled rank 5" -- ARCHITECTURE.md section 5.1).
ADJUDICATIONS_ONLY = "ADJUDICATIONS_ONLY"


@dataclasses.dataclass(frozen=True)
class ClassSpec:
    name: str
    ladder: bool
    rank: Optional[int]  # 1 (highest) .. 7 (lowest); None for non-ladder classes
    admissible_in_a: bool
    admissible_in_d1: object  # bool | ADJUDICATIONS_ONLY
    allowed_sections: tuple  # where a non-ladder class may appear; () for ladder classes (any admissible section)
    banner: Optional[str] = None  # mandatory rendering banner for non-ladder classes


# --- the ladder (rank 1 highest .. 7 lowest; BR-HO-0001 section 2.2 item 2; ARCHITECTURE.md section 5.1 table) ----
LADDER: tuple = (
    ClassSpec("OWNER_DECISION", True, 1, True, True, ()),
    ClassSpec("CONTRACT", True, 2, True, False, ()),
    ClassSpec("FROZEN_GATE_CONTRACT", True, 3, True, False, ()),
    ClassSpec("ARCHITECTURE_DECISION", True, 4, True, True, ()),
    ClassSpec("ORCHESTRATION_RECORD", True, 5, True, ADJUDICATIONS_ONLY, ()),
    ClassSpec("EVIDENCE", True, 6, True, False, ()),
    ClassSpec("DERIVED", True, 7, False, False, ()),
)

# --- non-ladder classes: never rank as authority, never admissible in A or D.1 (ARCHITECTURE.md section 5.1) ------
NON_LADDER: tuple = (
    ClassSpec("OWNER_DIRECTION_TO_TEST", False, None, False, False, ("D.2",),
              banner="OWNER DIRECTION TO TEST: NOT YET AUTHORITY. The synthesis tests it and may reject it."),
    ClassSpec("HYPOTHESIS_TO_TEST", False, None, False, False, ("D.3",),
              banner="HYPOTHESIS TO TEST: NO CLASSIFICATORY FORCE. The bridge makes it testable and does not answer it."),
    ClassSpec("HYPOTHESIS_RELEVANT_OBSERVATION", False, None, False, False, ("F",),
              banner="OBSERVATION ABOUT ORCHESTRATOR REASONING. It concerns reasoning, not implementation, and is not "
                     "evidence for any hypothesis."),
    ClassSpec("EVIDENCE_WITHDRAWN", False, None, False, False, ("E", "F"),
              banner="WITHDRAWN: retained as evidence of a withdrawn claim; never cited as a finding."),
    ClassSpec("FIXTURE", False, None, False, False, ("H",), banner="TEST FIXTURE COPY, not a record"),
    ClassSpec("UNCLASSIFIED", False, None, False, False, ("H",), banner="AUTHORITY UNKNOWN"),
)

ALL_CLASSES: dict = {c.name: c for c in (*LADDER, *NON_LADDER)}

#: lifecycle vocabulary (ARCHITECTURE.md section 5.1) -- fixed statuses, in the code's own words, plus the mapping
#: table. Order matters for `lifecycle_order` (used by packet sort, and by tests here).
LIFECYCLE_ACTIVE = "ACTIVE"
LIFECYCLE_SUPERSEDED = "SUPERSEDED"
LIFECYCLE_WITHDRAWN = "WITHDRAWN"
LIFECYCLE_PROPOSED = "PROPOSED"
LIFECYCLE_HISTORICAL = "HISTORICAL"
LIFECYCLE_UNKNOWN = "UNKNOWN"

LIFECYCLE_ORDER = (LIFECYCLE_ACTIVE, LIFECYCLE_PROPOSED, LIFECYCLE_HISTORICAL, LIFECYCLE_SUPERSEDED,
                    LIFECYCLE_WITHDRAWN, LIFECYCLE_UNKNOWN)

#: the fixed source-vocabulary -> lifecycle mapping (ARCHITECTURE.md section 5.1). Checked, in order, against a
#: source string with a case-insensitive substring test; the first match wins. "Anything else maps to UNKNOWN."
_LIFECYCLE_WORDS: tuple = (
    ("SUPERSEDED", LIFECYCLE_SUPERSEDED),
    ("WITHDRAWN", LIFECYCLE_WITHDRAWN),
    ("RETRACTED", LIFECYCLE_WITHDRAWN),
    ("HISTORICAL", LIFECYCLE_HISTORICAL),
    ("RETIRED", LIFECYCLE_HISTORICAL),
    ("RETAINED AS HISTORICAL", LIFECYCLE_HISTORICAL),
    ("PROVISIONAL", LIFECYCLE_PROPOSED),
    ("PROPOSED", LIFECYCLE_PROPOSED),
    ("PENDING", LIFECYCLE_PROPOSED),
    ("IN FORCE", LIFECYCLE_ACTIVE),
    ("ACTIVE", LIFECYCLE_ACTIVE),
)


def map_lifecycle_word(text: Optional[str]) -> str:
    """Map a source status/quote string onto the fixed lifecycle vocabulary. Order-sensitive: SUPERSEDED/WITHDRAWN/
    HISTORICAL are checked before the ACTIVE/PROPOSED family so "SUPERSEDED by ..." never reads as ACTIVE. Anything
    unrecognised, including an absent string, maps to UNKNOWN (never treated as ACTIVE)."""
    if not text:
        return LIFECYCLE_UNKNOWN
    upper = text.upper()
    for word, lifecycle in _LIFECYCLE_WORDS:
        if word in upper:
            return lifecycle
    return LIFECYCLE_UNKNOWN


def map_in_effect(in_effect: Optional[bool]) -> Optional[str]:
    """``in_effect: true`` maps to ACTIVE, ``in_effect: false`` to PROPOSED (ARCHITECTURE.md section 5.1); None if
    the field is absent, so the caller can fall through to another source."""
    if in_effect is True:
        return LIFECYCLE_ACTIVE
    if in_effect is False:
        return LIFECYCLE_PROPOSED
    return None


BRIDGE_STATE_PATH = "release/orchestration/phase-2-context-bridge/ORCHESTRATOR_STATE.yaml"


def load_state_authority_classes(ref: str = "records", view_path: Optional[str] = None,
                                   repo: Optional[str] = None) -> dict:
    """The live ``mandatory_bridge_inputs.authority_classes`` dict, read from the bridge's own state file at its
    canonical occurrence (the ``records`` ref of ``config/canonical-view.yaml``), never from the working tree, so
    this always reflects the committed, canonical bridge state."""
    from govbridge import GOV_BRIDGE_DOMAIN
    import os

    view_path = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    vc = viewmod.load_view(view_path)
    resolved = viewmod.resolve_view(vc, repo=repo)
    commit = resolved.ref_commit(ref)
    if commit is None:
        raise ValueError(f"canonical-view has no ref named {ref!r}")
    text = gitobj.read_path(commit, BRIDGE_STATE_PATH, repo=repo)
    if text is None:
        raise FileNotFoundError(f"{commit}:{BRIDGE_STATE_PATH} not found")
    doc = load_yaml_text(text.decode("utf-8"))
    return dict(doc["mandatory_bridge_inputs"]["authority_classes"])


#: class names that never appear in mandatory_bridge_inputs.authority_classes: the ladder rows other than
#: OWNER_DECISION/ORCHESTRATION_RECORD/EVIDENCE, plus FIXTURE and UNCLASSIFIED. ARCHITECTURE.md section 5.2: "The
#: table's other classes (CONTRACT, FROZEN_GATE_CONTRACT, ARCHITECTURE_DECISION, DERIVED, FIXTURE, UNCLASSIFIED)
#: come from the ladder in BR-HO-0001 section 2.2 item 2, which covers the whole corpus."
NOT_IN_STATE_NAMES = (frozenset(c.name for c in LADDER) - frozenset({"OWNER_DECISION", "ORCHESTRATION_RECORD", "EVIDENCE"})) \
    | frozenset({"FIXTURE", "UNCLASSIFIED"})


def diff_against_state(state_classes: dict) -> list:
    """Every problem that would fail the build per ARCHITECTURE.md section 5.2's two build-failure conditions:
    (1) a class named in ``state_classes`` missing from ALL_CLASSES; (2) present but with different admissibility
    than section 5.1 says. Returns an empty list when the table matches."""
    problems = []
    for name in state_classes:
        if name not in ALL_CLASSES:
            problems.append(f"class {name!r} is in mandatory_bridge_inputs.authority_classes but missing from "
                             f"authority.classes.ALL_CLASSES")
            continue
        spec = ALL_CLASSES[name]
        if name in ("OWNER_DECISION", "ORCHESTRATION_RECORD", "EVIDENCE"):
            continue  # these three ladder rows are also named in the state dict; admissibility is the ladder's
        if spec.admissible_in_a or spec.admissible_in_d1:
            problems.append(f"class {name!r} from mandatory_bridge_inputs.authority_classes must never be "
                             f"admissible in A or D.1, but ALL_CLASSES says admissible_in_a={spec.admissible_in_a} "
                             f"admissible_in_d1={spec.admissible_in_d1}")
    for name, spec in ALL_CLASSES.items():
        if name not in state_classes and name not in NOT_IN_STATE_NAMES:
            problems.append(f"class {name!r} is in ALL_CLASSES but neither in mandatory_bridge_inputs.authority_classes "
                             f"nor in the documented ladder-only set")
    return problems
