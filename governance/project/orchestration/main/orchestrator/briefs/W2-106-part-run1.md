You are the ticket lead for ticket `DAEO-0mtg` (`W2-106`, "The template's hook lines pinned"), profile FULL, priority 0 (DEC-966). You work only in the worktree `/home/usain/gov-os-worktrees/W2-106` on branch `w2/W2-106`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `1f0bf2836dc2`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Why:** the template's hook lines run `python3 "$h"` with no pinned interpreter (`template/governance/kernel/settings.json` lines 8, 20, 32). W2-90's test designer measured that a session whose `PYTHONPATH` points at an edited copy of `gov` gets a refused write through (exit 0): a fail-open that must not ship in EXAMIN's copy. This repository's lines carry the pinned form (DEC-822, W2-59). The owner chose (a) (DEC-966 item 2; `packages/P-W2-90-1.md` P1-B).
**Read first:** the ticket (`.tickets/DAEO-0mtg.md`) whole; DEC-966, DEC-822, DEC-957, DEC-965, DEC-801; `packages/P-W2-90-1.md`; this repository's own hook lines in `.claude/settings.json` and `.rulesync/hooks.jsonc` (the pinned form) and W2-59's README; W2-90's helper (how a project is generated and its hook lines run).
- **FULL:** after green, a fresh reviewer (brief A3, `JUDGEMENT.md`, effort max) probes the generated project's hook lines for any way they fall back to an unpinned interpreter or let a refused call through.

## The decisions for this run
- **The work order in parallel (DEC-959 item 7, DEC-963, the common brief's loop):** the independent test designer in the tests worktree (`/home/usain/gov-os-worktrees/W2-106-tests`, retrieving only from the integration branch's store) and the engineer in this worktree start at the same time, both from the KPIs; when TESTS-READY appears, the engineer merges the tests branch and runs them once.
- **Verification (DEC-959 item 1, DEC-962):** your acceptance suite, plus `select_tests.py` once before returning; a full run only if it says so, through `verify_lock.sh` (it waits for the gate's room). Known reds you do not own are named, re-run alone, and left. Since W2-90's merge, 7 named cases are red after ACT 1 (W1-05's two orchestrator-asks cases, W1-46's research npm-install case, four W2-59 cases): your ticket's change should turn the four W2-59 cases green once W2-90's next round moves them; do not edit them yourself.
- **Installs** are refused for you; raise any as a P1. Scratch: 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-106`.

Return the twelve fields, `brief_gaps:` and `guard_refusals:`, status DONE (commits, suites, the passing probe record) or PACKAGES.


**DEC-968 (owner, 2026-10-31), overriding anything above about a full run:** never run the full suite, whatever your change, core included: the nightly runs it once a day. Your verification is the scoped set `select_tests.py` gives (always `scoped` now; for a core change it names `core_changed` and selects every suite the change can reach), run once before you return, in the close's form. A case that fails there and that your change did not cause (it fails on `w2/integrate` too) is named in your return for the CTO to deal with at once; one your change caused is yours to fix. Exit 2 from the selection (scope `refused`): return PACKAGES with its reasons.
