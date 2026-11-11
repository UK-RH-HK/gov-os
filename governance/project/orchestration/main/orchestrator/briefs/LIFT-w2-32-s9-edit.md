# W2-32 S9 re-worded, option (a1) (DEC-1129 (1))

Read `LIFT-common.md` first, **with one change: you edit two files in the main tree**,
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-0pyc.md` (W2-32) and
`/home/usain/Dynamic-Agentic-Engineering-OS/docs/changes/W2-32-evidence.md`, and nothing else; report to
`.gov-runtime/scratch/orchestrator/drafts/w2-32-s9/EDIT-REPORT.md`. Role: product-spec helper, Sonnet high, class C1. You do
not commit; the CTO does. Read DEC-1129 (1) in the register first.

## The edit (from `governance/project/orchestration/packages/W2-32-S9-DISPOSITION.md` §3, option (a1))
1. S9's line replaced by the (a1) line word for word as the package gives it, ending `[re-worded, DEC-1129 (1)]` (the
   package wrote DEC-1126 (6); the owner's decision is DEC-1129 (1): cite both); add a `Verify:` clause naming how it is
   checked (the S9 cases of `tests/acceptance/W2-32/`, re-pointed to the end-to-end figure; FRESH-80-RESULT's figures).
2. The title's "the hit@5 85 row" (or its words) changed to "the memory line", as the package says.
3. DEC-1097, DEC-1098, DEC-1129 added to `sources` if missing.
4. The evidence note's S9 row rewritten with the 80's figures and where they are recorded; the stale "no improvement
   round has run yet" replaced by what ran (S7, S8, S11, the pool), each with its record.
Keep every other line, status, acceptance criterion and field. Checks: the YAML front matter parses; the structural
pass (`python3 .gov-runtime/scratch/orchestrator/tools/structural_pass.py /home/usain/Dynamic-Agentic-Engineering-OS`) ok;
`PYTHONPATH=src python3 -m gov.context.context_check` no new error (DAEO ids, never W2 ids, in `sources`).

## Then, for the test designer (not you)
In your report, write the exact brief text for an independent test designer: the README's S9 row and
`w2_32_record.py`'s `s9_state` and S9 cases re-pointed to the end-to-end figure (`Rewrite-Reason: DEC-1129 (1)`), with
the files, the KPI line, and the check (`gov accept W2-32`, scoped). Return the twelve fields, short. Estimate 30-45 min.
