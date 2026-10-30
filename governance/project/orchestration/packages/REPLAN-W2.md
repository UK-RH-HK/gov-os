# P-REPLAN-W2 — The rest of Wave 2, re-planned (DEC-930, with DEC-936 item 3's six additions)

From: the W2 orchestrator, drafted 2026-10-29; delivered with STATE-OF-GOV-OS in the first morning package after re-pin 3, at the latest on 2026-11-01. Six parts (DEC-818). The evidence is the STATE file's annexes A to E. The figures below are measured unless marked as an estimate.

## 1. Context

**The owner's five points** (DEC-930 item 1), plus six additions (DEC-936 item 3).

**Today** (STATE §1 to §3):
- 15 of 70 Wave 2 tickets are closed (13 by a clean close);
- none of the 9 keystones is done;
- memory is unmeasured;
- 9 held tickets are 10 or more days stale;
- scoped closes run about 10 minutes of wall time; full closes run about 74;
- 42 % of close attempts have passed overall, and 8 of 11 since 10-26.

**Measured capacity:**
- **The machine:** 20 CPUs and 23 GB of memory (`nproc`, `free`).
- **A lead run:** median 3.4 h, 75th percentile 5.0 h, maximum 13.7 h; median cost 5.38 USD (82 runs, `LOG/W2-*-A5-run*.json`, `duration_ms` and `total_cost_usd`).
- **A full verification run:** 46 to 60 minutes of parallel phase plus 18 to 25 minutes of serial phase (annex B §5), one at a time under `/tmp/gov-os-verify.lock`.
- **Leads at once:** the resource gate (load below 20, at least 6.7 GB of memory available) admitted 2 to 3 leads at once on 10-28 and 10-29 (launch logs: load 13 to 15 at launch).

## 2. The minimum to start EXAMIN's copy, and what goes to Wave 3 (point 1)

### 2.1 In the minimum

| Block | Tickets, in order | Estimate (lead-days) | Why in the minimum |
|---|---|---|---|
| **A. Fast closes** (K2) | W2-77 (the nightly's own-clone clean-up; FULL, small); re-pin 3 (W2-68, W2-71); the batch switched on and measured; W2-78 (P-SCOPE-RECORDS-1); W2-76 (the rebuild lock and watchdog) | about 3 | Every other ticket passes through a close; today a full slot is about 85 minutes |
| **B. Memory proven** (K4) | W2-61 (the 20-question measure, first, as the baseline); W2-03 (merge back, close); W2-55 (superseded decisions out of results); W2-64 (record schema widening); W2-04 (the context packet's ceiling); W2-05 then W2-06 (incremental indexing); W2-13 (ranked BM25); W2-15a (semantic recall to DEC-833's 85 % floor, with EXP-003). W2-61's measure is repeated after each. | about 15, of which about 10 on the critical path | The owner's condition. It is also the longest chain, and lens B's defects (packet 42 to 168 times its ceiling, the index switched off by any edit, the superseded filter failing open, 65 % hit@5) fail open for any agent that relies on memory |
| **C. Agents load role, skills and model at launch** (K3) | W2-60 (file it: role defaults, skills and model per role at `gov launch`); W2-11 (the kernel skills, with D's priorities 4 and 5); W2-09; W2-33 (cut down, DEC-832); W2-58's close | about 7 | The owner's condition; today it is all done by hand in the prompt (annex D, H1) |
| **D. The leads' sandbox** (K6) | W2-56 (file it); W2-21 (`gov launch lead`); W2-20 (merge back; the resource gate in code, with the machine profile, item 4 below); W2-42 | about 6 | The owner's condition; leads run unsandboxed today (lens E F1) |
| **E. Adoption readiness on the proving ground** (new) | a proving-ground ticket (synthetic repositories with planted problems and held-out question sets, item 6 below); W2-26 and W2-52 (merge back); W2-27 to W2-30 as the planted problems require | about 8 | The owner's new entry criterion (DEC-936 item 3.6) |

**Order and parallelism:**
- A first: it is short, and every block uses closes.
- B, C and D side by side: they share no code paths. B is in `src/gov/retrieval/` and `store/`; C in `launch/` and `template/governance/kernel/`; D in `launch/` and the sandbox. C and D both touch `src/gov/launch/`, so their launch-file tickets are split by file, or run in turn.
- E after B and C: adoption leans on memory and the launch path.

### 2.2 Proposed for Wave 3, with what each deferral costs

| Deferred | What waiting costs |
|---|---|
| K5's W2-12 (`gov approve`) and W2-49 (the decision pipeline, Contract v4.2's text) | Owner decisions stay transcribed by the orchestrator and committed with `Role: orchestrator` (CAP-21 weakened, F-M6). The Contract text stays at v4.1 though the plan follows v4.2. |
| K7: W2-16 (releases), W2-17, W2-18 | Re-pins stay manual: about 1 to 10 h of preparation, and an owner act of 7 to 26 h end to end (annex C, S-5). No `gov update` for adopters (CAP-45). |
| K8: W2-43 (CI), W2-22, W2-45; keep only W2-05, W2-06 and W2-08's pre-commit tier in Wave 2 | No CI; ADR-0001's hard boundary rests on the runtime guard alone. Keeping W2-08's commit-time tier gives D's priority 5 (no commit on a red check), which would have prevented R12, R15 and S3 (annex C). |
| W2-10, W2-14, W2-31, W2-32 (component separation), W2-37 (impact), W2-46, W2-47 | Each its capability's Wave 3 items (annex A). W2-37's held work goes stale further (impact analysis stays a skill, not a command). |

## 3. An estimate per remaining keystone, and a target date (point 2)

These are estimates from the measured capacity in §1. The single uncertainty that moves the date most is the batch's gain on this repository, unmeasured until W2-77 is pinned.

| Keystone | Remaining in the minimum | Estimate | Done by (estimate) |
|---|---|---|---|
| K1 Pinned judge | W2-07's close (in the queue now) | under 1 day | 2026-10-30 |
| K2 Close queue | Block A | about 3 lead-days, 2 to 3 calendar days | 2026-11-02 |
| K3 Agents know what to do | Block C | about 7 lead-days, 5 calendar days beside B | 2026-11-07 |
| K4 Memory | Block B | about 15 lead-days; critical path about 10 days | 2026-11-12 |
| K6 Sandbox per role | Block D | about 6 lead-days, beside B | 2026-11-07 |
| Adoption readiness | Block E | about 8 lead-days after B and C | 2026-11-17 |
| K5, K7, K8 (in part), K9 | Wave 3 (§2.2), except K9's EXAMIN copy itself | — | — |

**Target for the start of EXAMIN's copy: 2026-11-18,** with an honest range of 2026-11-14 to 2026-11-25.

It assumes:
- **3 leads at once** (the gate's measured admission);
- **verification runs one at a time** (about 1 h 15 min each, so about 15 a day outside the nightly window);
- **scoped or batched closes** after 11-02;
- **no new base red** that stops the queue for more than a day. Two did this fortnight: 16 h 28 min and 15 h 14 min (annex C).

It moves earlier if the verification lock can be relaxed (§6) or the batch saves more than the fixture's 29 %. It moves later if W2-61's baseline shows memory further from the 85 % floor than lens B's 65 %, or if adoption's proving ground finds more planted problems missed than the minimum plans for.

## 4. The operating change (point 3)

Already in force (DEC-936 item 2.5, DEC-938):
- one daily digest with every non-urgent item;
- only P1s and ACTs ping;
- P2s are decided as delegated and listed for the owner to overturn;
- one morning package at 07:30.

**One proposal on top:** the digest and the morning package become one document per day (the morning package carries the digest's items), so the owner reads one file a day.

## 5. Four numbers reported weekly (point 4)

STATE §7 and annex E have them for W42 to W44. From W45 the weekly report gives them in the same form:
- clean closes per day;
- refused closes whose cause is my tooling or process;
- measured cost (with what it does not cover);
- owner and delegated decisions.

To make cost whole, workers' result files are kept before a worktree is removed (annex E, gaps).

## 6. Parallelism once closes are short (point 5)

**Side by side.**
- Blocks B (memory), C (K3) and D (K6) share no code paths except `src/gov/launch/`, which C's and D's launch tickets take in turn.
- Within B, the order is a chain: W2-61 first; W2-03 before W2-04 and W2-55; W2-13 before W2-15a. W2-05 and W2-06 run beside the W2-03 chain.
- So at any time about 3 to 4 tickets are ready at once: one from B's chain, one or two from C, one from D.

**How many leads at once.**
- Measured: the gate admitted 3 on this machine, with load at 13 to 15 at launch.
- A lead mostly writes and thinks. Its load comes from its full verification run, which the lock already serialises.
- **Proposal:** a computed maximum. Each lead counts 1 CPU and 3 GB while not verifying, and a verifying run counts 16 CPUs and 8 GB. That gives about 4 leads beside one verification run on this machine.

**Quiet windows.**
- Today: a scoped close's slot is about 22 minutes, of which 11 to 12 are gates (annex B §2.2).
- With the batch: one rebuild, one `gov check` and one regression per head. The wait for leads drops to about 15 minutes per batch instead of per close (estimate; the batch's gain is measured after W2-77).

**Relaxing the one-verification-run-at-a-time lock after W2-67.**
- The lock exists because two full runs at once raised load-sensitive reds and exhausted inodes (DEC-904, DEC-905).
- W2-67 (test hygiene, temporary-folder isolation) and W2-57's nightly route remove most of the causes.
- **Proposal: a measured trial after W2-67 lands.** Two full runs at once, each with `-n 10`, on two clones. Measure the wall time of each against one run alone, the reds compared, and peak inodes.
- Relax to two at once only if both runs stay green and finish within 1.3 times one run's wall time.

**Planning to keep leads from waiting on the machine:**
- The leads' full runs go in the hours closes do not use.
- A batch runs when 2 or more tickets are ready to close, not one by one.
- Nothing heavy starts between 01:00 and the nightly's end (DEC-939 item 6).

## 7. The six additions (DEC-936 item 3)

### 7.1 Mutation testing as a standing practice

- **Red-first:** as now (annex D, G1); written into the kernel's `test-design` skill (W2-11), where today it is missing.
- **For FULL tickets that change core code** (the judge, the guard, the secrets check, selection):
  - cosmic-ray, scoped to the changed lines, at review time;
  - a cap of about 60 minutes, sampling beyond it;
  - a pass mark of 85 to 90 %, with the survivors named for the test designer;
  - never inside a close, and never for record-only, test-only or documentation tickets.
- **Cost (estimate):** about 60 minutes of one CPU core-set per FULL core ticket, about 2 to 4 tickets a week, so 2 to 4 hours a week.
- **Where it starts:** after K3 (W2-11 carries the skill text), with a measured trial on W2-77's or W2-71's changed lines first. The nightly mutation check for adopted products' critical modules belongs to Wave 3, with item 7.4's planner, since the 02:00 to 05:00 window is full.

### 7.2 Carried through the kernel, not the prompt

- The test-design skill and the reviewer's role text in `template/governance/kernel/` describe it (W2-11).
- `gov launch` loads them at each session's start (W2-60).
- The pinned `gov close` checks the mutation report for FULL core tickets: a new KPI on the close, Wave 3 unless the trial is quick.
- Adopted repositories declare their critical modules and mutation tool at adoption (W2-19's declared commands).
- It ships through the release and pin ladder (K7, so Wave 3 for the release part).

### 7.3 Every standing practice's home

Annex D: 80 practices, 39 only in this repository's tooling, about 25 with no carrying ticket. The five to move first are in STATE §6. They go into blocks A and C above:
- the nightly and the stale-probe check into the judge: W2-77, then a W2-M407 ticket;
- the scratch budgets and the verification lock into `gov launch`: W2-20 and W2-21 KPIs;
- the judgement rules and red-first into the kernel: W2-11;
- the commit-time tier: W2-08.

### 7.4 Capacity-aware scheduling

- **Minimal, for Wave 2 (in W2-20's KPIs):**
  - a machine profile read at start: CPUs, memory, disk, GPUs and their memory (`nvidia-smi` when present);
  - the GPU added to the resource gate;
  - the computed maximum of concurrent leads from §6, replacing my judgement.
- **For Wave 3:** the full planner, with:
  - a resource profile per ticket or job, declared and corrected from measured runs;
  - a dependency and overlap graph;
  - dispatch as slots free, GPU jobs exclusive, respecting the close lock, the verification lock and the nightly window;
  - utilisation and waiting reports;
  - later, across machines.

### 7.5 A Wave 3 row: a reproducible environment and a RunPod trial

- **A new row:** a container image built from the tool registry (Python and its packages, Node and rulesync, gitleaks, Ollama and the pinned models, the code-graph tool, the pin, the scheduler).
- **Then a measured trial on a RunPod pod against the owner's PC:** close times, build times, GPU jobs and cost per day.
- Secure Cloud only, with held-out material kept off the pod unless its protections come with it.

### 7.6 Adoption readiness before EXAMIN's copy

**What exists:**
- the adopt transaction A0 to A11 (W1-39, W1-41; the `adopt` skill);
- namespaces by path map;
- index builds and refreshes;
- retrieval;
- the drift row (W2-02's verdicts).

**What is missing:**
- telling current from historical documents (drift) beyond verdict records;
- a refresh measured after edits (lens B F2: any edit switches the index off);
- answering correctly from the indexes, which W2-61 measures;
- proposing restructuring as governed tickets, never moving files.

**The proving ground (a new ticket in block E):**
- **Five synthetic repositories:**
  - a Python application with drifted specs and plans;
  - a Rust workspace;
  - a TypeScript monorepo;
  - a repository with legacy documents and large files;
  - a repository with a secret in its history.
- **Planted problems with known correct handling:**
  - a stale spec that looks current;
  - a superseded plan;
  - a misleading file name;
  - a secret;
  - an orphaned test.
- **A held-out question set per repository,** to check the indexes' answers.
- **Pass mark:** adoption finds and handles every planted problem, and the question sets reach DEC-833's floor. A planted problem that passes unnoticed means adoption is not ready.
- **Passing it becomes an entry criterion for EXAMIN's copy,** beside the memory measure.

## 8. Recommendation

1. **Accept the minimum (§2.1) and the deferrals (§2.2).** Keep W2-08's commit-time tier in Wave 2.
2. **Target 2026-11-18** for the start of EXAMIN's copy, re-estimated each week from the measured numbers, with the old and new figures side by side (DEC-834).
3. **File W2-55, W2-56, W2-60, W2-61 and W2-64, and the proving-ground ticket, now.**
4. **The verification-lock trial after W2-67.**
5. **The mutation trial on one FULL core ticket after W2-11.**

Confidence: medium. The date depends on the batch's measured gain and on W2-61's baseline.

## 9. What it blocks, and what waiting costs

It blocks the order of the next fortnight's work. Without it, leads run in the old keystone order (DEC-831), and memory, the longest chain, starts after work the owner now places in Wave 3.
