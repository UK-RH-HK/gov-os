# The C3 trial: Sonnet engineers, Opus test designers (the owner, DEC-1222 (2))

`docs/emergency-2/C3-TRIAL.md` · the CTO · opened 2026-11-19 · result to the owner when both trial tickets have landed

**The owner's words:** "the next two C3 code tickets run with Sonnet engineers and Opus test designers; compare their
runs to green and their landing reds with earlier C3 tickets, and tell me the result. C3 text (the Contract, the Charter,
kernel text) is written on Sonnet, and you check it. The memory measure's reader and grader stay as DEC-1098 defines
them. If quality holds, the rubric changes for good; if not, that role returns to Opus."

## Rules while it runs
- **C3 code** (a ticket whose code paths fall under C3 in `governance/project/criticality.yaml`): the independent test
  designer runs **Opus** (the spawn names `model: opus` and its prompt carries `Task: <ticket id>`); the engineer runs
  **Sonnet** (no model named). The lead runs Sonnet as every lead.
- **C3 text** (the Contract, the Charter, kernel text: role files, templates, skills, CLAUDE.md, AGENTS.md): written on
  Sonnet; the CTO reads every such change before it lands and records the check below.
- **Unchanged:** the memory measure's reader and grader (DEC-1098); every C2 and C1 role (Sonnet).
- **The trial tickets** are the first two C3 code tickets whose engineer starts after 2026-11-19 16:46. A fix under a C3
  ticket does not count as one of the two (it is not a ticket), but its figures are recorded beside them.

## What is compared
| Measure | How it is counted |
|---|---|
| Runs to green | the number of acceptance runs (`gov accept <W2>` or the folder's pytest run) from the engineer's start to the first all-green run of either, read from the lead's and helpers' transcripts by `.gov-runtime/scratch/orchestrator/tools/c3_trial_measure.py` |
| Send-backs | the times the lead sent the engineer back for a red that was the change's |
| Landing reds | reds on the merged tree at the landing check that were the ticket's, plus reds traced to the ticket in the next full suite |
| After-landing fixes | fix commits citing the ticket within 7 days of its landing |
| Cost and time | the lead's reported cost; engineer-start to green, in minutes |

## Baseline: earlier C3 tickets (Fable engineers under DEC-1215, and Opus)
Measured by the research helper on the evening of 2026-11-19 from the leads' transcripts, `log/leads/<lead>.json`, the night
notes, the morning brief §1, §2, §6, the tickets' close paragraphs and git on `w2/integrate`. Ten C3 code units of 18 to 19
November, every one led by Sonnet. C3 was confirmed by each ticket's changed paths against `criticality.yaml`; the
engineer and test-designer model is the model of each helper's own transcript, not the model the spawn asked for (the hook
refused an Opus engineer spawn for W2-200 and W2-201 and the Fable one ran). The same row comes from
`.gov-runtime/scratch/orchestrator/tools/c3_trial_measure.py <lead> [--ticket W2-nnn] [--merge SHA] [--evidence]`.

| Ticket | Lead | Engineer model | Test-designer model | Runs to green | Send-backs | Landing reds | After-landing fixes | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|---|
| W2-201 rubric in code (DAEO-k1us) | k1-usage | Fable | Opus (S1-S8), Fable (S9, S7 redo) | 5 (3 from first commit) | 0 (1 message after a ticket change, not a red) | 0 of its own (the 1 collection error was the CTO's new unit file); a live defect at the land: the helper hook refused the leads' Fable helpers for 2 min | 1 (c3c5a836f, +2 min, test first) | $35.02 | 29 |
| W2-200 M1, `gov context` retired (DAEO-r4xc) | m1-context | Fable | Opus | 5 (5); the first all-green run was the lead's, after the designer fixed 2 wrong cases | 0 (the one message went to the designer) | 5 at the landing check (4 W2-194 cases: new DECISION_NOT_FOUND refused a fixture ticket; 1 W2-203 doctor case flagged M1's own path) + 1 in the full suite (W2-61 q04, file removed) = 6 | 1 (88002d402, W2-61's case, shared with W2-205); 2 fixes and an amended KPI line went in on the landing branch before the land | $68.74 | 93 |
| W2-202 L2 A1, A3, A4, A5 (DAEO-l2bd) | l2-build | Fable | Fable | 1 (0: the run came 13 s before its first commit) | 0 | 0 (the 14 W2-115 cases red were red at the base: not counted) | 2 (f1fa2e00e: the runner's keep_report; an acceptance run that names no test; found while W2-206 was built, 1 h on) | $48.54 | 39 |
| W2-203 register's exit (DAEO-r3gx) | register-exit | Fable | Fable | 5 (5); the first green `gov accept` was run 7, minute 55 | 1 (the archived-id findings; 2 other reds were the designer's cases) | 2 collection errors at the landing (two unit files' bare sibling import) + 4 in the full suite (W2-13 lexical policy, W2-86 embedding guard, W2-61 visible x2) = 6 | 5 (136080645 doctor; df647f986, 1ed81c869, 339d7b2f1, b8ffb49b6: cases of W2-13/86/61 and its own S5, S2) | $41.07 | 35 |
| W2-204 memory measure, adopted repos (DAEO-ma4q) | memaudit-adopted | Fable | Fable | 2 (2); the first green `gov accept` was run 3, minute 77 | 0 | 0 (in no full suite yet: not measured) | 0 | $64.68 | 29 |
| W2-206 L2 A6, A8 (DAEO-l2b2) | l2-build-2 | Fable | Fable | 3 (3) | 0 | 0 at the landing + 1 in the full suite (W2-158 after-step case) = 1 | 1 (cb5e4dda2, the W2-158 case) | $33.34 | 45 |
| W2-205 run-time slice 3 (DAEO-rt3s); mixed: C3 is 2 kernel hook files | rt-slice3 | Fable (kernel hooks) + Sonnet (run-time code, C2) | Fable | 3 (3) | 0 | 0 at the landing + 2 in the full suite (Stop-hook unit case; W2-61 q20 heading) = 2 | 2 (1fcaac1c8; 88002d402 shared) | $12.16 | 33 |
| W2-208 kit after Emergency 2 (DAEO-kt8e; a fix under W2-17) | kit-e2 | Opus | Opus | 1 (1) | 0 | 0 | 0 | $19.14 | 9 |
| W2-201 fix X1-X5 (not a ticket) | rubric-tickets | Opus | Opus | 1 (1) | 0 | 0 | 0 | $18.89 | 16 |
| W2-201 fix X6-X8 (not a ticket) | rubric-tickets-2 | Opus | Opus | 2 (2); the 1 red was the designer's wrong case | 0 (the message went to the designer) | 0 recorded | 0 | $10.94 | 21 |

**Fable engineers** (W2-200, 201, 202, 203, 204, 206; W2-205 is mixed and left out): median 4 runs to green (1, 2, 3, 5, 5, 5), 0 send-backs, 0.5 landing reds (0, 0, 0, 1, 6, 6), 1 after-landing fix (0, 1, 1, 1, 2, 5), $44.81, 37 minutes (29 to 93).
**Opus engineers** (W2-208, X1-X5, X6-X8; three small units, no feature ticket among them): median 1 run to green (1, 1, 2), 0 send-backs, 0 landing reds, 0 after-landing fixes, $18.89, 16 minutes (9 to 21).
**What it shows and cannot:** n is 6 and 3, so a median moves with one ticket; the Opus units are all small fixes or a chore (4 to 6 source files, tests written for the fix), the Fable units are feature tickets (3 to 20 source files, median 8), so the groups differ in kind as much as in model, and no C3 feature ticket of the period had an Opus engineer (the Sonnet trial has a Fable feature baseline here, not an Opus one; an earlier window, before the Fable substitution, may hold Opus C3 feature tickets: not searched); the Fable reds are mostly interactions with other tickets landing the same night (W2-203's archive, M1's decision check), not the engineer's code alone, and the test designer (Opus on W2-200 and the first part of W2-201, Fable elsewhere) cannot be separated from the engineer; cost is the lead's total (lead, designer and engineer together), not the engineer's.

How the numbers are counted (the script does the same): an acceptance run is a `gov accept <W2>` call or a pytest run naming `tests/acceptance/<W2>` whole (with other folders too; not one file, not `-k`), by the engineer or the lead; the green is the first run of those with no red in its output, which was the folder's pytest run, not `gov accept`, for W2-203 and W2-204 (the `gov accept` figure is in brackets there); minutes run from the engineer's start (the page counts runs from its first commit: that figure is in brackets, and it undercounts when the first run comes just before the first commit). A send-back is a lead message to the engineer about a red that was the change's; a ruling or a changed ticket is not one. Landing reds are the ticket's own reds at the landing check (its close paragraph, the night notes) plus reds the full suite of 05:17 (nine reds) and the next test-designer pass traced to it; the full suite started 16:29 had not ended, so nothing after it is counted. W2-199 (rt-slice2) is not in the table: its paths are all C2 and its helpers ran Sonnet (2 runs, 1 send-back, $17.99, 104 min), which is a C2 Sonnet reference only.

## The trial tickets
| Ticket | Engineer model | Test designer model | Runs to green | Send-backs | Landing reds | After-landing fixes | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|

## C3 text checks by the CTO
| Date | Change | Written by | CTO's check |
|---|---|---|---|

## Result
(to the owner when both trial tickets have landed: holds, or the role returns to Opus)
