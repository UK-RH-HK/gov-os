---
id: DAEO-mpq2
wbs_id: W2-192
external-ref: W2-192
status: in_progress
deps: []
links: []
created: 2026-11-16T14:45:01Z
type: task
priority: 2
assignee: Usain
parent: DAEO-sdxk
tags: [wave-2, adoption]
class: implementation
role: engineer
profile: FULL
state_class: AUTHORITATIVE
allowed_paths:
- src/gov/adopt/command.py
- src/gov/adopt/stages.py
- src/gov/adopt/spec_audit.py
- tests/unit/adopt/test_w2_192*
- src/gov/adopt/project.py
- "tests/acceptance/W1-41/*support*.py"
- "tests/acceptance/W2-23/*support*.py"
- "tests/acceptance/W2-88/*support*.py"
- "tests/acceptance/W2-190/*support*.py"
reads:
- template/governance/kernel/skills/adopt/SKILL.md
- src/gov/adopt/**
- docs/contract/CONTRACT_v4.md
- governance/project/orchestration/packages/P-ADOPT-SPEC-AUDIT-1.md
needs:
- src/gov/adopt/command.py
- src/gov/adopt/stages.py
waits_on: []
est_loc: 400
kpis:
  success:
  - line: "S1 gov adopt offers stage AS (the spec audit) after A2 and before A3: `gov adopt --lite --stage AS` reads A1's inventory and A2's classes and writes governance/adoption/AS-spec-audit.md; A3 refuses to run before AS is recorded [DEC-1200, P-ADOPT-SPEC-AUDIT-1]"
    verify: "tests/unit/adopt/test_w2_192_stage.py: a fixture repository through A1 and A2; AS writes its record; A3 before AS is refused with a named code; command.STAGES lists AS between A2 and A3"
  - line: "S2 The AS record lists every spec found (path, title, its stated wave or status), each built, partly built or not built with evidence (code paths, tests, commits), the tickets found done or not by wave, specs with no code, code with no spec (top-level code modules no spec names), and each gap as one question to the owner with a place for the answer [DEC-1200]"
    verify: "tests/unit/adopt/test_w2_192_record.py: a fixture with a built spec, a partly built spec, an unbuilt spec, an unspecified module and two tickets; the record holds each in its class with evidence and one question per gap"
  - line: "S3 The lite checks: the record names every spec and every top-level code module the inventory holds, and every gap carries a question; a record that fails either is refused by gov adopt [DEC-1200]"
    verify: "tests/unit/adopt/test_w2_192_record.py: a record missing one module, or a gap without a question, is refused with a named code"
  failure:
  - line: "F1 AS writes outside governance/adoption/, changes any spec or code, or a gap is closed without the owner's recorded answer [DEC-1200]"
    verify: "tests/unit/adopt/test_w2_192_scope.py: a byte comparison of the fixture outside governance/adoption/ before and after AS; a gap's answer field stays empty until written by the owner's route"
non_goals:
- "the adopt skill's text gains the stage by its CIT-P (a kernel path: the owner's approval of the bytes), and the Contract's CAP-44 line is a specification change by its own CIT-P; the lead returns PACKAGES with both drafts"
- "no independent auditor session in the lite form: A5's reviewer reads the AS record"
- "no classing of specs by a model; built or not is judged from code paths, tests and commits"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1200, DEC-1199, DEC-974, CAP-44]
acceptance_tests: {path: tests/acceptance/W2-192/}
---
# Adoption stage AS: the spec audit (P-ADOPT-SPEC-AUDIT-1)

# W2-192 Adoption stage AS: the spec audit (P-ADOPT-SPEC-AUDIT-1)

Filed 2026-11-16 by the CTO on the owner's word (DEC-1200: "P-ADOPT-SPEC-AUDIT-1 (a); this is my approval of its new
ticket").

**Problem.** The adoption practice has no spec audit: the adopt skill's stages are A0-A10 and MA, A2 classes a spec as
a document, and CAP-44 has no spec-to-code stage (A11's full audit is Wave 3, CAP-44.k). The owner made it a standard
adoption stage for every repository; EXAMIN's CTO does it by hand meanwhile (its Wave 0 step 3).

**Approach.** Stage AS after A2, before A3, as P-ADOPT-SPEC-AUDIT-1 section 2: its record
`governance/adoption/AS-spec-audit.md`, the lite checks, gov adopt's stage list, a stage function, its record schema;
the skill's text and the Contract's CAP-44 line by CIT-P. For the release after 0.1.1.

**Started now** on the owner's line of 2026-11-16 14:5x ("Launch leads now for the two new tickets … nothing blocks building them"); it lands in the release after 0.1.1.

**Path case 2026-11-16 15:3x (P-W2-192-P1 (a), P2 (a); the CTO, DEC-1156 (7); listed for the owner's reading):** the tests run returned DONE (30 cases, 5a9a6ca7a). Other tickets' adoption cases run A3 straight after A2, which stage AS now precedes: the ticket gains `src/gov/adopt/project.py` (the stage chain, the engineer's) and the shared support helpers of W1-41, W2-23, W2-88 and W2-190 (acceptance folders: an independent test designer's change, each case's assertion unchanged, AS run before A3). P2 (a): F1's owner route stays as the cases state (AS and A3 leave every gap's answer empty). The kernel CIT-P (the adopt skill, CAP-44's line) comes back once the code is green.
