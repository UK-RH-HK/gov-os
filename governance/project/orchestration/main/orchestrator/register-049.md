
## 49. Delegated decisions on W1-08's packages DP-8 and DP-9 (register v0.49, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-04 under DEC-220, on the two packages the W1-08 (`DAEO-uudf`) ticket lead
returned after implementation. For each, the proposer's recommendation and the orchestrator's agree, the confidence
is medium or higher, and the choice is reversible: no reader of either key exists yet.

### DEC-251 — W1-08 DP-8: the value of a `capabilities` entry
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-8 option (a), the test designer's and the lead's recommendation; confidence medium-high for the shape, medium for "both required" · **Under:** DEC-238, CAP-06.e
- **Decision:** Both keys, `code_intelligence` and `research_corpus`, are required. Each is a closed map with a
  required boolean `enabled`. `code_intelligence` also has `languages`, a non-empty list of strings when it is
  enabled. The path map already has this form; the schema is tightened to it, after a short test design round.

### DEC-252 — W1-08 DP-9: the lesson id grammar is the carried form
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-08 package DP-9 option (a), the lead's recommendation; confidence medium-high · **Under:** DEC-227, CAP-41.d
- **Decision:** `lesson_id` is `^L-[0-9]{4,}$`, the form of the carried lesson `L-0074`, in the shared definitions
  file and the lesson template. W1-44 carries the Phase-2 lessons without renumbering.

| Version | Date | Change |
|---|---|---|
| 0.49 | 2026-10-04 | Delegated under DEC-220: DEC-251 (W1-08 DP-8: both capabilities required, each a closed map with a boolean `enabled`; `languages` non-empty when `code_intelligence` is enabled), DEC-252 (W1-08 DP-9: `lesson_id` is `^L-[0-9]{4,}$`). |
