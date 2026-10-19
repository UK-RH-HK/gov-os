---
id: WAVE-2-REVISED-PLAN
type: plan
status: ACCEPTED
state_class: NARRATIVE
depends_on: [CHARTER-v5, CONTRACT-v4, WAVE-2-WBS, WAVE-2-LIST, WAVE-2-TRIAGE]
decisions: [DEC-064, DEC-083, DEC-105, DEC-715, DEC-722, DEC-725, DEC-726, DEC-727, DEC-736, DEC-776, DEC-780, DEC-801, DEC-802, DEC-803, DEC-806, DEC-818, DEC-819, DEC-820, DEC-821, DEC-822, DEC-823, DEC-824, DEC-825, DEC-826, DEC-827, DEC-828, DEC-829, DEC-830, DEC-831, DEC-832, DEC-833, DEC-834, DEC-835, DEC-836, DEC-837, DEC-838, DEC-839, DEC-840, DEC-841, DEC-842, DEC-843, DEC-844, DEC-845, DEC-846, DEC-847, DEC-848, DEC-849, DEC-850, DEC-851, DEC-852]
---

# Wave 2, revised plan by keystones

**Status: ACCEPTED by the owner, 2026-10-19 (DEC-831), with the owner's changes DEC-832 to DEC-852.** Wave 2 resumes by the keystones. The WBS, the ticket files and the list change to match, each change before its ticket starts or resumes (DEC-825 item 7). Until the WBS is brought in line ticket by ticket, this plan holds where the two differ.

## 0. The owner's decisions on this plan (2026-10-19)

The text below carries these answers; where an older sentence survives, this section holds.

| §11 item | Decision | Entry |
|---|---|---|
| 1 | Approved, with the changes below | DEC-831 |
| 1a, 6 | Backend, database and data, integration and API, and security become **skill packs** the engineer loads at launch (through W2-60), in a **cut-down W2-33** (about 1.5 days of product-spec work, no new machinery; CIT-P). Architecture, frontend, DevOps and SRE, and performance go to Wave 3 | DEC-832 |
| 1b, 3 | CAP-10's **85 stays the floor**; the owner's **99 % is the target** W2-61 and W2-15b measure: the stacked context holds all the evidence each question needs, across batches. Both figures reported | DEC-833 |
| 1c | **Every estimate recalibrated after keystone 2,** from measured ticket and close times | DEC-834 |
| 1d, 7 | W2-59 approved; it also ships `retrieve_baseline.yaml` and fixes **every module that finds the repository from its install path** | DEC-835 |
| 1e | **Memory used, not just built:** keystone 4's exit needs every brief built with `gov context`, every lead and worker brief telling its agent to use `gov retrieve`, and the usage measured | DEC-836 |
| 1f | **Resume in full, in keystone 3:** new ticket **W2-62** (split out of W2-10); the session-start hook loads RESUME HERE in full; DEC-792's 8,000-character limit lifted once it does; a checkpoint at every handover | DEC-837 |
| 5 (windows) | **Every session on its model's full window** (1M for Opus 5.5); no compaction threshold in any launch; usage, not money, is the limit. Replaces §6's 300k and 500k | DEC-838 |
| 5 (the rest) | Opus 5.5 for every role; effort per role per launch; subagents on the parent's model; agent teams off; prompt v3 | DEC-839, DEC-840 |
| 2 | The Contract re-baseline, (a) now, through W2-49's CIT-P | DEC-841 |
| 4 | DEC-062 and DEC-140 withdrawn | DEC-842 |
| 8 | W2-48 approved, testmon and coverage one package; **plus three conditions:** subprocesses seen, the leads' runs served, a nightly full uncached run | DEC-843, DEC-852 |
| 9 | `docs/imported/` out of the schema check | DEC-844 |
| 10 | The path map's `experiments/**` and `evaluation_sets` | DEC-845 |
| 11 | The owner's acts as exact commands, when due | DEC-846 |
| 12 | **No fixed cap:** as many leads as eligible tickets, the measured resource gate and the owner's usage limits allow, never in a close's quiet window, at most 10; fewer until W2-48 lands | DEC-847 |
| — | The owner's daily backup push continues | DEC-848 |
| — | **W2-58 first in keystone 3,** or straight after keystone 1 if its paths allow | DEC-849 |
| — | How questions reach the owner; every standing rule written where sessions read it | DEC-850, DEC-851 |

**What this changes in the count:** W2-33 stays (cut down) and W2-62 is new, so Wave 2 holds **55 tickets plus W2-00**. Eight tickets move to Wave 3 (W2-31, W2-34, W2-35, W2-36, W2-38, W2-39, W2-41, W2-44) with W2-19's Rust and TypeScript half; the nine Contract items still move (CAP-22.b and CAP-22.c are W2-33's carded scope, which goes to Wave 3).

**Written by:** the Wave 2 orchestrator (W2-00, DAEO-sdxk), 2026-10-19, at `fecb870c` plus the staged batch DEC-813 to DEC-830.

**Sources:**
- the owner's answers (DEC-818 to DEC-830);
- the assessment `docs/assessment/2026-10/`: lenses A to G and the synthesis, with lens F (models, effort, context) and lens G (tools glued versus built) used throughout;
- the WBS, the list, the triage and the ticket files;
- W2-26's profile of EXAMIN (branch `w2/W2-26`);
- the dry run of the bootstrap pin (section 4.1).

## 1. In one page

- **Principle (owner, DEC-829):** every capability EXAMIN will use is proven working on this repository first. Nothing unproven here is adopted.
- **Order:** nine keystones, each landing before the work it makes easier.
  - Keystones 1 to 3 make the judge, the queue and the agents' instructions sound.
  - Keystone 4 makes memory sound.
  - Keystones 5 to 8 make the decision pipeline, the sandbox, the releases and the outside referee sound.
  - Keystone 9 is the gate run, the audit, then EXAMIN.
- **What changes against the WBS in force:**
  - **Nine tickets move to Wave 3**, with 87 list rows and nine Contract Wave 2 items. This needs a Contract re-baseline (section 8).
  - **W2-19 is cut to what EXAMIN needs.** EXAMIN is Python with pytest. The Rust and TypeScript fixtures move to Wave 3 with UPIM and ASMO, and so does the Rust install (Q-6).
  - **Three tickets are new, each under the admission rule (iii):**
    - W2-59: the judge's own checks and hooks run from the pin;
    - W2-60: the role, its skills and its model, effort and compaction loaded at launch;
    - W2-61: the standing 20-question measure, split under Policy 2 (d).
  - W2-55 to W2-58 already have cards, and get ticket files.
  - Twelve tickets are widened, as listed in section 5.
  - **Glue rather than build** in six places (section 7):
    - pytest-testmon for the test cache;
    - the code-graph tool's own traversal;
    - check-jsonschema for the records;
    - FTS5's own ranking;
    - a hash-locked requirements file, and Copier's update;
    - the sandbox in place of a growing shell parser.
  - **Lens F's per-role model, effort and compaction are set on every launch** (section 6).
- **Size after the change:** 53 Wave 2 tickets plus W2-00, against 55 plus W2-00 today. About 1,650 estimated lines leave the plan with the moved tickets.
- **Estimates,** in working days from the day the queue moves (section 9):

  | Milestone | At today's cap of 3 in flight | With the cap raised to 4 after keystone 2 |
  |---|---|---|
  | Track A's verdict (W2-25) | about day 23 to 30 | about day 18 to 25 |
  | The copy's verdict (W2-28) | about day 26 to 35 | about day 21 to 30 |
  | The real repository's verdict (W2-30) | about day 31 to 44 | about day 26 to 39 |

  Confidence is low. These are later than the synthesis's 12 to 21 days for Track A, for three reasons:
  - the memory proofs now come before the copy (DEC-828);
  - seven ticket files are added;
  - the cap is 3.

## 2. The adoption-ready set: what EXAMIN will actually use

What EXAMIN is, from W2-26's profile at EXAMIN's `a7cf346`:
- **Code:** Python, 542 files and about 210,000 lines (FastAPI, SQLAlchemy, Postgres), and 848 Markdown files.
- **Tests:** pytest, in two suites:
  - a product suite run as `-m "not live"`;
  - its own governance suite, run with xdist.
- **Other repository content:** its own `CLAUDE.md` and governance scripts.
- **Its code graph:** 24,665 nodes and 81,356 edges, under the code-graph tool's 100,000-row cap.

Each capability below is used by EXAMIN's pilot (W2-27 to W2-30), and is proven on this repository first, by the ticket and measure named.

| # | Capability | What EXAMIN uses it for | Proven here by | State today |
|---|---|---|---|---|
| 1 | A pinned judge | EXAMIN runs a pinned, hash-verified release (exit criterion 6) | The bootstrap pin; W2-59; W2-16, W2-18 | Editable install; pin commands ready (DEC-822) |
| 2 | `gov close` with the repository's own test command | One ticket closed at exit 0 with EXAMIN's command (CAP-44.h) | W2-57, W2-48, W2-07, W2-19 (Python part); clean closes here | 1 clean close here (W2-01, by `tk close`) |
| 3 | The guard and Policy 2 | Every session in EXAMIN | W2-58, W2-42, W2-09 | Gate by record; DEC-508's listing refusals still enforced |
| 4 | Sandboxed launches for every role, leads included | Every worker and lead in EXAMIN | W2-56, W2-21, W2-40 | Workers only (DEC-799) |
| 5 | The role, its skills and its model, effort and compaction loaded at launch | Every session in EXAMIN | W2-60, W2-11, W2-21 | No role text loaded (lens E F2); no effort or compaction set (lens F F1) |
| 6 | Correct decision records | EXAMIN's own register | W2-02, W2-03, W2-55 | Every register chunk carries DEC-812 (lens B F4) |
| 7 | The index on during edits | Every edit in EXAMIN | W2-06 | Any edit switches the index off (lens B F2) |
| 8 | Bounded context packets with real text | Every session brief | W2-04 | 42 to 168 times the ceiling, ids only (lens B F1) |
| 9 | Resume keeping the next step, with checkpoints per session | Every compaction and resume | W2-10 | One series per ticket; the next step is lost (lens B F5, lens E F11) |
| 10 | Combined retrieval | Every question | W2-13, W2-15a, W2-37 (the code graph), W2-32 | Ranked lexical not built; the reranker hurts on lens B's set |
| 11 | A standing measure of memory | At each release, and on EXAMIN's copy (DEC-828) | W2-61 | Lens B's 20 questions, now visible to all (section 4.4) |
| 12 | Owner decisions as git facts | The go for the real repository (Charter §6) | W2-12, W2-55, W2-49 | Owner entries transcribed (F-M6) |
| 13 | Releases, the pinned install and update | EXAMIN installs and updates a release | W2-16, W2-18, W2-17 | No release cut |
| 14 | Hooks and CI | The hard boundary (ADR-0001) | W2-05, W2-06, W2-08, W2-43 | Hooks off since 2026-10-15; CI cannot pass |
| 15 | An honest `gov check` and `gov doctor` | CAP-44.h's conditions | W2-45, W2-22, W2-59 | False greens (lens A F4; lens D F7; lens G F2, F10) |
| 16 | Adoption safety and stage records | Adopting a repository with its own `CLAUDE.md` and governance | W2-23, W2-52, W2-02 (the verdict type) | Being built |
| 17 | The governance share | Exit criterion 8 | W2-07, W2-14 | Measured on dev tiers only |

**Not used by the pilot, so moved to Wave 3 (section 8):**
- budget gates;
- `gov readiness --generate` and the UX row;
- `gov discover`;
- impact-selected tests;
- the model-switch reconstruction;
- the specialist roles;
- close-integrity and trailer-identity hardening against deliberate constructions.

### Pulled forward from Wave 3

Each item is in the adoption-ready set; each is pulled forward in its lite form only.

| Wave 3 item | Lite form in Wave 2 | Ticket |
|---|---|---|
| CAP-35.c, role defaults (tier and reasoning per role) | Each role file states its default model, effort and compaction threshold. The launcher applies and records them, and refuses a model that is not the role's (lens F Table 3, R1) | W2-11 (the role-file lines), W2-60, W2-21 |
| CAP-36.a, per-run telemetry | One record per session id: model, effort, window, tokens, cost, minutes, turns, subagents. The role, ticket and task class come from the launch record; pass or fail and the repair count come from the close (lens F R6) | W2-60, W2-07 |
| CAP-39.c, part: a cache keyed by inputs | The test-result cache (already pulled forward by DEC-726) | W2-48 |
| CAP-44.i, part: interrupted-session recovery during adoption | "A failed or interrupted batch leaves a resumable record and no half-staged state" (already in W2-23's KPIs). The freeze stays the owner's | W2-23 |

CAP-44.g, CAP-47.a and CAP-48.b need no new work. CAP-44.h's lite verdict covers them: W2-02's verdict type, the fresh auditors of W2-28 and W2-30, and the ten conditions.

## 3. The keystones, at a glance

| K | Keystone | Tickets (state) | Lands about (day, cap 3 / cap 4) |
|---|---|---|---|
| 1 | The pinned judge | The owner's pin (ready); **W2-59** (new) | the pin: day 0; W2-59 and the re-pin: day 2 to 4 |
| 2 | The close queue moving, and the test cache | the queued closes (DEC-806); W2-57, W2-48, W2-07; resumes of W2-02, W2-05, W2-37, W2-50, W2-51, W2-52 | day 4 to 7 |
| 3 | Agents know what to do | the batch (done at the commit); **W2-58 first** (DEC-849), **W2-62** (new, DEC-837), **W2-60** (new), W2-11, W2-09; then the cut-down W2-33 (DEC-832) | day 5 to 8 |
| 4 | Memory | W2-02, W2-03, W2-55; W2-05, then W2-06; W2-04; W2-10; W2-13, W2-37, W2-15a; **W2-61** (new); then W2-32 | W2-15a's baseline: day 12 to 18; W2-32: day 20 to 26 |
| 5 | The decision pipeline | W2-55 (its check), W2-49, W2-12 | day 7 to 12 |
| 6 | The sandbox and write lists per role; leads sandboxed | W2-20, W2-56, W2-21, W2-42, W2-40 | day 10 to 15 |
| 7 | Releases and the pin ladder | W2-16; the owner's first release; W2-18, W2-17 | day 9 to 13 |
| 8 | Hooks and CI back on | W2-08 (with W2-05 and W2-06), W2-43, W2-22, W2-45 | day 12 to 17 |
| 9 | The gate run and audit, then EXAMIN | W2-14, W2-23, W2-52, W2-19 (Python part); W2-24, W2-25; W2-26, W2-27, W2-28; W2-15b, W2-29, W2-30 | section 1's table |

**About the order.** The keystones overlap in time. Each keystone's tickets start as soon as their dependencies close, and the keystone order sets the priority for a free slot:
1. a lower keystone first;
2. then the copy's path (W2-13, then W2-15a, then W2-24);
3. then the rest.

W2-32 and W2-15b are on the real repository's path, not the copy's. So they trail keystone 4 and run beside keystones 5 to 9.

## 4. The keystones in detail

### 4.1 Keystone 1: the pinned judge (DEC-822)

- **The owner's act (step 1):** run `.gov-runtime/scratch/orchestrator/pin/PIN-COMMANDS.sh`, whose copy is in the orchestration record.
  - It builds a reproducible wheel of `fecb870c`: sha256 `385fd5f0…`, the same bytes from two builds.
  - It installs it in `~/.local/share/gov-os/pin-fecb870c`, links `~/.local/bin/gov` to it, removes the editable install, and records the entry with `pin_registry.py`.
- **What the dry run found: the pin does not yet cover the judge's own checks.**
  - `src/gov/check/runner.py:76–91` runs each declared check as `python3 -m gov.check.*`, with the working tree's `src` first on `PYTHONPATH`.
  - The guard's hook lines do the same (`PYTHONPATH="$CLAUDE_PROJECT_DIR/src"`).

  Ordinary work: yes, because any ticket that edits `src/gov/check/` changes the checks that judge it. Consequence: fails open.
- **W2-59, new (STANDARD, engineer; CAP-33: a judge change, through CIT-P):**
  - The runner runs the kernel's declared checks with the pinned interpreter and package. Only the code under test comes from the tree (DEC-822 item 3).
  - The hook lines call the pin's environment. This is DEC-822 step 2, after the independent test designer has checked W1-38's hook-source tests.
  - The canary template is found from the project root, not from `__file__` (`retrieval/canary.py:10`). **DEC-835: every module that finds the repository from its own install path does the same** (today also `retrieval/retrieve_check.py:16`), proven from an installed wheel.
  - `retrieve_baseline.yaml` is shipped as package data (DEC-835).
  - **Overlap (2026-10-19):** W2-05's unmerged branch changes `_run_command`'s environment lines in `check/runner.py` and the git calls in `retrieval/retrieve_check.py`, which W2-59 also changes. The order is package P-W2-48.
  - `gov --version` names the version and the commit.
  - Paths: `src/gov/check/runner.py`, `src/gov/retrieval/canary.py`, `src/gov/cli/main.py` (the version), `pyproject.toml` (package data), the hook command lines (owner-approved), `tests/unit/check/**`, `tests/unit/cli/**`, `docs/changes/W2-59-CIT-P.md`.
  - Admission: exit criterion 1 ("a clean `gov close` by the pinned release in force").
- **After W2-59 merges,** the owner re-runs the pin commands at its merge commit. This is the pin ladder by hand until W2-16 and W2-18 land.
- **Glue (lens G R4):** `gov`'s own dependencies are pinned in a hash-locked requirements file (PyYAML 6.0.1, sqlite-vec 0.1.9), used by the pin, by CI and by `gov install`. This rides in W2-18.

### 4.2 Keystone 2: the close queue moving, and the test cache (DEC-823)

- **The closes, in DEC-806's order, each once, in a quiet window, straight after a rebuild (DEC-780):**
  - closes only: W2-53, W2-54, W2-03, W2-20, W2-16, W2-49 (after W2-51);
  - a resume first:
    - W2-02: its standalone-types line, a fresh probe, and section 5's validator widening;
    - W2-51: lens A F4's counting fix;
    - W2-50: its resume probe;
    - W2-05: F-A, P-1, W2-M281, DEC-805 and lens G R7's measure;
    - W2-52: its merge, DEC-814's regeneration and the probe;
    - W2-37: DEC-812 plus the code graph (keystone 4);
  - W2-26: re-scoped (DEC-827), then closed after W2-07.
- **W2-57 (FULL; DEC-813, DEC-823):** load out of the close. One ordinary-work row rides in it: lens A's ancestry case of the commit range (W2-H023), if its test designer finds it reachable in ordinary work.
- **W2-48 (FULL), glued (lens G R6, F6):**
  - pytest-testmon and coverage, one DEC-083 install package (Q-13), raised when W2-48 starts;
  - `--testmon-env` set to a hash of the declared data globs and the test command;
  - deselected tests recorded as "reused", with the run they came from;
  - `.testmondata` written only by main-tree closes;
  - `--testmon-noselect` for W2-24's and W2-46's full runs.

  Decided (DEC-843): the key KPI restated as behaviour. Each planted change re-runs every dependent test; a change outside every input reuses; every reuse is recorded; a failed result is never reused. **DEC-852 adds three conditions:** (1) the cache sees code run in a subprocess (subprocess coverage, configured and tested) or always re-runs a test that starts a process, proven by a change reached only through a subprocess; (2) the same cache serves the leads' suite runs in their worktrees, with the same rules and `--no-cache`; (3) from W2-48's merge, a nightly full uncached regression on `w2/integrate`'s head in a quiet window, reported in the next digest; a test that fails there but passed through the cache is a P1 package.
- **W2-07 (STANDARD):** close by ticket class, so that research, integration, audit and coordination tickets close properly. It also adds pass or fail and the repair count to the per-run record (section 2).
- **The countdown reports the close success rate** (DEC-823 item 5).
- **Parallelism (DEC-847, replacing the cap):** no fixed number. As many leads as eligible tickets, the measured resource gate and the owner's usage limits allow, never during a close's quiet window, at most 10; fewer until W2-48 lands, then as many as the gate and the limits allow.

### 4.3 Keystone 3: agents know what to do (DEC-819, DEC-820, DEC-821, DEC-824, DEC-826)

- **Done at the owner's commit:**
  - Policy 1 and the orchestration record;
  - Policy 2 in the prompt and the briefs;
  - the working rules in git;
  - `CLAUDE.md` corrected;
  - ADR-0001 accepted.
- **W2-58 (STANDARD; DEC-821), first in this keystone (DEC-849):** Policy 2 in the guard and the launcher. Its paths overlap W2-50's unmerged files (`guard/decide.py`, `guard/protected.py`, `launch/launcher.py`), so it starts when W2-50 merges, or stacked on W2-50 once W2-50's resume probe has passed (DEC-786). Until it lands, a read refusal is taken, never routed round, and counted in the digest.
  - Widened: `gov.secrets.indexable` leaves out held-out and export-denied paths. This is the code half of the synthesis §6 row 7. The check half is the owner's now: each held-out path is looked up in both indexes.
  - Widened: the path map gains the `evaluation_sets` block (section 4.4).
- **W2-60, new (STANDARD, engineer), the role at launch (DEC-826 Q1, Q5; lens F R1, R6; lens E F2, F13):**
  - `gov launch` starts a worker as its role: the role file's text and its skills, with their hash and version in the launch record;
  - a cleaned environment: no connectors, no user-level agents or skills, no model-side memory;
  - the role's default model and effort, applied on the launch line; **no compaction threshold is set, and the model's full window is recorded** (DEC-838);
  - the subagent model set to the parent's;
  - the engineer's skill packs (DEC-832), once W2-33 has written them;
  - a launch record holding all of these, and a per-session record with **tokens, turns and any rate-limit event** (DEC-838);
  - a refusal of a model that is not the role's;
  - research first: whether a `paths:`-scoped `.claude/rules/` file loads in a headless worker (lens G Q4).

  Paths: `src/gov/launch/**` (after W2-58, which shares it), `tests/unit/launch/**`. Admission: CAP-35.c lite and CAP-36.a lite (section 2), and exit criterion 5.
- **W2-11 (STANDARD, product-spec; kernel CIT-P):** as carded, with DEC-825 item 1 and DEC-808. Widened:
  - the role files' default lines (lens F Table 3), with `template/governance/kernel/roles/**` (those lines only) added to its paths;
  - one versioned source per skill (DEC-825 item 6);
  - the generated skill list trimmed (lens G R10): no OpenSpec skills or commands in this repository's sessions, and no Superpowers unless a role file names it.
- **W2-09 (FULL; CIT-P):** `SubagentHandback` on the guard's list. It is needed by W2-10 and W2-22, and the guard refused 58 correct calls.
- **W2-62, new (STANDARD, engineer; a kernel hook change through CIT-P; DEC-837):** resume in full, split out of W2-10 so that it lands first.
  - The session-start hook injects the RESUME HERE section in full, never a cut of its first 9,000 characters (row W2-M372), and names the prompt in force (row W2-M373).
  - The checkpoint skill states the resume rule: the full session state (what is happening, what was decided, what is next, where things are); repository knowledge from retrieval and the context packets.
  - Once it lands, DEC-792's 8,000-character limit is lifted.
  - Paths: `template/governance/kernel/hooks/sessionstart.py`, `template/governance/kernel/skills/checkpoint/**` (the resume rule only), `tests/unit/hooks/**`, `docs/changes/W2-62-CIT-P.md`. No dependency; no overlap with a ticket in flight.
- **The cut-down W2-33 (STANDARD, product-spec; kernel skills through CIT-P; DEC-832):** four skill packs (backend, database and data, integration and API, security), loaded by the engineer at launch through W2-60. After W2-60 and W2-11.
- **Until W2-60 lands,** the prompt's launch forms carry the values by hand (prompt v3, section 6).

### 4.4 Keystone 4: memory, in the owner's order (DEC-828)

| Order | What | Ticket | Widened by this plan | Gates |
|---|---|---|---|---|
| 1 | Correct records: each decision its own record, correct ids, supersession honoured | W2-02 (resume), W2-03 (close), W2-55 | W2-02: the full validator, by calling check-jsonschema (lens G R2 (a)), with lens G's planted ticket as a case. W2-55: the must-not-cite filter keyed on each chunk's own entry id (lens B F4; question Q05 the test) | §6 rows 2, 4: the copy |
| 2 | The index on during edits | W2-05 (resume), then W2-06 | W2-06: lens B F2 (uncommitted edits); the kernel template embedded, and tests given their own facet (§6 row 6, row W2-L253 raised); content-based chunk ids (§6 row 13) | §6 rows 3, 6: the copy |
| 3 | Bounded context packets carrying real text | W2-04 | Lens B rec. 1: each of lens B's ten packets within 6,000 tokens, with each mandatory decision's text, and `ok: false` over the ceiling; the packet names the register commit it used | §6 rows 1, 2: the copy |
| 4 | Resume keeps the next step; checkpoints per session | W2-10 | Automatic checkpoints in one subfolder per session (DEC-826 Q3) with the session id; after a compaction the session's own role and task are injected (lens F R5); W2-M372, W2-M373. Paths gain `src/gov/checkpoint/**` (the series only; W2-42 keeps the atomic saves) | §6 row 5: the copy |
| 5 | Combined retrieval | W2-13, W2-37 (resume), W2-15a; then W2-32 | W2-13: FTS5's `bm25()` with column weights and `ORDER BY rank`, plus a trigram table for exact identifiers (lens G R8). W2-37: `src/gov/codeintel/**` added; `trace_path`, `search_graph` and per-kind `query_graph`, never SKIP-paging; the tool's error passed through (lens G R1); "callers of `rrf` and `indexable`" answered (§6 row 8). W2-15a: the deterministic semantic route (the CPU embedder) and the reranker measured against no reranker; **the reranker is kept only if it helps**, otherwise retired with its venv and model (lens G Q5) | §6 row 8: the copy; W2-32 and W2-15b: the real repository |
| 6 | The standing 20-question measure | **W2-61**, new | See below | Each release; §6 row 9 on the copy |
| 7 | **Memory used, not just built (DEC-836)** | the orchestrator and every brief | Every brief built with `gov context` (from W2-04's merge); every lead and worker brief tells its agent to use `gov retrieve`; usage measured: how many briefs and worker tasks used them | Keystone 4's exit |

**W2-61, new (STANDARD, written by an independent auditor session; the script by an engineer):**
- **Lens B's 20 questions and their gold answers become the visible development half,** because they are already readable: `docs/assessment/2026-10/B-memory-retrieval.md` §2, in this batch.
- **A hidden measurement half** of 20 more questions is written by a session independent of the retrieval tickets. It is stored where W2-58's `evaluation_sets` block refuses it to the measured roles.
- **A measurement script** reports the governing source in the first five and in the bundle, and repeatability on an unchanged index and after a rebuild. It prints scores, never the hidden answers. **It reports both figures (DEC-833):** hit@5 against CAP-10's floor of 85, and the share of questions whose stacked context holds all their needed evidence, across batches, against the owner's target of 99 %.
- **The same split for EXAMIN's set** (DEC-828 item 3), written before W2-27.
- **EXP-003's gold answers** (W2-15a, W2-15b) are split the same way.
- Admission: exit criterion 4, and CAP-10.

**CAP-10's line,** decided before W2-15a measures (DEC-828 item 4):
- **Decided (DEC-833): keep 85** as the Contract's floor, and do not re-baseline to 80; the owner's 99 % is the target W2-61 and W2-15b measure.
- W1-21's and W2-54's tests that use 80 are corrected to 85 by W2-32's test designer.
- A figure short of 85 after W2-15b is a named residual for the owner (DEC-725's finish line), not a new round.
- Confidence: medium. Lowering the line before measuring goes against the owner's principle.

### 4.5 Keystone 5: the decision pipeline (DEC-825)

- **W2-55 (STANDARD), widened:** its "lands in" tag, plus the check DEC-825 item 1 asks for. Every kernel-wide standing entry is stated, with its id, in the kernel file it binds, and every project entry is in the prompt or the project briefs. Built with keystone 4's order 1.
- **W2-49 (resume, then close):** DEC-825 item 3, namely the missing providers, the authority form named by decision, and a check that compares the forms.
  - **Widened:** it carries the Contract re-baseline of section 8 as part of Contract v4.2's CIT-P (Q-14).
  - Its merge is an entry criterion of W2-28 and W2-30.
- **W2-12 (FULL):** owner approvals as git facts, with `gov approve`. The go for EXAMIN's real repository becomes an owner git fact (ADR-0001).
- **From the first release on,** one CIT-P per release carries the kernel-wide rules decided since the last release (DEC-825 item 6).
- **Records owed by DEC-825 item 5:**
  - **DEC-062** (GitHub through `gh` with a read-only fine-grained token): **withdraw.**
    - It is still PROPOSED and has landed nowhere (lens C F-6).
    - No session has used GitHub through a token. Research reads web pages, and Policy 2 (a) already refuses tokens.
    - `gh` in the registry's install commands is the owner's tool, registered as such in W2-22's registry pass.
    - Confidence: medium.
  - **DEC-140** (`Task: decision-record` on residual entries in `bootstrap.md`): **withdraw.**
    - It was followed in 8 of 69 commits (lens C).
    - Wave 2 keeps residuals in the list, under W2-00's id (DEC-729), and delegated decisions keep `Task: decision-record` by the W2-00 card.
    - Confidence: medium-high.

### 4.6 Keystone 6: the sandbox and write lists per role; leads sandboxed

- **W2-20:** close only. The machine-wide resource gate, which W2-21 needs.
- **W2-56 (FULL; DEC-799):** as carded. Widened with:
  - DEC-826 Q5's refused flags;
  - lens E F13's cleaned environment, shared with W2-60;
  - lens E F17's single retry on a missing git lock file.
- **W2-21 (FULL; DEC-715):** `gov launch lead`, the ticket-lead role, leads sandboxed under their own role, and launch records.
  - Widened: lens F R1 for leads, through the same role defaults as W2-60.
  - Widened: lens G R3. A worker or a lead is resumed only through `gov launch … --resume`. Until this lands, the rule is in the prompt and the briefs.
- **W2-42 (FULL):** as carded (missing role, links, late paths, atomic saves).
  - Widened (lens G R5): one shared tokeniser that reads a quoted heredoc's body as literal text. That ends lens G's 116 refusals a month of ordinary commit and script forms. Cases: Claude Code's commit form with an apostrophe, and a Python heredoc with an apostrophe in a comment.
  - The parser grows no further. Its nine open rows are settled in the light of the sandbox (DEC-770).
- **W2-40 (research):** EXP-002's untested sandbox cases.
  - Widened (lens G R3): whether a launcher-written settings file that Claude Code re-reads on resume can carry the sandbox, and whether a worker can change it.
  - Re-scoped to `experiments/EXP-002/**` (DEC-827).

### 4.7 Keystone 7: releases and the pin ladder

- **W2-16:** close only (keystone 2's queue), under the bootstrap pin. **Then the owner cuts the first release** (DEC-772), with W2-59 in it.
- **W2-18 (STANDARD):** the pinned install, widened to this repository (DEC-822 item 5). Widened (lens G R4): the hash-locked requirements file, and doctor failing an editable or foreign `gov` here too (DEC-830 item 3).
- **W2-17 (FULL):** `gov update` (CAP-45.a), glued to Copier's update (lens G Q4), which needs git tags, a clean tree and an untouched answers file. The estimate falls from 260 lines to about 200.
- **The ladder for each version** (the synthesis §3):
  1. build;
  2. prove on fixtures with that version installed;
  3. the owner cuts N+1;
  4. N+1 closes real tickets on another repository first;
  5. the owner moves this repository's pin;
  6. to roll back, the owner moves the pin back.

### 4.8 Keystone 8: hooks and CI back on (DEC-830)

- **W2-05 (resume, keystone 2) and W2-06 (keystone 4) come first.**
- **The lefthook measure, an owner act before W2-08 (lens G R7):**
  - `lefthook install` in a scratch clone, with and without an `ai` key, shows what lefthook writes into `.claude/settings.json`.
  - Then (a): commit the form lefthook writes, if it is stable. Otherwise (b): adapter-portability compares parsed JSON. This changes W2-05's KPI again.
- **W2-08:** the owner reinstalls the hooks. Doctor's hooks check reads what git will actually run.
- **W2-43 (STANDARD):** the approved tools on the runner, installed by checksum, using the requirements file of keystone 7. CI's evidence step stays red until the hooks return (DEC-830 item 2).
- **W2-22 (STANDARD), widened (lens G R4, F10):**
  - doctor starts each tool under the runtime it really uses;
  - it says "version only" where no installed file can match;
  - it verifies `gov` by the wheel (row W2-M385, from the pin's dry run);
  - the registry adds pytest, execnet, Python, SQLite and git.
- **W2-45 (STANDARD):** as carded. "Exit 0 with findings is not green", and "an absent tool of a hard-block check is red". `openspec-validate` takes DEC-781's not-applicable branch here (lens G R10). It also joins W2-27 if EXAMIN exceeds DEC-078's envelope (DEC-727).

### 4.9 Keystone 9: the gate run and audit, then EXAMIN

- **W2-14:** ARGUS's full cycle and the governance share (AR-9; exit criterion 8).
- **W2-23 (FULL):** adoption safety. It is needed in earnest: EXAMIN carries its own `CLAUDE.md` and governance suite.
- **W2-52:** resume, then close (keystone 2).
- **W2-19, cut to its Python part:**
  - a project declares its test commands, with their markers, suite paths, interpreter and result reader. EXAMIN's two suites are the target case;
  - a run that collects nothing is unmeasured, never passed.
  - The Rust and TypeScript fixtures move to Wave 3 with UPIM and ASMO, and Q-6's Rust install is dropped.
- **W2-24, then W2-25:** Track A's gate run and audit.
- **W2-27's ticket file** (section (i) (a)) takes as dependencies:
  - W2-24, W2-56 and W2-57;
  - W2-25 as an entry criterion;
  - W2-49 merged;
  - W2-21 (leads sandboxed, DEC-803);
  - the synthesis §6 rows 1 to 8 and 14 (DEC-828);
  - W2-61's EXAMIN set, written and split.
- **Then the copy and the real repository:**
  1. W2-26 (closed, re-scoped);
  2. W2-27, then W2-28;
  3. W2-32 and W2-15b, run in parallel before W2-29;
  4. W2-29 (the owner's go, and Q-16), then W2-30;
  5. W2-46, then W2-47.

## 5. Ticket changes, all of them

**New ticket files:**
- W2-55 to W2-58: they have cards, but no `tk` file yet;
- W2-59, W2-60 and W2-61: new.

**Widened:**

| Ticket | Widened by |
|---|---|
| W2-02 | The validator, through check-jsonschema, plus the owner's ruling on the four imported records |
| W2-04 | Lens B rec. 1 |
| W2-06 | Lens B F2, §6 rows 6 and 13 |
| W2-10 | Checkpoints per session |
| W2-11 | Role defaults, skill sources, the skill trim |
| W2-17 | Copier |
| W2-18 | This repository; the requirements file |
| W2-21 | Lens F R1; lens G R3 |
| W2-22 | Lens G R4 and F10; W2-M385 |
| W2-37 | `codeintel/**` |
| W2-42 | The heredoc tokeniser |
| W2-48 | testmon; the behaviour KPI |
| W2-49 | The Contract re-baseline |
| W2-55 | The chunk-id filter; the "lands in" check |
| W2-56 | DEC-826 Q5; lens E F13 and F17 |
| W2-58 | `indexable`; `evaluation_sets` |

**Cut:** W2-19, to its Python part.

**Re-scoped to `experiments/EXP-00n/**` (DEC-827):** W2-26, W2-40, W2-15a and W2-15b.
- The check DEC-827 asks for is done. No specification names `docs/research/` as the place of a research record: not the Contract, `docs/spec/`, the ADRs, the Charter, the kernel or `src/gov`. Only WBS cards, ticket files and the adoption inventory name it.
- **Two things the re-scope needs:**
  1. The path map holds no namespace for `experiments/**`, though every tracked path must match exactly one. An owner edit to `governance/project/path-map.yaml` adds it before the first record moves.
  2. W2-26 has 12 committed files under `docs/research/EXP-003/examin/` on its branch. Its lead moves them with `git mv` in the resume.

## 6. Model, effort and compaction, per role and per launch (lens F; DEC-826 Q6)

**Decided (DEC-838, DEC-839):** lens F's Table 3 for model, effort and subagents, set on every launch line. **No compaction threshold:** every session uses its model's full window (1M for Opus 5.5), and none is asked to stop or compact early; lens F's 300k and 500k values are replaced. Usage, not money, is the limit: the daily digest reports the daily and weekly allowance used.

| Role | Model | Effort | Window | Subagent model |
|---|---|---|---|---|
| Orchestrator (the owner's session) | `claude-opus-5-5` | high; max when it drafts an owner package | the model's full window | the parent's |
| Ticket lead | `claude-opus-5-5` | high | the model's full window; a checkpoint at every handover | the parent's |
| Test designer | `claude-opus-5-5` | high; xhigh for FULL tickets, as a measured trial | the model's full window | — |
| Engineer | `claude-opus-5-5` | high | the model's full window | — |
| Reviewer and probe | `claude-opus-5-5` | high; max for FULL probes | the model's full window | — |
| Independent auditor | `claude-opus-5-5` | max | the model's full window | the parent's |
| Synthesiser | `claude-opus-5-5` | max | the model's full window | — |
| Research | `claude-opus-5-5` | high | the model's full window | — |
| Product-spec | `claude-opus-5-5`; a lower tier only as a CAP-35 trial | high | the model's full window | — |
| Live harness tests (W1-49, W1-46) | Haiku 4.5 where the case only checks that a hook fired; `claude-opus-5-5` at low effort for the recall case (lens F R10) | low | the test's own | — |

**Why per launch** (lens F §2.3):
- In CLI 2.1.292, while the user-level `CLAUDE_CODE_AUTO_COMPACT_WINDOW` exists, `--autocompact` has no effect. Only an env value passed with `--settings` wins (lens F P2 to P4).
- 75 Wave 1 main sessions ran unpinned on Opus 4.6, with a 200k window, costing $508.97 (lens F F9).

**Until W2-60 and W2-21 land (prompt v3, an owner edit with this plan):**
- the lead and worker forms carry `--effort` per the table, and the forms that take `--settings` add `"CLAUDE_CODE_SUBAGENT_MODEL":"claude-opus-5-5"`; none sets `CLAUDE_CODE_AUTO_COMPACT_WINDOW` (DEC-838);
- A5's "if you pass about 300k tokens" becomes "write CHECKPOINT.md at every handover (a worker's return, a merge, a package, a compaction)", and `LEAD_CHECKPOINT` is dropped (lens F R4, DEC-837, DEC-838);
- the resume rule of section 4.6 is added.

(The CLI note above, P2 to P4, no longer bites: the user-level `CLAUDE_CODE_AUTO_COMPACT_WINDOW` was removed on 2026-10-19, and `claude -p "/autocompact"` then reported "1m tokens (default for this model)".)

**Owner questions from lens F:**
- **R7:** is there a reason to keep `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-6`? Recommendation: no; use the parent's model.
- **R9:** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` has no decision behind it. Recommendation: switch it off, unless a ticket's entry criteria carry its risks (W2-09 is the candidate).
- **R8:** a new register entry corrects DEC-460's stated cause. The Opus 4.6 sessions were unpinned main sessions.

## 7. Glue rather than build (lens G)

| Need | Today | Glue | Where | Build avoided or removed |
|---|---|---|---|---|
| Test-result cache | A built per-test key planned | pytest-testmon and coverage (DEC-083 package) | W2-48 | Most of a per-test import and fixture tracer, with its own storage and invalidation |
| Code questions | Our code pulls the whole graph (fails above 100,000 edges here) | The tool's `trace_path`, `search_graph` and `query_graph` | W2-37 | About 60 lines of traversal; it unblocks `gov impact` and adoption at scale |
| Record validation | A 169-line subset that passes what the schemas refuse (lens G F2: fails open) | check-jsonschema, already pinned | W2-02 | A subset that would grow with every type |
| Lexical ranking | FTS5 as a filter, plus Python's `in` | FTS5's `bm25()`, `ORDER BY rank`, a trigram table | W2-13 | About 30 lines |
| The guard's shell reading | 512 lines of parser; 116 refusals a month | The sandbox as the boundary; one tokeniser that respects heredocs; no growth | W2-42, W2-56, W2-21 | Nine parser rows not turned into rounds |
| CI and installs | `pip install .` with unpinned PyYAML and no sqlite-vec | A hash-locked requirements file, `actions/setup-python`, `--require-hashes` | W2-18, W2-43 | Our own installer logic |
| Kernel update | Our own update planned | Copier's update | W2-17 | Part of W2-17 |

**Retired here:**
- OpenSpec in this repository: the check takes its not-applicable branch, and the template keeps the layout;
- the twelve OpenSpec skills and commands, and Superpowers, unless a role file names it;
- the reranker, if W2-15a shows no gain;
- S0b2's leftover language servers, TypeScript and Rust toolchain: an owner act (uninstall), or registered with a purpose. With W2-19's Rust half in Wave 3, none is needed.

**Kept:** uv, rulesync, copier, ollama, qwen3-embedding, sqlite-vec, `tk`, gitleaks, ccusage, Claude Code, bubblewrap, socat and pytest-xdist.

## 8. Moved to Wave 3, each with its reason

| Ticket | Closes (Contract) | Rows | Reason |
|---|---|---|---|
| W2-31 Budget gates | CAP-04.a, CAP-04.d | 0 | Not used by the pilot. Lens F's per-run record (W2-60) gives the cost data that budget gates will need |
| W2-33's carded scope (Wave 2 roles and typed handoff records) | CAP-22.b, CAP-22.c | 6 | The pilot needs no new role (section 10). The twelve-field return stays (AR-6, W2-10 and W2-11). **W2-33 itself stays in Wave 2, cut down to four skill packs (DEC-832)** |
| W2-34 `gov readiness --generate` | CAP-30.c | 25 | Not used by the pilot |
| W2-35 The UX readiness row | CAP-30.g | 1 | Not used by the pilot; it needs W2-33 and W2-34 |
| W2-36 `gov discover` | CAP-32.d | 1 | Not used by the pilot |
| W2-38 Profile from impact; impact-selected tests | CAP-53.b | 4 | W2-48's cache shortens the close without it |
| W2-39 Model and provider switch | CAP-37.e | 8 | Not used by the pilot. Lens F's note (a window change in the case) goes with it |
| W2-41 Close and escalation integrity | — | 23 | Its high rows (W2-H022, H024, H025, H033) guard against task-less configuration edits, forged escalation lifts and resets: deliberate constructions under DEC-801. W2-H023 rides in W2-57 if ordinary |
| W2-44 Trailers bound to the launch identity | — | 19 | A forged role is a construction (DEC-801). Misattribution is an aid's noise, kept down by the rule "never two writing sessions in one tree" |
| W2-19, its Rust and TypeScript half | — | split at its resume | EXAMIN is Python. DEC-567's language-agnostic need comes with UPIM, ASMO and Release 1 (section 10 (v)) |

- **Rows:** the 87 rows of the moved tickets go with them, with their ticket's reason. They include the high rows W2-H019, H022, H024, H025 and H033. Every other open row stays with its Wave 2 ticket or its triage place.
- **The Contract.** Nine of the Contract's 17 Wave 2 items move to Wave 3: CAP-04.a, CAP-04.d, CAP-22.b, CAP-22.c, CAP-30.c, CAP-30.g, CAP-32.d, CAP-37.e and CAP-53.b. This is a re-baseline under DEC-105.
  - It is carried by W2-49's CIT-P (Contract v4.2, Q-14).
  - Exit criterion 7 then names 8 items: CAP-17.b, CAP-45.a, CAP-10.b, CAP-19.a, CAP-19.c, CAP-33.b, CAP-33.g and CAP-61.f, plus v4.2's lite CAP-44.h and CAP-43.b.
  - **The three DEC-105 options:**
    - (a) re-baseline now (recommended). The cost is one CIT-P line set, in a ticket that runs anyway;
    - (b) keep them in Wave 2, after W2-30, which adds about 10 to 14 ticket-days;
    - (c) defer the decision to W2-46, where the gap would show as a failed exit criterion.

## 9. Estimates

**Recalibrated after keystone 2 (DEC-834),** from measured ticket and close times; the old and new figures will be shown side by side. The cap columns below predate DEC-847, which sets no fixed cap.

**How they are made:**
- Each ticket takes about 1 day, plus 1 day per 150 estimated lines, plus half a day for FULL (WBS §4). A resume takes about 1 day.
- The work from now to Track A's verdict comes to about 75 ticket-days at 3 in flight, or about 25 working days with perfect packing.
- The ranges add dependencies and one review round in four.
- Closes cost 1 to 1.5 hours each on a quiet machine until W2-48 lands.
- Counted from day 0: the owner's commit, the bootstrap pin and W2-53's close.
- Confidence: low.
- **Lower than the plan's own figures, against what happened:** two of the first three critical-path tickets were built in 3.5 days, against 6.8 planned. **Higher:** code comes in at twice its estimate, and review rounds (lens A F2).

| Keystone | Lands about, day (cap 3) | With cap 4 from day 5 |
|---|---|---|
| 1 The pinned judge | the pin: 0; W2-59 and the re-pin: 2 to 4 | the same |
| 2 The queue and the cache | 4 to 7 | 4 to 7 |
| 3 Agents know what to do | 5 to 8 | 5 to 7 |
| 4 Memory (to W2-15a's baseline) | 14 to 18 | 12 to 15 |
| 5 The decision pipeline | 9 to 12 | 7 to 10 |
| 6 Sandbox and leads | 12 to 15 | 10 to 13 |
| 7 Releases and the pin ladder | 10 to 13 | 9 to 12 |
| 8 Hooks and CI | 14 to 17 | 12 to 15 |
| 9 Track A's verdict (W2-25) | 23 to 30 | 18 to 25 |
| 9 The copy's verdict (W2-28) | 26 to 35 | 21 to 30 |
| 9 The real repository's verdict (W2-30) | 31 to 44 | 26 to 39 |
| The exit (W2-47) | plus 2 to 3 | plus 2 to 3 |

**Owner waits are not included.** They are: the CIT-P approvals of W2-09, W2-11, W2-49 and W2-59; Q-13; the lefthook measure; the first release; and the go.

## 10. Scope, size and the other products (DEC-829 items (i) to (v))

**(i) (a) The EXAMIN path:** see section 4.9. W2-27's ticket file changes before W2-27 starts.

**(ii) (a), light: the size against DEC-064, recorded now.**
- **Measured:** 15,914 lines at `fecb870c`, of which 14,979 are in `src/gov` and 935 in the kernel hooks (lens G F9). DEC-064 set "glue ≈ 4.5k LOC across three waves"; this is about 3.5 times that.
- **The WBS in force:** adds about 6,860 estimated lines, and code comes in at about twice its estimate.
- **This plan:**
  - takes about 1,650 estimated lines out, with the moved tickets and W2-19's half;
  - glues instead of building in section 7's places;
  - removes about 260 lines (lens G R9).
- **The re-baseline decision** is taken with Wave 3's sizing at Track A's verdict.

**(iii) The admission rule.** A new ticket is admitted only when it serves an exit criterion or a Contract item, under DEC-801. W2-59 (exit criterion 1), W2-60 (exit criterion 5; CAP-35.c and CAP-36.a lite) and W2-61 (exit criterion 4; CAP-10) each pass it. Every other new need is a row.

**(iv) The eight unplanned Charter roles** (Charter §6):

| Role | Does EXAMIN's pilot need it? |
|---|---|
| Architecture | No |
| Frontend | No (3 HTML files, 1 script) |
| Backend | No for the pilot; first for its product work (FastAPI, 542 Python files) |
| Database and data | No for the pilot; first for its product work (Postgres, SQLAlchemy) |
| Integration and API | No for the pilot; for its product work (Anthropic and paid APIs, live tests) |
| DevOps and SRE | No |
| Security | No for the pilot; for its product work (API keys, candidate data) |
| Performance | No |

- **What the pilot needs:** the six roles and the ticket lead cover CAP-44.h's lite conditions, and one governed ticket closed with EXAMIN's own test command.
- **Decided (DEC-832):** backend, database and data, integration and API, and security become skill packs the engineer loads at launch, in a cut-down W2-33; the other four go to Wave 3 by that decision.
- **The orchestrator's recommendation was:** none stays in Wave 2. Defer all eight to Wave 3 by a recorded decision (DEC-105, defer), naming backend, database and data, integration and API, and security as EXAMIN's first.
- **Confidence:** medium.
- **The alternative,** if the owner wants governed product work on EXAMIN in Wave 2: keep those four as role files only, in a cut-down W2-33. That is about 1.5 days of product-spec work, with no new machinery.

**(v) The other products.**
- UPIM and ASMO are tied to W2-19's Rust and TypeScript half and to Release 1, in Wave 3.
- Wave 3 is sized, and Release 1 given a range, at Track A's verdict.

## 11. Decisions for the owner, with this plan (answered 2026-10-19: see section 0)

| # | Decision | Recommendation | Confidence |
|---|---|---|---|
| 1 | Approve this plan: the keystones, the order, the new and widened tickets, the moves | Approve | Medium |
| 2 | The Contract re-baseline of section 8 (nine Wave 2 items to Wave 3), through W2-49's CIT-P | (a) now | Medium-high |
| 3 | CAP-10's line | Keep 85 | Medium |
| 4 | DEC-062 and DEC-140 | Withdraw both | Medium, medium-high |
| 5 | Lens F's per-role values (section 6), prompt v3, the subagent model, agent teams, DEC-460's cause | As proposed; subagents on the parent's model; agent teams off | Medium |
| 6 | The eight roles | Defer to Wave 3, with EXAMIN's first four named | Medium |
| 7 | W2-59: the judge change and the hook lines (CAP-33; DEC-822 step 2) | Approve the scope; the CIT-P follows | High |
| 8 | W2-48's KPI restated as behaviour; testmon and coverage as one DEC-083 package when W2-48 starts | Approve | Medium-high |
| 9 | The four imported decision records whose ids fail the schema (`docs/imported/`) | Leave `docs/imported/` out of the schema check, as history | Medium |
| 10 | The path map gains `experiments/**` and the `evaluation_sets` block | Approve | High |
| 11 | The owner's acts: the pin; the held-out index check; the lefthook measure before W2-08; the S0b2 leftovers removed | As listed | — |
| 12 | The in-flight cap raised from 3 to 4 after keystone 2 | Approve, under the resource gate | Medium |

**What it blocks, and what waiting costs:**
- **Blocks:** every start and resume in Wave 2 (DEC-829 item 6).
- **Costs:** each day of waiting moves every date in section 9 by a day. The pin, the queued closes and W2-57 could start on approval of item 1 alone; the others can follow.
