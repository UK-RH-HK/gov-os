---
type: probe
task: DAEO-l78m
kind: "narrow independent check of the S-STAGES reopen (DEC-1197 (2); DEC-1154; not a round, DEC-1010)"
reviewer_session: 37e1680d-15a6-42cc-8092-8460e86d5598
reviewer: "au-1, independent-auditor, claude-opus-5-5, effort high, C2 (promoted: a fail-open finding), read-only"
implementer_session: ff849d94-6fc9-48f4-89e8-9df1743fcce5
implementers: ["td-1-2 8cc64460-dff9-45c5-917f-1bcc2f45c3b1 (independent-test-designer, 6032affcd904)", "td-2 ff849d94-6fc9-48f4-89e8-9df1743fcce5 (independent-test-designer, 78c2a7cd6e48)"]
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: b3ed06d8eaae02fba698ab2c4904a2eb3d036569
probed_range: b183a850d..b3ed06d8e
date: 2026-11-16
decisions_applied: [DEC-1197, DEC-1154, DEC-1010, DEC-801, DEC-808]
---

# Narrow check: W2-81 S-STAGES, the judge's stage list

The owner reopened W2-81 for S-STAGES (DEC-1197 (2), P-W2-81-VERDICT-1 (b)): the judge counts A7 and A10 as built from
`gov.adopt.command.STAGES`, not `gov.adopt.project.STAGES`. Two test-designer batches made the change:
`6032affcd904` (`built_today()` reads `command.STAGES`; self-tests and README) and `78c2a7cd6e48` (the lead's decision
within S-STAGES' "never passed": the product's lite gate commits its record with `result: fail` when the gate fails, so
an A7/A10 record whose `result` is not exactly `pass` is MALFORMED, never PRESENT). The lead merged both in `b3ed06d8e`.

A fresh independent auditor, read-only, with the brief carrying JUDGEMENT.md word for word, checked exactly
`b183a850d..b3ed06d8e` against S-STAGES, F1 and F2. It found:

- The diff touches only `w2_81_judge.py`, `test_w2_81_judge.py` and `README.md`.
- `w2_81_judge.py:147-150`: `built_today()` takes A7 and A10 only from `command.STAGES` (`src/gov/adopt/command.py:20`).
  `project.STAGES` (`project.py:22`) no longer plays a part.
- `record_name("A7")` and `record_name("A10")` equal `lite_gates.record_path(...)`.
- `w2_81_judge.py:215-217`: an A7/A10 record whose `result` is not `"pass"` is MALFORMED. The auditor probed records in
  the real gate's format: `pass` gave PRESENT; `fail`, `PASS` and `True` gave MALFORMED; a missing record gave ABSENT.
- `w2_81_judge.py:799-802, 863, 879-889`: with A7/A10 built, the stage status is the record's own state; every stage
  not PRESENT is a reason; a judge error is ERROR. So an absent, unreadable, malformed or failed A7/A10 record is always
  NOT_READY and named, never NOT_BUILT and never passed.
- No other rule changed. The suite gave 318 passed, 0 skipped (the base had 300).

The lead's own runs at `b3ed06d8e`: `gov accept W2-81` gave outcome pass, 318 passed, 0 failed, 0 skipped. The scoped
run (`lead_verify`, DEC-968) gave 7199 tests, 2 failed, 6 skipped. Neither red is this change's: both come from
`.tickets/DAEO-kfn1.md:59` (W2-189's ticket, at the claim commit `b183a850d`), whose non_goals item holds an unquoted
`: ` (`tests/acceptance/W1-08/test_w1_08_ticket.py:88`, `tests/acceptance/W2-02/test_w2_02_green_here.py:62`).

## Findings (rows, not a round)

**R1.** `tests/acceptance/W2-81/w2_81_judge.py:802,863` and the README's "Found and missed, for a stage".
The KPI line says MISSED and FOUND. The judge reports a stage's record state: ABSENT, UNREADABLE or MALFORMED for the
missed form, PRESENT for the found form. This is the vocabulary stages always had, and the README states the mapping.
The stage is named, the verdict is NOT_READY, and it is never NOT_BUILT and never passed.
Ordinary work: yes, because anyone reading the run's result sees ABSENT where the ticket says MISSED.
Consequence: other (wording only; the verdict and the named reason are the same either way).
Scope: in. A row.

**R2.** `tests/acceptance/W2-81/w2_81_judge.py:215-218`.
The judge checks only `result` on an A7 or A10 record, so a hand-made record holding only `result: pass`, or naming a
different `stage`, is PRESENT. The README says so.
Ordinary work: no, because the only writer is `lite_gates.gate` (`lite_gates.py:244-255`), which writes `stage`, the
checks and the conditions, and writes `result: pass` only when no check failed. A minimal or mislabelled record has to
be made by hand on purpose.
Consequence: fails open (only in that deliberately made case).
Scope: in. A Wave 3 hardening row.

```verdict
{"kpis": [{"kpi": "S-STAGES", "verdict": "pass", "findings": [{"id": "R1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "R2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}], "reviewer": "independent-auditor, fresh read-only session; not the author"}
```

The auditor's full return: `.gov-runtime/scratch/lead/log/au-1.result.txt` in the W2-81 worktree.
