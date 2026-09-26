# BR-ARCH-RULING-2: grading interpretations D-1..D-5, and the choice of CONTROL-A

| Field | Value |
|---|---|
| Record | Orchestrator ruling (2026-09-26). It answers REPAIR-1 §8.1 (BR-AR-0016). **It is not an owner decision.** A verifier may challenge it. |
| Principle | Every answer below applies `ARCHITECTURE/DEMONSTRATION_DESIGN.md` §3–§4 **as written**. **No gate's meaning changes.** For D-2 and D-3 the analyst offered alternatives that *would* have changed a gate's meaning. Those alternatives are **not adopted**, so no owner consultation is required. |

| Id | Question | Ruling | Source text |
|---|---|---|---|
| D-1 | Does a citation to a whole document match a sectioned record anchor? | **Yes, by record id**: "A record anchor matches by record id or section." A citation carrying the record id matches. A citation to a section of a different record does not. | §4 G4 |
| D-2 | Is a must_state fact bound to its stage or to its chain? | **To its stage**: "[R] Each must_state fact is present in the stage's claim." The run-2 test-author must place each fact on the stage whose claim naturally states it. That is authoring guidance, not a rule change. | §4 G4 |
| D-3 | Are AUTH-1..4 gated? | **Yes, under G3**: "checked on the packet by the deterministic grader, and on the answers by the rubric." The rubric checks the answer side and quotes the text it judged. | §3.5; §4 G3 |
| D-4 | Is a read of RUN's own task inputs or orchestrator metadata an undeclared read? | **No**, when the file is under `run-<n>/` and is listed as a task input or in the orchestrator's protocol notes. It is not corpus. Every read of corpus must still be declared. | §4 G7 ("undeclared reads" concerns corpus reads) |
| D-5 | What counts as packet bytes for G7? | The **main packet plus every supplementary packet**, as manifested and budgeted. Task inputs count once. Any raw, unbudgeted query output the agent chooses to save counts in full. | §4 G7 ("the main packet plus every supplementary packet") |

## CONTROL-A: the visible regression control, used by R1-CTRL and R1-INT

It is chosen so that it overlaps **neither Review 8 nor the graded CTRL-1..3**, so builders cannot tune against a
graded question:

> **CONTROL-A.** Why does renaming or removing a certification test break `gov contract verify`? Which contract
> capability or decision requires the governed evidence map? Where is the check enforced in code, and which tests
> prove it?

**CONTROL-B** is the held-out multi-batch control for R1-MB. The orchestrator chooses it only when dispatching R1-MB
and never shows it to builders.
