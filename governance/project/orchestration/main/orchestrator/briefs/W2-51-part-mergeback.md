You are the ticket lead for ticket `DAEO-egsy` (`W2-51`, "The Wave 2 plan validator"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-51` on branch `w2/W2-51`.

**This is run 2: the merge-back (DEC-941 item 2), not a new round.** `git rev-parse --short=12 HEAD` must show `c2c80e6c8f12`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-1 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md` ("What the resume lead must do", and the verification at `73d28a4a`);
- the ticket file (`.tickets/DAEO-egsy.md`), DEC-744, DEC-741 (item 4), DEC-841 (item 3) and DEC-941 (item 2).

## Why you start now

- **W2-51 is built and verified work,** held since 2026-10-17 for the close order (DEC-737). Its hold is gone: W2-01 is closed.
- **The owner's re-plan (DEC-941, 2026-10-29):** the nine held tickets are merged back, re-verified and closed. W2-51 is one of the four taken in spare lead capacity (item 2), and capacity is spare now (DEC-942).
- **The close order, W2-51 first:** W2-49 (DAEO-ha8z) closes after W2-51 (DEC-744 item 3, DEC-741 item 4): W2-49's KPI line 3 and failure line are tested against your validator. W2-52 (DAEO-siiz) is stacked on W2-49 (DEC-786) and closes after it. So the order is **W2-51, then W2-49, then W2-52**: each merges into `w2/integrate` and closes before the next. Your return goes to the orchestrator, who merges and closes W2-51 first; nothing else waits in this run.
- **Where the branch stands:** 4 commits ahead of `w2/integrate` and 795 behind; merge base `61ca9c1aa62b`. A dry merge (`git merge-tree --write-tree w2/W2-51 w2/integrate`) reports **no conflict**.
- **What changed in your inputs meanwhile:** nothing on `w2/integrate` touches `docs/plan/tools/`, `tests/unit/plan/`, `tests/acceptance/W2-51/` or `docs/contract/`. `docs/plan/WAVE_2_WBS.md` changed (+816/−78):
  - §1's ticket table now has rows for W2-51 and W2-52 (your run-1 plan finding is fixed);
  - exit criterion 7 now names DEC-841's eight items plus v4.2's lite items; the baseline line your `cit-p-moved-items` reads ("The Contract's 17 Wave 2 items, by ticket.") is still there, as written.
  - Your acceptance tests build their own plan trees (`w2_51_support.py`), so none of this should move them. The validator over the real tree will.
- **No review, no probe:** W2-51 is STANDARD. No reviewer before the merge (DEC-498), and no probe record exists under `docs/probes/DAEO-egsy/` to go stale (DEC-895 does not apply).

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-51`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-egsy`, `Implements: DEC-941` and `Role: orchestrator` in the final trailer block). Never `-s ours`, never drop this ticket's side (DEC-750 item 3).
   - If git reports a conflict that a mechanical fix resolves (both sides kept as written, neither side's behaviour changed), resolve it and say how in the return. Any other conflict: `git merge --abort`, and return PACKAGES naming each file.
   - After the merge, `grep -c '^### DEC-941' docs/DECISION_REGISTER.md` must show 1. If not, stop and return PACKAGES: the trailer gate would refuse every `Implements: DEC-941`.
2. **Rebuild** from this worktree's code (check `gov.__file__` first), under the machine's rebuild lock: `flock /tmp/gov-os-rebuild.lock` around the rebuild command, never `--no-embeddings`. Name every entry or record the load lists as `invalid`; `invalid: []` is expected.
3. **Verification: in full,** in the close's form (LEAD-w2-common), plus `pytest --collect-only -q` over `tests` (DEC-868). The full run goes under `flock /tmp/gov-os-verify.lock` (one run at a time, machine-wide; a close queue holds that lock while it closes). The branch changes no file under `src/`, but its tests and the 795 commits of `w2/integrate` have never run as one. Look hardest at:
   - `tests/acceptance/W2-51/` and `tests/unit/plan/`;
   - **the validator over the merged tree,** `python3 docs/plan/tools/validate_w2.py` (no `--root`): quote its output whole. A FAIL there is a plan finding, not a red of this ticket (no test runs it on the real tree): name each one, with what it names. In particular:
     - `wave2-tickets`: name every id on one side only (tickets filed on 2026-10-29 may not all have a §1 row yet);
     - `contract-items-delivered` and `contract-items-cited-by-tests`: the Contract on `w2/integrate` is still 4.1 with the 17 items in Wave 2 (W2-49 has not merged; DEC-841's move is not applied anywhere), while exit criterion 7 names eight. Say which list the validator read;
     - `cit-p-moved-items` and `cit-p-lines-applied` on this tree (0 and 0 expected until W2-49 merges).
   - **On W2-49's real files again,** as in run 1: a scratch tree in your session's temporary folder (never under the worktree), with the merged tree's WBS and `w2/W2-49`'s `contract.yaml`, `CONTRACT_v4.md` and CIT-P read with `git show`. Quote both checks' lines. W2-49's lead uses this result.
   - **The nightly:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite. Between 00:30 and 05:30, start no worker and no suite run (DEC-942 item 5). From about 01:00, start no full verification run that cannot finish before 02:00. A close queue may be running in the main tree: run your suites only when the 1-minute load is under 20.
   - **Known:** W1-42's accepted reds; the load-sensitive cases, re-run alone. Run 1's W1-46 live-session errors (`test_w1_46_live_sessions.py`, the research fixture's `probe.sh` exit 127) are a serial-only, nightly case: say whether they recur. Any other red is named with its cause.
4. **Repair: at most one batch.**
   - A red in this ticket's code: a fresh engineer (`gov launch`, sandboxed, `--effort high`), in the ticket's allowed paths only (`docs/plan/tools/validate_w2.py`, `tests/unit/plan/**`).
   - A red in `tests/acceptance/W2-51/`: a fresh independent test designer (DEC-906), each change with a `Rewrite-Reason:` and no expectation lowered.
   - Then the red cases and their suites again; a second full run only if code changed.
   - A validator FAIL over the real tree is not a red: no repair for it in this run.
5. **Reviews: none.** W2-51 is STANDARD (DEC-498).
6. **Checkpoint:** `gov checkpoint` at the end (DEC-511), committed with this ticket's trailers.
7. **Your trailers** (LEAD-w2-common, DEC-927 item 2): run `trailer_gate.py` on your worktree before you return.
8. **Return** DONE (green; ready to merge into `w2/integrate`, then the close queue, **before W2-49**), or PACKAGES. Carry run 1's residuals in the return as they stand (the WBS-baseline wording dependence; the empty pass on a Contract with no Wave 2 items), mark the one now fixed (the §1 table), and add any new one. Name the temporary folder run 1 left (its session scratchpad's `w249/`) if you find it, with its size.

**The park rule (DEC-941 item 2):** if the repair grows beyond this one run, stop and return PACKAGES naming the cost. That covers a second repair batch, a fix outside the ticket's paths, or a red whose cause is another ticket's code. Name what is left, its size in lines and hours, and what waits on it (W2-49's close and its KPI line 3 and failure line, then W2-52; exit criterion 7's two-way check).

**Running beside you:**
- W2-49's lead may run beside you. It merges `w2/integrate` only after your branch has merged there, and it never touches your paths.
- W2-03's lead holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`.
- W2-05's lead holds the git-environment lines across `src/gov/**/*.py`, `src/gov/util/gitenv.py` and the lefthook files.
- W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
- W2-61 holds `src/gov/retrieval/measure.py`.
- W2-60a holds `src/gov/launch/launcher.py`, `role.py` and `record.py`.
- W2-77 holds `src/gov/close/nightly.py`.

Do not touch them. If a fix needs a change there, return PACKAGES.

**Estimate:** about 2.5 hours:
- the merge and the rebuild, about 30 minutes;
- one full run, about 95 minutes (the last two nightly runs took 5,623 s and 5,707 s), split over several background jobs (run 1's single job hit the 2-hour background limit);
- the validator runs and the return, about 20 minutes.

With one repair batch, up to 4.5 hours.

---
