---
milestone: "Retrospective 2026-11, part 4: ceremony against value (every rule, gate, check, record and practice in force)"
commit: 4416b8403a386da14cd2a9f7a631846e4a8e2a1b
pack_sha256: "none: no gov context pack was given; inputs are the repository at the commit and the files the brief named"
task: retro-2026-11-P4
decisions: [DEC-1047, DEC-1158, DEC-1204, DEC-1010, DEC-801, DEC-820, DEC-953, DEC-954, DEC-1154, DEC-1156, DEC-1157, DEC-866, DEC-1205, DEC-1045, DEC-1137, DEC-974]
written: 2026-11-16 17:22 (from date)
author: independent auditor (fresh, read-only; wrote none of the audited files)
---

# P4: ceremony against value

**Where this file is.** The brief asked for `.gov-runtime/scratch/orchestrator/drafts/retro-2026-11/P4-ceremony.md`. The guard's
rule 5 refused it (an auditor writes only under docs/probes/, docs/audit/, docs/assessment/, the CTO's reviews/ folder, its own
scratch or /tmp). It was refused once. I did not retry or respell the call. The report is here, in reviews/, which rule 5 allows.
This is itself evidence for row S10: the CTO's brief named a path its own guard refuses.

**Yardstick.** The aim paragraph of DEC-1047 still stands: stop drift, give the agents memory, help with spec and KPIs, keep roles
separated, govern the traffic and not a city. DEC-1158 (1) superseded only DEC-1047's decision items (1) and (2), which were the stop
and the investigation (DEC-1073 rule 6 asks me to name both ids). Every row below is judged by DEC-1204's golden rule. The two lines
say what the item guards against: "Ordinary work: yes|no, because …" and "Consequence: fails open|loses work|other". "Reversed by"
says what evidence would change the verdict (DEC-1014).

**The counts behind the costs (all read-only, counts only):**
- **The guard's call log** (`~/.gov-os/guard-calls/*.jsonl`, 2026-11-09 to 16): 143,443 lines. 60,448 of them come from replay
  or check sessions (guard-fix-3/4, agf5, guard4-check, refusal-scan, walls-check). Those sessions made 95 % of the denials and
  should not be in the live log.
  - Real sessions (UUID ids, 1,028 of them) made 82,995 calls. 298 were not allowed (0.36 %): error 70, run-time listing 47,
    g14 35, rule 5 34, 2b-line 24, secrets 21, hidden 16, unresolved revision 16, rm 13, rule 1 7, sudo 6, 2d 3, install 2,
    held-out 2, 2c 1, ask 1.
  - The guard's own judging time: median 88 ms, p95 210 ms, 2.4 h in total over 8 days.
- **`log/guard-refusals.jsonl`** holds 270 refusals with verdicts: 217 false positives and 53 true. A false positive costs about 1 min.
- **Probe records** (`docs/probes/`): 192 records over 88 tickets. 129 verdict blocks hold 502 findings and 32 KPI lines marked fail.
  Only 25 findings are in the blocking class (in scope, ordinary work, fails open or loses work), which is 5 %.
- **Landings** (`dispatch/dispatch.log`, `land-done.txt`): 90 lands, median 21 min, p90 50 min, 38.8 h in total. 71 closed,
  12 ejected (9 red).
- **The landing select's verify** (`dispatch/inbox/read/*landing-select*`): it ran 17 times for about 4.0 h. Results: 13 RED (1 to
  125 failures), 8 landing-check P1s, 4 GREEN, 1 REFUSED.
- **The CTO's inbox:** 1,219 items read. 151 are guard harvests, 121 lead returns, 114 idle-headroom, 90 lands, 73 structural notices,
  85 helper-watch, 16 spend brakes, 13 dead-man wakes.
- **ACTs:** 61 bundles and 18 applied by the operator agent (11-10 to 11-16), all class (b). 12 of the 61 are ACT-CLAUDE-COPIES-n.
- **Session costs** (return logs, API-equivalent): lead runs $2,686 over 587 runs. Worker logs whose names say reviewer: 331
  sessions, about $1.2k and 76 h. Test designers: 265, about $1.0k. The worker split is approximate because it comes from file
  names.
- **Lead hours lost on 11-12** (`drafts/lead-delay-inventory-measure.md`): 45.2 lost against 70.8 used. Most of the causes were
  lifted by DEC-1157, which is why the night rules and the cap do not appear below.

## Security walls

| # | Item | Where | What it protects | Ordinary work | Consequence | Cost | Fired / caught | Verdict | The change | Reversed by |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | Rule 1: only the test designer writes acceptance tests | `.claude/hooks/pretooluse.py` rule 1, `bash_writes.py` | the builder editing its own acceptance tests (MR-3, the aim) | yes, because an engineer facing a red test "fixes" the test | fails open | low today; 64 FP before GF-6, none since | 7 real denials in 8 days; 2 true in the log | keep | none | a week of real denials that are all FP after GF-6 |
| S2 | Landing G-1: an acceptance-test commit must carry `Role: independent-test-designer` | `tools/land.py` step 1 | the same, for writes the guard lets through | yes, same reason | fails open | seconds per land | no refusal found in the inbox | keep | none | none: it is the backstop that lets S1 stay loose |
| S3 | Rule 2: held-out reads | hook rule 2, `gov.guard.heldout` | qualification material reaching a session | yes, because a broad grep or find reaches it | fails open | negligible | 2 real | keep | none | none |
| S4 | Rule 2: the hidden half, in-tree | hook, `reads._hidden` | a measured session seeing its exam | yes, because of searches over fixtures | fails open | low | 16 real; log 11 FP / 5 true | keep | none | none |
| S5 | Rule 2b: reads and writes of the sets root's hidden folders | hook `sets_root_rule`, path-map `sets_root_hidden` | the same, outside the repository | yes, because of measure scripts | fails open | negligible | 0 real 2b-write | keep | none | none |
| S6 | Rule 2b-line: a Bash line naming the sets root together with a variable, glob, substitution or cd | hook `sets_line_refusal` | a path built at run time into a hidden folder | yes, because of loops over the sets root | fails open | moderate FP | 24 real; log 10 FP / 11 true | scope | once the box (which does not mount the sets root) is live and SANDBOX-1 has a denyRead for it, retire the line rule for those sessions | an OS wall shown not to cover a session kind |
| S7 | Rule 2c: session_hidden (the W2-56 tuner refused `~/.claude/projects`) | hook `session_rules`, path-map `session_hidden` | one ticket's engineer reading raw transcripts | yes, but only on W2-56 | fails open (for that ticket) | negligible | 1 real | scope | lift when W2-56 closes; under DEC-803 it is that ticket's entry criterion | a second ticket needing it |
| S8 | Rule 2d: no writes into `~/gov-os-operator` (but queue/) or the guard's call log | hook `write_rules` | a session altering the operator's install or frozen ACTs | yes, because of a mistyped target in the CTO's session | fails open | negligible | 3 real, 1 true | scope | launched workers are already walled by SANDBOX-1; the box mounts these folders read-only; lift for boxed sessions once the box is live | an unboxed session kind that writes there |
| S9 | Rule 3: reads of secrets and keys | hook rule 3, `reads.py` | a secret printed into a transcript | yes, because of `cat .env` while debugging | fails open (the DEC-820 wall) | FP: heredoc text that names `.env` | 21 real; log 13 FP / 1 true | keep | apply P-GUARD-FP-1 (a): write scripts with the Write tool and run them by path | none |
| S10 | Rule 5: reviewers write only their own records | hook rule 5 | a reviewer fixing what it reviews (DEC-137) | yes, because reviewers like to patch | fails open (independence) | FP | 34 real; log 27 FP / 9 true; refused this brief's own output path | keep | allow `$TMPDIR` and the sandbox's empty home; briefs must name a reviews/ path (this brief did not) | none |
| S11 | g14: role separation on reads | hook + `role_reads.py`, path-map `role_paths` | the engineer reading tests, the test designer reading the implementation (the aim) | yes, because of repository-wide searches | fails open | low | 35 real; log 15 FP / 14 true | keep | none | none |
| S12 | Run-time listing refusal ("names another command gives at run time") | `gov.guard.reads` (runtime) | a computed file list reaching a walled folder | yes, because of `find \| xargs grep` | fails open only where a walled folder lies under the searched root | the worst FP rate: 52 FP / 4 true (93 %) | 47 real, the largest wall class | scope | refuse only when the listing's root is at, in or above a folder walled for this session; let every other listing through | a true refusal with a root outside every walled folder |
| S13 | Unresolved revision (REV_REFUSAL) | hook `Judge`, `decide._expand_token` | a git show of a hidden blob through a variable | yes, because of loops over hashes | fails open (the wall) | FP | 16 real; log 10 FP | simplify | P-GUARD-FP-1 (b): expand shell-local literal assignments (GF-8) | none |
| S14 | R5: a path field that is not a path | hook `_no_path` | the judge being fooled by a NUL byte or a non-string | no, because it needs a crafted call | other | negligible | 0 | keep | none (cheap) | none |
| S15 | Rule 4: installs (ask in the CTO's session, refused elsewhere), sudo | hook rule 4, settings deny `Bash(sudo:*)` | unapproved installs and root | yes, because `pip install` is reflexive | other | negligible | 2 install, 6 sudo, 1 ask | keep | none | none |
| S16 | Catastrophic rm | hook `rm_refusal` | deleting the repository, a .git or a tracked tree | yes, because of `rm -rf $UNSET/` | loses work | low FP | 13 real; log 3 FP / 2 true (one a .git) | keep | scope it so the CTO may delete its own memory files (MEMORY.md keeps a duplicate entry only because the delete was refused) | none |
| S17 | Fail closed on a guard error or the 20 s deadline | hook `__main__`, `deadline` | the guard missing a judgement | yes | fails open (if it failed open instead) | 70 real refusals in 39 sessions, the largest real class | 70 | simplify | keep fail-closed; log the exception class in the call log and fix the top causes | errors traced to genuine timeouts under load only |
| S18 | Guard call log (HMAC jsonl) | hook `record` | evidence for audits like this one | no (records) | other | negligible | 143k lines | simplify | replays and checks must set `GOV_GUARD_CALLS_DIR`: 60k replay lines polluted the live log | none |
| S19 | The guard's shell reading as a whole | `bash_writes.py` 2,783 lines + hook 1,830 lines; ACT-GUARD-FIX-1 to 9 | rules 1, 2b, 2c, 2d, 3 and 5 for Bash | yes | fails open | the costliest security item: 9 (b) ACTs, each reviewed, rehearsed and approved by the owner; 60k replay calls; 217 FP | see S1 to S16 | simplify | after the box is live, carry the static walls (secrets, held-out, sets root, operator folder) as OS mounts in the box and as SANDBOX-1 denyRead; keep shell reading only for rules 1, 5 and g14, which an OS wall cannot express | an OS layer shown unable to carry a static wall |
| S20 | Settings deny lists | `.claude/settings.json` (6), `settings.local.json` (4) | the named key and secret edits, the oracle, push, the memory hidden and verdict sets | yes | fails open | none | n/a | keep | none | none |
| S21 | Quiet-hours PermissionRequest hook | `orchestration/tools/permission_request.py` | a prompt freezing the CTO at night | yes | other | small | not counted | scope | lift when DEC-1205's in-box no-prompt mode is live (no prompts left to queue) | prompts still seen inside the box |
| S22 | gov launch settings refusals (no bypass, --add-dir, disableAllHooks, --bare; guard registered; no sandbox key) | `src/gov/launch/launcher.py:394-509` | a worker without its guard | yes, because of a copied CLI line | fails open | negligible | rare | keep | none | none |
| S23 | SANDBOX-1 (OS sandbox of launched workers, empty network) | `src/gov/launch/sandbox.py` | a worker writing outside its worktree (CLAUDE.md: the only such wall) | yes | fails open, loses work | small (memory: TMPDIR and code-graph quirks) | n/a | keep | none | none |
| S24 | The session box (P-BOX-EXCEPTION-1) | `drafts/session-sandbox/` | CTO, leads and adopters reaching secrets, held-out material, protected branches | yes | fails open, loses work | about 45 min of the owner's time; degradations listed in §6 | not live yet; 18 Wave 3 rows (W1 to W18) kept as rows, which is the golden rule applied correctly | keep | then lift S6, S8, S12 and S21 as duplicates, and narrow S19 | box probes failing on ordinary merges and rebases |
| S25 | Commit freeze during an ACT apply | `operator/freeze_gate.py` | a commit landing on an ACT's paths mid-apply (locks the operator, F15) | yes, because the CTO commits during an apply | loses work | 2.7 lead-h on 11-12 (with restarts) | n/a | keep | already scoped to the ACT's paths and the control paths | none |

## Quality gates

| # | Item | Where | What it protects | Ordinary work | Consequence | Cost | Fired / caught | Verdict | The change | Reversed by |
|---|---|---|---|---|---|---|---|---|---|---|
| Q1 | Operator G1 + G5: the frozen bytes equal the reviewed and requested bytes | `operator_run.py` G1, G5 | applying something other than what was reviewed | yes, because the bundle is edited after review | fails open | seconds | n/a | keep | none | none |
| Q2 | G2: under an ACCEPTED decision | G2 | applying without a decision | yes | fails open | seconds | n/a | keep | none | none |
| Q3 | G3: rehearsed with 0 failures | G3 | an untried apply on live files | yes | loses work | minutes per ACT | n/a | keep | none | none |
| Q4 | G4: READY by verdict.py; reviewer not the author; at most 2 rounds | G4, `verdict.py` | self-review, endless rounds | yes | fails open | seconds | n/a | keep | none | none |
| Q5 | G6: class by three votes; a (b) needs the owner's yes | G6, `act_class.py`, `class-rules.yaml` | a control change without the owner | yes | fails open | owner's attention per ACT | 18 applied, all (b) | scope | see Q8 | none |
| Q6 | G7 live state + G8 dry run in a planted-HOME clone with a byte-exact undo | G7, G8 | an apply that cannot be undone | yes | loses work | minutes | n/a | keep | none | none |
| Q7 | G9: holds (waits, never refuses) | G9 | applying during a land or a release | yes | loses work | waits | n/a | keep | none | none |
| Q8 | Generated `.claude/agents|skills` copies classed (b) | `class-rules.yaml` row agents-skills-kernel | instructions changed without the owner | no, because the bytes are `gov adapters generate` output of a kernel commit that already passed ticket, CIT-P and the kernel gate | other | 12 ACT-CLAUDE-COPIES = 20 % of ACT bundles, each with a review, a rehearsal and an owner's yes | 12 | simplify | new row: a copy whose bytes equal the generator's output at an owner-approved kernel commit is (a), checked by code; anything else stays (b) | a copy whose source was not approved |
| Q9 | Landing check: control-path commits outside a ticket give a P1 | `operator/landing_check.py` | the CTO editing a guard or kernel path outside the ACT route | yes (seen) | fails open | low | 8 P1s; about 4 true (the dead-man wake commit, reverted twice; a kernel template edit) and about 4 trailer form | keep | simplify the trailer-form half: the merge tool writes `Task:` in one block (memory: three trailer traps) | none |
| Q10 | Landing select: lead_verify after a land when commits outside a ticket touch the trigger paths | `tools/landing_select.sh` | a red w2/integrate becoming every lead's base | yes (seen) | other (a red base spreads) | about 4.0 h over 17 runs | 13 RED, 1 to 125 failures: the best catch rate here | keep | none | REDs that turn out to be load flakes |
| Q11 | land.py pre-checks: FULL probe record at the head, YAML parses, disk gate (gitleaks already off, DEC-1045) | `tools/land.py` step 1 | landing an unreviewed head | yes | fails open | seconds | 2 refusals on 11-12 (gave DEC-1154) | keep | none | none |
| Q12 | Kernel gate (kernel bytes listed in kernel-approved.txt, 206 lines) | `tools/kernel_gate.py` | kernel instructions drifting without the owner (CAP-33) | yes | fails open | small | n/a | keep | it is the source gate Q8 relies on | none |
| Q13 | Merge queue (reds traced each way; load-sensitive cases get 3 rounds; batches of 2 or 3) | `merge_queue.py`, `land.py` | merging reds; losing a lead's work in conflicts | yes | loses work | 38.8 h landing time for 90 lands | 12 ejected (9 red, 1 conflict) | keep | none | none |
| Q14 | gov close gates: trailers and Implements resolve, containment, tree committed, store fresh, accepted_reds only from owner commits, disk floor, scoped selection widening on the unknown | `src/gov/close/` | closing what was not measured; silent red growth; drift outside allowed paths | yes | fails open | inside the land time | n/a | keep | none (F-031 is a product defect, not ceremony) | none |
| Q15 | Structural pass notice after each land | `land.py`, `structural_pass.py` | structure drift (it never refuses) | no, because it is a notice only | other | 73 inbox wakes in 90 lands | 73 | simplify | one daily digest line instead of an inbox item | a notice that changed a decision |
| Q16 | Nightly full regression + the 08:00 check | crontab, `orchestration/nightly/` | reds and flakes the scoped close cannot see | yes | other | machine time at night (the night hold is already lifted) | n/a | keep | none | none |
| Q17 | FULL-ticket probe by a fresh reviewer | `audit` skill, `docs/probes/` | lost work, out-of-scope writes, changed tests, gates failing open (DEC-137) | yes | fails open, loses work | the costliest quality item: 331 reviewer sessions, about $1.2k, 76 h; 192 records | 25 blocking findings caught (5 % of 502); 32 KPI fails | keep | simplify the brief: ask for blocking-class findings first and cap rows at five (83 % of findings are rows that the lead must still triage) | a cap that hides a blocking finding |
| Q18 | Two rounds, then the owner once; READY by code | DEC-1010, DEC-1204, `verdict.py` | review loops without end | yes | other | none | no cap stop recorded on 11-12 | keep | none | none |
| Q19 | Narrow check after a decided change (DEC-1154); the CTO's path cases (DEC-1156 (7)) | CTO practice | an unreviewed post-review change landing | yes | fails open | about 1 to 1.5 worker-h a day | n/a | keep | see Q20 for its launch friction | none |
| Q20 | gov launch quality refusals: effort floor, effort max for a second review, model must match criticality, `--reason` for max, `--owner-named` past two rounds | `launcher.py:779-817` | under-powered reviews | no, because they are quality tuning and not a wall | other | CTO relaunches; 4 memory entries | rare but recurring | simplify | the launcher picks the model and effort itself and states them; it refuses only an explicit choice below the floor | a review missed because the effort was auto-picked |
| Q21 | gov launch plan check, ticket in_progress, role matches the ticket | `plan_check.py`, `launcher.py:319-349` | a worker on the wrong or unclaimed ticket | yes (seen: 5+ caught CTO claim mistakes) | fails open (wrong role's walls) | seconds | about 6 | keep | none | none |
| Q22 | gov launch resource gate and start lock | `launch/gate.py` | a launch that sinks the machine | yes | loses work | waits | 3 seen | keep | none | none |
| Q23 | gov brief refusals: KPI_NO_VERIFY, PLACEHOLDER_LEFT, NON_GOALS_MISSING, NOT_READY, WAITS_ON (size budgets are warnings) | `src/gov/brief/build.py` | a worker briefed without a spec or KPIs (the aim) | yes | other | seconds | about 1 seen | keep | none | none |
| Q24a | Lead step scratch_measure (du and inodes before every heavy run, in the evidence) | `facts.yaml` steps, role-lead | a full disk | no, because the disk gate already refuses at launch, close and land | other | a command and an evidence line per heavy run, every lead | n/a | lift | drop the step; the disk gate stays | a disk-full incident between gate checks |
| Q24b | Lead step hooks_check (no pre-commit hook before each commit) | `facts.yaml` steps | a planted git hook running | no, because it needs a crafted hook | other | a command per commit | n/a | scope | lift once the box makes git hooks read-only | none |
| Q24c | Lead step context_ceiling (gov context before DONE; a package when over the ceiling) | `facts.yaml` steps | a brief too big to read | no | other | blocked briefs on W2-88 and W2-111 (memory) | 2+ | simplify | warn only | none |
| Q24d | Lead step keyword_warn | `facts.yaml` steps | DEC-911 paths | yes | other | seconds | n/a | keep | none | none |
| Q25 | SubagentStop: the twelve return fields enforced on every subagent | `kernel/hooks/subagentstop.py` | a lead missing a worker's status or evidence | yes for 4 fields, no for the other 8 | other | words on every return, helpers' included | blocks on a missing field | simplify | enforce status, files_changed, evidence, unresolved; the rest optional | a lead decision that needed one of the other eight |
| Q26 | Test-map, opt-in and ratchet lists classed (a) only when they tighten | `class-rules.yaml` | fewer tests run in silence | yes | fails open | small | n/a | keep | none | none |
| Q27 | placeholder_scan and applied_check | `tools/placeholder_scan.py`, `tools/applied_check.py` | placeholders reaching the owner; decided-not-landed drift | yes (DEC-1012 slipped twice) | other | seconds | n/a | keep | none | none |

## Records

| # | Item | Where | What it protects | Ordinary work | Consequence | Cost | Fired / caught | Verdict | The change | Reversed by |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | The decision register | `docs/DECISION_REGISTER.md`: 2.1 MB, 15,572 lines, 1,203 entries | the owner's decisions as the governing record (the aim) | yes | other | 127 decision-record commits in 8 days | n/a | keep | delegated P2s get a one-line entry | none |
| R2 | Hand-written version rows and "Next free id" lines | the register: 589 rows | none that git and a script do not already give | no, because git history carries every version | other | a table and a line in every decision commit; next-free-id errors appear in CHECKPOINT | n/a | lift | compute the next id and the version by script; stop writing the rows by hand | a test or tool that reads the rows (check before lifting) |
| R3 | DEC-866 marks and sweep (W2-130 reddens the nightly when a mark is missing) | register, W2-130 | superseded rules still enforced: the drift the aim names | yes (its basis: W1-49 and W2-59) | fails open (old rule enforced) | a hand mark per Changes: (a memory trap) | n/a | keep | simplify: the decision-record script writes the marks from Changes: and Supersedes: | none |
| R4 | DECISIONS-IN-FORCE | `orchestration/DECISIONS-IN-FORCE.md`: 92 KB | a fresh session acting on stale rules | yes | other | hand upkeep; it went stale once (DEC-1158: a fresh session would have stopped leads) | 1 | simplify | generate it from the register's Status lines | none |
| R5 | DECIDED-NOT-DONE | `packages/DECIDED-NOT-DONE.md`: 445 lines, 127 KB | decided work never done | yes | other | hand upkeep | n/a | keep | move DONE rows to an archive file | none |
| R6 | WAVE_3_PARKING | `docs/plan/WAVE_3_PARKING.md` | where rows go, so they leave rounds | yes | other | small | n/a | keep | none | none |
| R7 | Six-part package form (DEC-818) | `templates/decision-package.md` | the owner deciding without the options | yes | other | words per package (292 packages) | n/a | keep | allow a 3-line form for CTO-delegated P2s | none |
| R8 | Probe record form (front matter + one unquoted verdict block) | W1-08, W1-26, `land.py ready()` | READY computed wrongly | yes | fails open | two memory traps | n/a | keep | simplify with a probe-record writer tool | none |
| R9 | Commit trailers (Task, Role, Implements resolving; one block) | close gate (e), landing check | work untraceable to ticket and decision (the aim: record the work) | yes | other | three memory traps; about 4 FP landing P1s | n/a | keep | simplify with a commit helper that writes the block | none |
| R10 | Checkpoint and close records (Stop, PreCompact and SessionStart hooks) | `kernel/hooks/` | memory lost at compaction (the aim) | yes | loses work | small | n/a | keep | none | none |
| R11 | CHECKPOINT.md with all history inline | orchestrator `CHECKPOINT.md`: 337 KB, 1,863 lines, 28 RESUME HERE blocks | the CTO's handover | yes | loses work (handover) | tokens at every fresh start and compaction | n/a | simplify | keep only the live RESUME HERE and STATE; move history to CHECKPOINT-ARCHIVE.md at each handover | none |
| R12 | Guard refusal harvest: the log plus per-refusal inbox items | `tools/guard_refusals.py`, `log/guard-refusals.jsonl` | knowing the false positives (it found 217) | no | other | 151 inbox wakes | n/a | simplify | keep the log; one daily digest instead of the inbox items | none |
| R13 | Status block at every report (new and reopened tickets) | `tools/status_block.py` | the owner losing track of scope | yes | other | scripted | n/a | keep | none | none |
| R14 | Scratch sprawl: `.pre-*` tool copies, 2,297 log files, 378 drafts, 321 tools | orchestrator scratch | none (backups git could hold) | no | other | search noise and reading tokens | n/a | lift | the `.pre-*` copies only; the tools that matter are already versioned (DEC-1010 (6)) | a `.pre-*` copy used in an undo |

## Coordination practices

| # | Item | Where | What it protects | Ordinary work | Consequence | Cost | Fired / caught | Verdict | The change | Reversed by |
|---|---|---|---|---|---|---|---|---|---|---|
| C1 | The dispatcher (cron every minute; the CTO's ready.txt and land.txt; 120 s stagger; claim and brief checks) | `orchestration/tools/dispatch/` | governing the traffic: start order, landing approvals | yes | other | negligible | 262 starts, 90 lands, 10 never-ran items | keep | none | none |
| C2 | Idle pressure: the dispatcher's idle-headroom items and stop_idle_check | `stop_idle_check.py`, dispatcher | idle slots (4.0 lead-h "no line prepared" on 11-12) | no fail-open or loss | other | 114 inbox items and IDLE-REASON lines | n/a | simplify | fold into one watcher (C9) | none |
| C3 | Heavy-job slots (every pytest through heavy_slot.sh) | `tools/heavy_slot.sh` | the machine sinking (WSL down takes every session) | yes | loses work | 1 to 4 lead-h a day (estimated, no wait log) | n/a | keep | add a wait log so the cost is measured | none |
| C4 | Memory guards: mem_guard, mem_hold, the resource gate | `tools/mem_guard.py`, `mem_hold.py` | WSL going down (11-11: 2,161 rg processes) | yes (seen) | loses work | negligible | n/a | keep | none | none |
| C4b | Memory and kind samplers (mem_sampler, kind_sampler, lead_mem_watch, lead_hour_watch, lead_usage) | `tools/` | measurement for the sizing package | no | other | processes running for 4.7 days | n/a | scope | stop them once the sizing package is decided | none |
| C5 | Release hold (no commit between "release ready at C" and "released", then a src-only freeze) | CTO practice, `log/act-in-progress.txt` | released bytes differing from the reviewed C | yes | fails open | hours of frozen commits on release day | n/a | keep | none (already scoped to src after the release) | none |
| C6 | `pgrep land.py` before every commit (CTO habit) | CHECKPOINT Standing | a queue restart ("moved while under test") | yes | other (0.72 lead-h of restarts on 11-12) | a check per commit | n/a | simplify | the queue restarts only when a commit touches its selection, or a hook refuses commits while a land runs | none |
| C7 | Spend brake and usage watch | `tools/usage_watch.sh`, DEC-1091 | the plan running out | yes | other | about 1 min a trip | 16 trips | keep | none | none |
| C8 | Dead-man + sentinel (a Haiku Remote Control session) + sentinel_check | `deadman.py`, `sentinel_check.sh` | the owner not knowing that the CTO stalled | yes | other | one small session | 13 wakes, 5 sentinel-silent | keep | none | none |
| C9 | Four layers keeping the CTO watching: helper_watch, waiter_guard, stop_waiter_check, inbox_wait (+ interim_watch, standby file) | `tools/`, Stop hooks | returns left unread (11-15: about 50 min) | no fail-open or loss | other (delay) | 85 helper-watch items; a re-arm in every response | n/a | simplify | one watcher with one state file and one wake rule | none |
| C10 | Job queue protocol | `~/gov-os-operator/queue/jobs/README.md` | the operator running anything but the named, rehearsed commands | yes | loses work | an owner relay per job | 7 job results | keep | interim until the box; lift with the box's own yes path | none |
| C11 | Rehearse every handed command on a copy; never against a live path (DEC-1196 (5)) | CTO practice, `tools/rehearse.sh` | a wrong command run live | yes (seen: a miscounted `../`) | loses work | minutes | n/a | keep | none | none |
| C12 | Work order: TD and engineer in parallel, never reading each other; one writer per worktree; the tests branch never fast-forwards to the ticket | role-lead, DEC-820, DEC-963 | independence and lost edits (the aim) | yes | fails open, loses work | none | n/a | keep | none | none |
| C13 | Refused twice: stop, never work around (DEC-1137) | every brief | walls eroded by respelling | yes | fails open | small | n/a | keep | none | none |
| C14 | New tickets only on the owner's P1 (DEC-974) | CTO practice | scope creep (governing the traffic) | yes | other | an owner line | n/a | keep | none | none |
| C15 | The golden-rule paragraph pasted into every judging brief | DEC-1204 (6) | a reviewer blocking on rows | yes | other | words per brief | n/a | scope | lift when W2-195 lands (judging-work is preloaded) | none |
| C16 | Interface stated at claim (DEC-1157 (3)) | CTO practice | a pair starting on an undefined interface | yes | loses work (redo) | minutes per claim (it was 4.9 lead-h as a lead stop) | n/a | keep | none | none |

## The CTO's own habits (MEMORY.md: about 95 entries, 103 files; CHECKPOINT "Standing")

| # | Item | Where | What it protects | Ordinary work | Consequence | Cost | Fired / caught | Verdict | The change | Reversed by |
|---|---|---|---|---|---|---|---|---|---|---|
| H1 | The memory index as a whole | `memory/MEMORY.md` | lessons surviving sessions (the aim) | yes | other | about 95 lines loaded every session; at least 25 are workarounds of tool or guard quirks; 4 are corrected or duplicate | n/a | simplify | turn each recurring workaround into a tool default (launcher picks effort and model; trailer and probe writers; sandbox TMPDIR); prune corrected and duplicate entries (needs S16's change) | none |
| H2 | Stamps from `date` | memory | false times in records (ran ahead 8 times) | yes | other | none | 8 | keep | none | none |
| H3 | Waits and stops by pid only | memory, `tools/proc.sh` | killing the wrong process | yes | loses work | none | n/a | keep | none | none |
| H4 | Long runs in the background, no timeout wrap on closes | memory | a close killed after selection | yes (seen) | loses work | none | 1+ | keep | none | none |
| H5 | Never edit a running bash script | memory | a batch crashing and skipping its after-record | yes (seen) | loses work | none | 1 | keep | none | none |
| H6 | Check before a ready line (role-lead present, brief non-empty, no {UPPER} slots, unused log name) | memory | a lead started on a broken brief | yes | other | a manual check per line | n/a | simplify | extend the dispatcher's `@@` check to {UPPER} slots and log reuse; drop the habit | none |
| H7 | Copy TD logs before removing a worktree | memory | evidence lost | yes | loses work (records) | manual | n/a | simplify | the worktree-remove tool archives logs | none |
| H8 | Write scripts with the Write tool and run them by path | memory, P-GUARD-FP-1 (a) | guard FPs (class 2: 11 of 31 live) | yes | other | small | n/a | keep | until GF-8 and S19 | none |
| H9 | Lessons to memory at once | memory | the same mistake repeated | yes | other | index growth | n/a | keep | pair it with H1's pruning | none |

## Verdict counts
keep 65 · simplify 18 · scope 9 · lift 3, over 95 rows (counted by script from the tables; Q24 is four rows and C4 is two).

## Plain ceremony: no ordinary-work protection, or a duplicate of another layer
- **Lift now:** R2 (hand-written version rows and next-free-id), Q24a (the scratch_measure step, which the disk gate covers) and
  R14 (the `.pre-*` tool copies).
- **Ceremony in their present form, so simplify:**
  - Q8: an owner's yes and a review for generated copies whose source the owner already approved.
  - Q15, R12 and C2: notices delivered as inbox wakes.
  - Q20: the launcher refusing the CTO's model and effort instead of choosing them.
  - Q25: twelve enforced fields where four carry decisions.
  - C9: four layers of watchers keeping the CTO watching.
- **Duplicates once the box is live, so scope:** S6, S8, S12, S21 and Q24b, and S19 narrowed.

## Not ceremony, kept with evidence
- **Security walls:** S1, S11 and C12 keep roles apart. S16, C3 and C4 protect against lost work.
- **Gates that caught real problems:**
  - Q10, the landing select: 13 reds after the CTO's own commits outside a ticket.
  - Q9, the landing check: 4 real control-path edits outside the ACT route.
  - Q17, the FULL probe: 25 blocking findings.
- **Decisions and records that stop drift:** the operator's gates Q1 to Q7, Q11 to Q14 and R3.

## What I probed and found sound
- READY is computed fail-closed by `verdict.py`.
- The box package classifies its 18 holes as Wave 3 rows and keeps them out of rounds, as the golden rule says.
- DEC-1157 has already lifted the largest lead-delay costs of 11-12: the night rules, the cap, the CPU band and one land per batch.
- gitleaks is already off (`secrets.yaml` scan: off).

No KPI lines apply: this is a retrospective, not a ticket probe, so there is no verdict block and no READY.
