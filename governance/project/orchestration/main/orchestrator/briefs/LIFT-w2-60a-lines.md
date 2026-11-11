# W2-60a takes RUBRIC-2's lines now (DEC-1126 (3), DEC-105 option "apply now")

Read `LIFT-common.md` first, **with one change: you edit one file in the main tree**,
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-cv58.md` (W2-60a), and nothing else; the closes are paused
while you do. Your report goes to `.gov-runtime/scratch/orchestrator/drafts/w2-60a-lines/REPORT.md`. Role: product-spec
helper, Sonnet high, class C1 (DEC-1120). You do not commit; the CTO does.

## The edit
`governance/project/orchestration/packages/AUDIT-NIGHT-1/w2-60a-options.md` §2 and §5 item 1 give it exactly, from
`packages/RUBRIC-2-APPLY.md` §3: replace success lines 3, 4 and 9; amend line 8 (the launch record's fields); add
S4'' if §2 gives it and the one failure line; add `governance/project/criticality.yaml` and its reader to
`allowed_paths` (find the reader's path from RUBRIC-2-APPLY; if no reader exists yet, name the path RUBRIC-2-APPLY
proposes, under `src/gov/launch/`); add DEC-1119, DEC-1120, DEC-1014, DEC-1126 to `sources`; fix the body's "W2-11"
to "W2-33" (§3 item 2). Mark each changed line `[changed, DEC-1120 (5), DEC-1126 (3)]`. Keep every other line,
status, acceptance criterion and field as it is. Read DEC-1120, DEC-1119, DEC-1014 and DEC-1010 in the register first.

## Checks
`python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]).read().split('---')[1])" .tickets/DAEO-cv58.md`; the
structural pass (`python3 .gov-runtime/scratch/orchestrator/tools/structural_pass.py /home/usain/Dynamic-Agentic-Engineering-OS`):
schema, claims and authority ok; `python3 -m gov.context.context_check` with `PYTHONPATH=src` from the main tree: no
new error (it refuses work ids such as W2-xx in `sources`; use DAEO ids there).

## Return
The twelve fields, short; per line old → new; the review-round question (DEC-1010's two-round cap: W2-60a had three
rounds; the options package reads the new lines as a new scope, so the count restarts; say what the register says).
Estimate 30-45 min.
