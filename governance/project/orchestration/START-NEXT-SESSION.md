# Start here — the next CTO session (written 2026-11-06 by session 812bc5ce, after DEC-1079; was 2026-11-05 morning, 33b3628c)

You are the Wave 2 orchestrator (the CTO), `orchestrator DAEO-sdxk`, in the main tree on `w2/integrate`, in
**emergency mode**. This file maps everything you need, in order. Where it and an older note differ, this file holds;
the register and the owner's word hold over both.

## 1. The emergency: in force
- **What holds it:** DEC-1047 (the emergency raised; the refactoring and the basis), DEC-1049 (no nightly full suite
  until the owner's word), DEC-1050 (the twelve decide-first rows), DEC-1051 (everything stopped until the
  refactoring and the re-pins; nothing scheduled but the dispatcher), DEC-1052 (the basis, the rows, the plan D-0 to
  D-11; and **the basis as a standing practice**: every rule, gate, check or KPI line is assessed against the five
  questions at adoption, on symptoms and weekly, the lift-or-remove list to the owner first), DEC-1053 (D-0 done).
  DEC-1045 (no gitleaks scan here) stands.
- **Allowed:** the plan's steps in order (§5), with engineers, test designers, reviewers and research as in-session
  agents of their role; scoped test runs through `tools/heavy_slot.sh`; record commits (`Task:`, `Role:` trailers);
  restarts of the repository's own servers from committed configs; the shared reranker (W2-112) running.
- **Not allowed (must not start):** any lead (the dispatcher's ready list stays empty) and any landing or queue run
  until the plan's restart (after D-10 and the lift); the nightly and its checks (crontab lines stay commented,
  `# DEC-1049 stopped:`), the runs sweep (`# DEC-1050 stopped:`); `tools/bench_loop.sh`, `tools/usage_watch.sh`; the
  guard-refusal harvest (`dispatch/config.json` `guard_harvest_s` 10^9); any full suite (D-10 only, on the owner's
  word), any `gov close`, any gitleaks scan; any change to `.wslconfig` before the RAM upgrade; any machine change
  outside the repository except by an owner ACT (DEC-1038).

## 2. The reading list, in order
1. `governance/project/prompts/w2-orchestrator.md` §0 (the standing decisions in short) and §1 (session start).
2. **This file.**
3. `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`, its **RESUME HERE** (2026-11-05): the session state, what is open.
3b. **The morning package** `governance/project/orchestration/packages/LIFT-1/D4B-MORNING-2026-11-05.md`: the night's figures, the structure, the measurement set's result, every decision waiting on the owner.
4. `governance/project/orchestration/packages/LIFT-1/P1-PLAN.md`, its section **"DECIDED BY DEC-1052"** with the status
   table (D-4b's row: the measures, the structural fixes, the night).
5. `governance/project/orchestration/DECISIONS-IN-FORCE.md` (DEC-1068 to DEC-1073 and the standing practice: the
   stand-by file while waiting, the sentinel check, bisect only in a throwaway clone, **waits and stops by pid only
   through `tools/proc.sh`**).
6. `docs/DECISION_REGISTER.md`: DEC-1054 to DEC-1086 (**next free id DEC-1087**). DEC-1086 holds re-pin window 4 and
   every experiment until the owner has read `packages/LIFT-1/SEVEN-ANSWERS.md` and given the go.
7. **D-4b's record:** `.gov-runtime/scratch/orchestrator/drafts/d4b/NIGHT2.md` (the night of 2026-11-05: every
   structural step, the measurement set's single use), `DAY.md` (2026-11-04: m6, the trial stopped, the diagnosis,
   stage A, M1-M5) and `NIGHT.md` (2026-11-04's night: m2 to m5, the GPU trips); `DIAG.md`; the packages
   `D4B-STRUCTURE.md`, `LINK-INTEGRITY.md`, `D4B-MORNING-2026-11-05.md`; the research `docs/research/D4B-link-census.md`,
   `docs/research/W2-88-memory-practice.md`, `docs/audit/memory-recall-diagnosis-hidden.md`; the older packages
   `packages/LIFT-1/D4B-NIGHT.md`, `D4B-RESEARCH.md`, `D4B-AUDIT.md`; the measure's audit
   `docs/research/memory-measure-audit/` (RUBRIC.md version 2, VISIBLE.md, HIDDEN.md, NEW-VISIBLE.md) and
   `docs/audit/memory-measure-new-*.md`.
8. The ACTs: `packages/ACT-REPIN-W3.md` (done), `ACT-RERANK-TRIAL-1.md` (stopped after T2 by DEC-1070; T3/T4 wait),
   `ACT-HLABEL-1`, `-2`, `-3`, `ACT-HNEW-1`, `ACT-MSET-1`, `ACT-MSET-2` (done by the owner's writer, checker and
   operator).
9. `INTENT-DEC-1052.md`, `OWNER-GLOSSARY.md`; the agents' common rules `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`;
   reviewers `governance/project/briefs/JUDGEMENT.md`.

## 3. Done (2026-11-03 and 2026-11-04, session 33b3628c)
- **G-14, D-3, D-4** (DEC-1054 to DEC-1063), **D-8** (ACT-D8), **re-pin window 2** (`pin-9894b0cf`).
- **D-4b, the memory stage** (DEC-1055, DEC-1064 to DEC-1069): W2-61h, W2-91, W2-92, W2-13 (S5, S6), D-7 + G4
  (`27a80411`), W2-32 (S1-S5, S7 G1, S8 routing by question type and the phrasings, S9, S10 no CPU fallback, F1; the
  padded reranker bound; contextual headers), the five index-time methods M1-M5 (each off by default, `d9e9f9ea`); the
  adopted methods switched on (`dc8a2829`: `governance/project/rebuild.yaml`, `retrieval.yaml`).
- **The measures** (hit@5): m1 28/48, m2 29, m2g1 35, m3 37, m4 38, m5 38/48 (the product), and on the grown set
  **m6 65/80 (81.2 %): visible 36/40, hidden 29/40** (`24f06026`, the new baseline).
- **Re-pin window 3** (DEC-1068 (e)): `pin-8284fb408bd4` live (the owner's registry commit `b05f62b8`); the
  integration store at `8284fb40` with headers; the main tree's store rebuilt with it.
- **The measure's audit** (DEC-1068, DEC-1069): the rubric, both halves judged blind; every label fix applied (visible
  by an independent session; hidden by the owner's operator); the set grown to **40 + 40**, cross-checked.
- **Found and fixed:** `core.bare` turning true at 00:31 (cause: `git bisect run` from a linked worktree exports
  `GIT_DIR`, and W2-122's test helper ran `git init` with it; the fix for the tests waits for the proposal flow;
  the CTO's rule is in force); the GPU backstop's two trips (a request bound by count, not size: the padded bound now).

## 3b. Done on 2026-11-04 evening and the night (DEC-1070 to DEC-1073)
- **The trial stopped after T2:** the 0.6B on the trial copy equals m6. The live reranker was restored (DEC-1070 (1)).
- **The three sets:**
  - the tuning 40 and the hidden check 40;
  - `memory-verdict` (60), written blind and cross-checked (ACT-MSET-1/2), declared in both path maps.
  - **It has had its single use** (40/59, 67.8 %).
- **The recall diagnosis:** `DIAG.md`, the hidden kinds, the structural review `D4B-STRUCTURE.md`.
- **The structural fixes,** judged on the 79 (h24 apart):
  - **v456 adopted:** 67/79, gap 0.4 from 15.6;
  - **the stated links adopted** (`w2/W2-92-proto` `e884675b`): drift 184 → 0 unjoined;
  - every other step measured and not kept (the morning package, section 1).
- **Nothing from the prototypes is in the product.**
- **The link census** (`3d1c459e`) and **the link-integrity package** (`23610a2e`).
- **W2-88 owns the memory-building practice:** `docs/research/W2-88-memory-practice.md`.

## 3c. Done on 2026-11-05 and 2026-11-06 (session 812bc5ce; DEC-1075 to DEC-1079)
- **The 60's 19 misses classified** (`docs/audit/memory-verdict-misses-kinds.md`, `3f975a3e`; D4B-MISSES): ranked
  below 5 10, vocabulary 4, never retrieved 3, other 2.
- **The verdict set of 80 ready** (`memory-verdict-2`, DEC-1075, DEC-1076, DEC-1078): written and cross-checked by the
  60's writer and checker sessions (resumed), declared in both path maps; **unused until the decision point**.
- **The reranker trials** (D4B-TRIAL-W4, D4B-LEVERS): on the 138 (the 79 + the spent 59), the 0.6B 107, the 4B 8-bit at
  40 112 and at 24 112 (2.84 s alone, 33 s at 20 at once), mxbai 76 (its input checked on a stand-in: genuine), no
  reranker 95 (the reranker +12 net, p 0.04); the 4B's +5 not significant (p 0.27-0.33).
- **Re-pin window 4's builds:** W2-92 (the stated links, S7-S10) **merged into integrate** (`3679ca0b`; acceptance
  116/0, review READY, adopted by DEC-1071's rule, drift 0 → 190 of 190). W2-32 S11 (v456 as five pool settings) on
  `w2/W2-32` `1aeae788` (acceptance 257/0, review READY, round 2): 107/138 with the pool, 108 without, the halves' gap
  2.9 against 13.1, 1.20 s a call against 1.48 s; its "the harness question for question" line cannot hold (the
  harness's own fusion): a wording package to the owner is due.
- **The research survey** (`docs/research/D4B-memory-survey.md`, its draft beside it) and the **invention disclosure**
  (`packages/LIFT-1/MEMORY-INVENTION-DISCLOSURE.md`).
- **The GPU backstop pauses by process group only** (`tools/gpu_backstop.sh <pgid> ...`, 11 tests).

## 4. Live and running now
- **gov:** `~/.local/bin/gov` -> `pin-8284fb408bd4` (rollback `pin-9894b0cf`, one line in `ACT-REPIN-W3.md`).
- **The servers:** the shared embedder 127.0.0.1:11434 and the query server :11435, both on the GPU (29/29 layers).
- **The shared reranker:** the 0.6B, live under class 3 (restored after each trial window). The trial copy, its venv
  and the downloads are kept (`~/.local/share/gov-os/rerank-trial/`, `reranker-trial-venv`, `~/.cache/gov-os-trial/`).
- **Watchers:** the dispatcher (cron); the inbox waiter, `tools/sentinel_check.sh` and `tools/bare_watch.sh` (the
  session's background runs: **re-arm them at every session start**); `tools/gpu_backstop.sh <pgid> ...` armed per GPU
  job on its process groups; the sentinel's deadman.
- **Branches:** `w2/W2-32` (S11, round 2, not merged); `w2/W2-92-proto` and `w2/W2-32-proto` (prototypes, never merge).
- **Measure clones and scripts:** `~/gov-os-runs/D4B/` (w4-*, trial-w4*, g1, verdict ...); `drafts/d4b/` (score138.py,
  lift_push.py, w4_point.sh with `VISIBLE_FROM_CLONE`, w4_32_product.sh, leak_check.py, mset_*.py) and
  `drafts/rerank-trial/` (trial_window*.sh, trial_w4.sh).
- **Must not start:** §1's list.

## 5. Next, in order (DEC-1079)
1. **The memory work (no GPU first):** L1 (every comparison with gains, losses, exact McNemar); L2 (for the 31 misses
   on the 138, where the answer left the top 5, ids and ranks only); **source families** in `gov.retrieval.measure`
   (W2-61's code; tests first), then every kept run re-scored. Then L3 (the lift on a normalised score, the moves ahead
   bounded) and the three rerankers replayed under equal weights; L5 (phrasing prototype); L6 (records of work in a
   lower tier, one measured test, to the owner with figures).
2. **After L3:** one quiet window for the cascade (0.6B over 40, then the 4B over the top 12, its requests at 8 texts or
   12,000 padded characters) beside the 4B at 24; the best onto the fresh 80 once, beside the 0.6B, at the decision
   point. No install until then.
3. **W2-32's S11 wording** to the owner; then re-pin window 4 (W2-92, W2-32, W2-112's memory release) as an ACT.
4. **D-5, D-6, D-9 start now** (DEC-1079), their agents on the CPU, the GPU for the memory measures: the plan is in
   P1-PLAN's status table. LINK-INTEGRITY: file W2-129 and W2-130; W2-129's tests first.
5. Then D-10 (the owner's word), the lift; D-11 after it.

**Rules to carry:**
- Consistency is within 5 points on sets of about 80 (DEC-1074 (4)).
- Every used set is tuning or diagnostic.
- A structural fix is judged on all the tuning sets together (DEC-1071 (2)).

## 6. Waiting on the owner
- **The go after `packages/LIFT-1/SEVEN-ANSWERS.md` (DEC-1086).** Re-pin window 4 and every experiment wait on it.
  S11's wording, W2-135 and the search-again reader are decided (DEC-1086 A to C), to be acted on at the go.
- D-9's fates and K9 were decided and applied (DEC-1083, DEC-1084); W2-128 was filed.
- Still the owner's: the templates' approval and their `.claude/` copies (an ACT); the 150-id reconciliation list
  (O2); M3's adoption (DEC-1043), after E4.

## 7. The checks at start (after the prompt's §1)
1. `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; `git status --porcelain` in the main tree empty.
2. Register: your session id into `log/cto-session.txt`; arm `tools/inbox_wait_quiet.sh` and `tools/sentinel_check.sh`
   (the Bash tool's background runs); one test push; the sentinel's last line in `log/deadman.log` under 10 minutes old.
3. **Holds:** if `log/act-in-progress.txt` exists, read it: an owner's ACT means no main-tree commit. While you wait on
   the owner or the operator, write `log/cto-standby.txt`. **Every wait and stop by pid only (`tools/proc.sh`).**
4. **The pin:** `readlink -f ~/.local/bin/gov` = `/home/usain/.local/share/gov-os/pin-8284fb408bd4/bin/gov`; the guard:
   `python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS` = `PASS`.
5. **The servers on the GPU:** both embedders 29/29 layers; the reranker: `tail -2 ~/.cache/gov-os/rerank.log`
   `READY ... cuda:0`, and `gov retrieve` from `~/gov-os-worktrees/W2-00-store` gives `rerank.by` = `service`.
6. **`core.bare`:** `git --git-dir=.git config --get core.bare` = `false`; `tools/bare_watch.sh` running.
7. **The inbox:** read and file each item; a `*-sentinel-down.txt` is pushed to the owner at once.
8. After every record commit: `python3 .gov-runtime/scratch/orchestrator/tools/structural_pass.py /home/usain/Dynamic-Agentic-Engineering-OS HEAD~1`.
