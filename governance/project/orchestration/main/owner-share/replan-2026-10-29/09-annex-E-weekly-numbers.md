# E-weekly: the four weekly numbers (DEC-930 item 2), Wave 2 from 2026-10-16 to 2026-10-29

Research agent E's findings (read-only, 2026-10-29), written down by the orchestrator. **Weeks:** ISO weeks, Monday to Sunday.
- W42 counts only Wave 2's part, Fri 16 to Sun 18 Oct (3 days).
- W43 is 19 to 25 Oct (7 days).
- W44 runs from 26 Oct to 29 Oct at about 13:00 (4 days, not finished).

## 1. Closes per day

Sources: the commits "<id> closed by gov close (exit 0, …)" on w2/integrate, which match the 13 close records in `docs/close/*/CL-*.md`.

| Week | Clean closes | Per day | Tickets (close commit) |
|---|---|---|---|
| W42 | 0 | 0.00 | none |
| W43 | 5 | 0.71 | 20 Oct: W2-53 (`a1565e56`). 21 Oct: W2-02 (`e52ad8a2`), W2-54 (`55162ea2`). 22 Oct: W2-62 (`d7daf01b`), W2-50 (`01488b72`) |
| W44 | 8 | 2.00 | all on 27 Oct: W2-70 (`23c24700`), W2-66 (`f8d1f60a`), W2-72 (`6c439d8a`), W2-59 (`f0f933e1`), W2-65 (`be18d1c7`), W2-73 (`74c08ed8`), W2-74 (`182823e4`), W2-69 (`07a8d624`) |

**Closed with tk close (not clean closes):**
- W1-42 on 16 Oct (DEC-717, `c215459d`)
- W1-43 on 16 Oct (DEC-718, `d2faf82c`)
- W2-01 on 17 Oct (DEC-757, `f15ac648`)
- W2-48, withdrawn on 21 Oct (DEC-880, `6cce71bb`)

W2-75 (DAEO-ebmh) was still closing on 29 Oct, so it is not counted.

## 2. Refusals caused by the orchestrator's own tooling or process

Sources:
- Non-zero exits in `.gov-runtime/scratch/orchestrator/log/close-queue-*/close-*.exit` and `queue.txt`.
- For W42 and 19 Oct, `log/close-W1-42.json`, `log/W2-01-close.json` and `log/close-DAEO-7rr2{,-2,-3}.json`.

Classes:
- **S:** a register entry or package states that the orchestrator caused it.
- **E:** the cause is an orchestrator file or commit, named in the orchestrator's own commit or record.
- **C:** an orchestrator artefact contributed.
- **N:** not the orchestrator.
- **U:** unclear.

| Week | When (exit) | Ticket | Cause | Class | Source |
|---|---|---|---|---|---|
| W42 | 16 Oct 05:11 | W1-42 | 22 findings, mixed, including an orchestrator decision-record commit `76ce6416` and PROBE_MISSING | U, possibly partly | DEC-717 |
| W42 | 17 Oct 13:46 | W2-01 | Probe invalid after an integration-side ticket-file edit; CONTEXT_FAILED (DEC-750 not in the store); stale checkpoint; "the refusals are not its own" | U, possibly partly | DEC-757; W2-01-close.json |
| W42 | 18 Oct 01:53 | W2-53 | context-reproducibility over its 60 s limit | N | P-W2-53 §2.1 |
| W43 | 19 Oct 10:44 | W2-53 | STORE_STALE in the log; P-W2-53 says W1-30's load case | U, sources conflict | close-DAEO-7rr2-2.json; P-W2-53 §2.2 |
| W43 | 19 Oct 12:01 | W2-53 | W1-30 r13 case under load | N | DEC-823 |
| W43 | 20 Oct 09:54 | W2-53 | Three of four causes were "the orchestrator's own records" | S | DEC-867 |
| W43 | 20 Oct 11:07 (exit 4) | W2-53 | ESCALATION_BLOCKED, a consequence of the earlier refusals | not counted | DEC-870 |
| W43 | 20 Oct 11:52 (exit 1) | W2-54 | TREE_NOT_COMMITTED: orchestrator package `P-W2-53.md` untracked | E | close json; commit `3bef1393` |
| W43 | 20 Oct 13:49 | W2-53 | Close-queue checkpoint commits had no `Implements:`, plus W1-38 under load | E | DEC-871; P-W2-55 |
| W43 | 21 Oct 02:37 (exit 1) | W2-02 | TREE_NOT_COMMITTED: the orchestrator's sync copied test-cache stores | E | commit `c3b32d31` |
| W43 | 21 Oct 15:36 | W2-02 | W1-08 red, "my slip", plus W1-07 under load | S | DEC-885 |
| W43 | 21 Oct 17:26 | W2-02 | W1-07 and W1-25 reds under load, and a git gc race caused by the orchestration record's growth | C | P-W2-02-C3 §2 |
| W43 | 22 Oct 00:11 | W2-63 | No acceptance folder (a gap in the close), plus load and network | N | P-W2-63-C1 |
| W43 | 22 Oct 11:40 | W2-50 | PROBE_INVALID (structural), and the DEC-892 entry, "the orchestrator's slip" | S | DEC-894 |
| W43 | 22 Oct 13:28 | W2-58 | WORK_WITHOUT_TASK: "the cause is the orchestrator's records" | S | P-W2-58-C1 §5 |
| W44 | 26 Oct 23:24 | W2-70 | Reds from the re-pin's settings regeneration, not swept | S | DEC-925 basis and item 2 |
| W44 | 27 Oct 19:52 | W2-66 | `ACT-P-TRACE-IMPL-1.patch` left under orchestration/ | S | ACT-P-TRACE-IMPL-1 lines 4–5; `508571d3` |
| W44 | 28 Oct 21:31 | W2-58 | W2-54 fixture timing out under load | N | DEC-937 |

**Gate stops before a close** (no attempt spent; source: `queue.txt`):

| Week | When | Ticket | Cause | Class | Source |
|---|---|---|---|---|---|
| W43 | 20 Oct 16:04 | W2-54 | gov check not green; cause not found | U | queue.txt |
| W43 | 21 Oct 22:39 | W2-62 | `0e686111`, `6e4b2750` and `162f17ea` have no `Implements:`; all three are `Role: orchestrator` commits | E | queue.txt; the commits' trailers |
| W43 | 22 Oct 13:56 | W2-62 | The secrets check's chance red | N | DEC-897 |
| W44 | 27 Oct 17:22 | W2-66 | Traceability red: briefs written by the orchestrator put a role in `Implements:` | S | P-TRACE-IMPL-1 |

| Week | Refused closes | Caused by the orchestrator (S+E) | Contributing (C) | Gate stops caused by the orchestrator |
|---|---|---|---|---|
| W42 | 3 | 0 (2 unclear) | 0 | 0 of 0 |
| W43 | 12 | 7 | 1 | 1 of 3 |
| W44 | 3 | 2 | 0 | 1 of 1 |

## 3. Cost per week (measured only)

The figure is the Claude CLI's `total_cost_usd`, an API-price figure, not an invoice.

Sources:
- `.gov-runtime/scratch/orchestrator/log/*.json`: lead returns `W2-*-A5-run*.json` and lens assessments `assessment-*.json`.
- `~/gov-os-worktrees/*/.gov-runtime/scratch/lead/log/*.json`: workers.

Each figure is assigned to a week by the file's modification time.

| Week (USD) | Leads | Assessments | Workers (surviving worktrees only) | Measured total |
|---|---|---|---|---|
| W42 | 133.75 (33 returns) | 0 | 124.97 (39 files) | 258.72 |
| W43 | 322.79 (45 returns) | 1,051.44 (lenses A–G and S on 19 Oct, H on 21 Oct, I1–I4, I4-resume and IS on 22 Oct) | 247.64 to 303.85 | 1,621.87 to 1,678.08 |
| W44 | 69.89 (10 returns) | 0 | 127.95 to 146.68 | 197.84 to 216.57 |

**Why the worker figure is a range:** resumed worker sessions keep their session id, and their cost appears to add up across resumes (W2-58 td-1 to td-4: 9.06, 16.57, 20.91, 26.98). The low end counts only each resume's increase; the high end sums every file.

**Not covered:**
- the orchestrator's own sessions;
- workers of removed worktrees (most closed tickets: W2-01, -02, -48, -50, -53, -54, -59, -62, -66, -69, -70, -72, -73, -74);
- probes and auditors not in these logs;
- the owner's sessions.

No digest records a `/usage` reading (DEC-838).

**Added by the orchestrator:** W44 since the agent's count includes W2-71 run 1 (7.01 USD), W2-75 run 1 (5.50), W2-68 run 1 (17.53), W2-07 run 5 (2.40) and W2-57 run 3 (2.77), per their `log/*-A5-*.json`, if their file times fall in the window counted. That is to be reconciled when the assessment is finalised.

## 4. The owner's decisions per week

Source: the Status lines in `docs/DECISION_REGISTER.md`, dated by their "owner, <date>" or "delegated, <date>". Each register entry counts once.

| Week | Owner | Delegated | Notes |
|---|---|---|---|
| W42 | 66 (DEC-715 to DEC-794, the owner entries) | 17 | DEC-735 and DEC-738 were delegated, then accepted by the owner. The owner count includes the Wave 1 exit decisions DEC-715 to DEC-718. |
| W43 | 99 (97, plus the since-superseded DEC-869 and DEC-876) | 24 | 18 delegated, plus DEC-863, -864, -890, -913 and -917 (accepted by the owner later), plus the superseded DEC-875. DEC-905 is mixed and counted in neither column. |
| W44 | 15 (DEC-922 to DEC-925, DEC-927 to DEC-936, DEC-938) | 2 (DEC-926, DEC-937) | DEC-939 and DEC-940 (2026-10-29) are not yet in the register; they are drafted. |

## Gaps

- Five orchestrator attributions come from its own commits and files, not from a register entry that states the cause.
- For W2-53's 19 Oct refusal, the log and its package disagree on the cause.
- The cause of one gate stop (W2-54, 20 Oct at 16:04) was not found.
- Whether cost adds up across resumed sessions is not proven, which is why the worker figures are ranges.
- **Preserve before removal (lesson):** workers' result files should be kept before their worktrees are removed, or their cost cannot be measured.
