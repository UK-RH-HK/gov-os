# The review bundle of 2026-10-22, for sharing

Copies of the 27 files of the orchestrator's list, in reading order, each named with its list number and its original name. They are unchanged byte for byte; `SHA256SUMS` beside this file gives each copy's hash. Nothing here is committed or decided: the drafts wait for the owner's review (DEC-889 item 14).

Read 01 and 02 first. 01 holds rows 03 to 17 in one file.

| # | File | What it is | |
|---|---|---|---|
| 01 | `01-ALL-DRAFTS-AND-PACKAGES.md` | Rows 03 to 17 in one file, in order, each part under a heading naming its source. It also holds P-IS-1 to P-IS-7 in full, the p95 question and DEC-898's text | MUST |
| 02 | `02-I-SYNTHESIS.md` | Lens I's synthesis: the diagnosis, the counts, what fails open, the changes by ticket, the retirements, all 16 packages | MUST |
| 03 | `03-00-INDEX.md` | The index: the decisions in work order, with the drafts each one assumes | MUST |
| 04 | `04-07-REPIN-PLAN.md` | The two re-pins: what each carries, the order before it, the owner's acts, the rollback | MUST |
| 05 | `05-01-W2-66-ticket.md` | W2-66's ticket file: selection and evidence, the test map | MUST |
| 06 | `06-02-W2-66-card.md` | W2-66's WBS card | MUST |
| 07 | `07-06b-W2-07-ticket.md` | W2-07's ticket file: DEC-896's three KPIs, the commit gates first, the disk reading | MUST |
| 08 | `08-06-W2-07-card.md` | W2-07's card | MUST |
| 09 | `09-03b-W2-68-ticket.md` | W2-68's ticket file: batching, reuse, the two fingerprints, the trial | MUST |
| 10 | `10-03-W2-68-card.md` | W2-68's card | MUST |
| 11 | `11-04b-W2-67-ticket.md` | W2-67's ticket file: test hygiene and the weak tests' revisions | MUST |
| 12 | `12-04-W2-67-card.md` | W2-67's card | MUST |
| 13 | `13-05-W2-57-ticket.md` | W2-57's ticket file: the probe first, the serial-only list, every list entry's route out | MUST |
| 14 | `14-05b-W2-57-card.md` | W2-57's card, replacing DEC-813's live-case KPI | MUST |
| 15 | `15-09-W2-70-ticket-and-card.md` | W2-70 (if P-IS-3 (a) is taken): the two nested reruns retired | MUST |
| 16 | `16-08-corrections-P-IS-5.md` | P-IS-5's corrections to the W2-65, W2-69 and W2-66 ticket files | MUST |
| 17 | `17-10-register-draft-DEC-899.md` | The register entry for the owner's answers (written for the recommended options; edited to the actual answers before commit) | MUST |
| 18 | `18-I1-guard-launcher-sandbox.md` | Lens I, area 1: the guard, the launcher, the sandbox | SUPPORT |
| 19 | `19-I2-close-checks-ratchet.md` | Lens I, area 2: the close, the checks, the ratchet | SUPPORT |
| 20 | `20-I3-retrieval-context-resume.md` | Lens I, area 3: retrieval, context, checkpoints, resume | SUPPORT |
| 21 | `21-I4-records-plan-rest.md` | Lens I, area 4: records, the plan, tickets, the rest (PARTIAL) | SUPPORT |
| 22 | `22-TOOL-TRIALS-2026-10-22.md` | The tool trials, with lens H's completed trials first (32 of 32 planted faults) | SUPPORT |
| 23 | `23-H-test-strategy.md` | Lens H's report, the test strategy | SUPPORT |
| 24 | `24-tooltrials-run.txt` | The trial runner's log | SUPPORT |
| 25 | `25-rest.log` | Lens H's rest run, raw | SUPPORT |
| 26 | `26-analysis_a6.json` | Lens H's planted-fault results, raw | SUPPORT |
| 27 | `27-analysis_b2.json` | Lens H's mutation results, raw | SUPPORT |

Sources:
- 01 and 03 to 17: `.gov-runtime/scratch/orchestrator/drafts/review-bundle/`.
- 02, 18 to 21 and 23: `docs/assessment/2026-10/` (committed `210721e0`, and lens H's earlier).
- 22: `governance/project/orchestration/packages/`.
- 24: the orchestrator's `log/tooltrials/20261022-0017/run.txt`.
- 25 to 27: `/tmp/gov-os-assessment-H/logs/` (copied here so they survive a reboot).
