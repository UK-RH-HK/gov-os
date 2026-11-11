# The lift's re-pin ACT (ACT-REPIN-W5): prepared, rehearsed in a scratch mirror, ready for review (DEC-1125 (3) (i))

Read `NIGHT-common.md` first. Role: orchestrator helper (ACT preparer), Sonnet high, class C2.

## What the owner gets in the morning
`governance/project/orchestration/packages/ACT-REPIN-W5.md`, in the form of `packages/ACT-REPIN-W4.md` (read it
whole first: it is the model), with the owner's exact commands, the rehearsal's evidence, the rollback, and what the
CTO does after. The owner runs it by hand in a plain terminal (DEC-928 item 3), after pushing (DEC-1087 (7)).

## The task
1. **Learn the last re-pin:** `pin/REPIN-COMMANDS-W4.sh`, `pin/repin6_checks.sh`, `pin/repin6_registry.py`,
   `pin/rehearse_repin6.sh`, `pin/dryrun_w4.sh` (all under `.gov-runtime/scratch/orchestrator/`), and the W4
   rehearsal logs `log/repin-w4-rehearsal-r*.txt`. The live pin is `pin-bcea09060ebc` (`readlink -f ~/.local/bin/gov`).
2. **The candidate:** `w2/integrate` at the commit you start from (`git -C <main> rev-parse w2/integrate`). `src/` is
   frozen tonight; record commits (tickets, packages, the register) continue. Design the script so it builds the
   wheel from the candidate commit's clean export, and **stops** (`STOP: ...`, nothing switched) if `src/`,
   `pyproject.toml` or anything else the wheel is built from differs between the candidate and `w2/integrate` at run
   time. The store is rebuilt at the run-time head (records may have moved) or at the candidate: choose, and say why.
3. **What changed since the live pin:** `git diff --stat bcea09060ebc <candidate> -- src/ pyproject.toml` and the
   tickets merged since (git log). For each build that changes what sessions run (the guard and its hook, the
   launcher, the reranker service, retrieval, the store's schema, rebuild, the CLI), add a check that it is found in
   the new pin, as W4 did. Decide from the diff: does the shared reranker's service code differ (then restart it from
   the new pin, class 3, as W4 part 6)? Do the git hooks (`.git/hooks/reference-transaction`, W2-116) need a change?
   Does any store schema change force a full rebuild?
4. **DECIDED-NOT-DONE row 88**, what this re-pin must carry from W2-141's rebuild (`beec1f2f8`): the four engineer
   near-miss cases in `drafts/g14/test_g14.py` (S1/S2 refuse them by design): revise them in your copy of the checks
   or expect them red by name; re-run `drafts/w2-141-rebase/rehearse.sh` with the candidate pin (review F4); fold F1
   and F3 into the README it names; note D1 (a `git diff` of two blob refs falsely refused) as a row for the CTO.
   Read `drafts/w2-141-rebase/REHEARSAL.md` and `review-session.summary` for F1-F4 and D1.
5. **The named reds (DEC-1125 (1), DEC-1123 (3)):** the warm-query latency is not a re-pin gate; the trailers family
   is a warning. Keep every other W4 check (the guard's suites, the hooks, the store, a search with both facets and the
   service, `gov context`, the hook's time).
6. **Rehearse it whole, twice** (DEC-1057), as W4 did, against a scratch mirror under `/tmp/gov-os-emg-repin5/`: a
   scratch gov link and pins folder (the live pin linked, never written), scratch store halves (shared clones with
   copies of their stores), a registry clone, a scratch hooks folder, `GOV_REPIN_SKIP_RERANK=1` (the live reranker is
   never restarted; part C still compares its bytes). **Never touch** the live `~/.local/bin/gov`,
   `~/.local/share/gov-os/pin-*`, the live store links (`/home/usain/gov-os-worktrees/W2-00-store`), the live
   `.git/hooks`, the servers. Check afterwards that each is unchanged (sha256 or `readlink` before and after, in the
   log). The GPU part (S): wait while a measure or a rebuild runs, take the GPU lock, the W4 limits. Heavy steps
   through `tools/heavy_slot.sh` / `tools/rebuild_slot.sh`. Run 1 may stop: fix and re-run; the last run is the script
   exactly as handed over, exit 0, `RE-PIN DONE`.
7. **Write:** `pin/REPIN-COMMANDS-W5.sh`, `pin/repin7_checks.sh`, `pin/repin7_registry.py`, `pin/rehearse_repin7.sh`
   (and helpers you need, `pin/*7*`), logs `log/repin-w5-rehearsal-r<N>.txt`, notes under `drafts/repin-w5/`, and the
   package `governance/project/orchestration/packages/ACT-REPIN-W5.md` with the scripts' sha256 (12 digits each side,
   as W4). The registry commit in the script is the owner's (`Role: owner`, as W4's).

## Paths you may write
`.gov-runtime/scratch/orchestrator/pin/*W5*`, `pin/*7*`, `log/repin-w5-*`, `drafts/repin-w5/**`,
`governance/project/orchestration/packages/ACT-REPIN-W5.md`, `/tmp/gov-os-emg-repin5/**`. Nothing else.

## Return
The twelve fields, short: the candidate commit, the wheel sha256, what changed since `bcea09060ebc` that the checks
cover, the reranker and hook decisions, each rehearsal run's exit and time, the live paths unchanged, row 88's four
items, open points for the reviewer. Estimate 2-3 h.
