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
| Runs to green | the number of acceptance runs (`gov accept <W2>` or the folder's pytest run) from the engineer's first commit to the first all-green `gov accept`, read from the lead's and helpers' transcripts |
| Send-backs | the times the lead sent the engineer back for a red that was the change's |
| Landing reds | reds on the merged tree at the landing check that were the ticket's, plus reds traced to the ticket in the next full suite |
| After-landing fixes | fix commits citing the ticket within 7 days of its landing |
| Cost and time | the lead's reported cost; engineer-start to green, in minutes |

## Baseline: earlier C3 tickets with Opus engineers
Filled by the baseline helper (2026-11-19): see the table below once written.

## The trial tickets
| Ticket | Engineer model | Test designer model | Runs to green | Send-backs | Landing reds | After-landing fixes | Cost | Minutes |
|---|---|---|---|---|---|---|---|---|

## C3 text checks by the CTO
| Date | Change | Written by | CTO's check |
|---|---|---|---|

## Result
(to the owner when both trial tickets have landed: holds, or the role returns to Opus)
