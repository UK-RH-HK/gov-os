You are the ticket lead for ticket `DAEO-ha8z` (`W2-49`, "Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P)"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-49` on branch `w2/W2-49`.

**This is run 3: the merge-back and the decided rest (DEC-941 item 2, DEC-745 item 2, DEC-750 item 5), not a new round.** `git rev-parse --short=12 HEAD` must show `19d452461125`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Start only after W2-51 has closed** (DEC-744 item 3, DEC-745 "Applied"): `git merge-base --is-ancestor w2/W2-51 w2/integrate` must succeed, and `git show w2/integrate:.tickets/DAEO-egsy.md` must show `status: closed`. If either fails, stop and return PACKAGES naming it.

**Read first:**
- your run-2 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md` ("What the resume lead does", "Open");
- the ticket file (`.tickets/DAEO-ha8z.md`), the CIT-P (`docs/changes/W2-49-CIT-P.md`, §8 and §13) and the CIT-E;
- DEC-741, DEC-744, DEC-745, DEC-748, DEC-750 (item 5), DEC-752 (item 1), DEC-786, DEC-825 (item 3), DEC-841 and DEC-941 (item 2).

## Why you start now

- **W2-49 is built and verified work,** held since 2026-10-17 for the close order (DEC-737). Contract v4.2 is applied (`90c4d20a`), the 273 version lines (`5a6a12f5`), the eight records of DEC-745 item 3 (`7f935156`) and the CIT-E (`b9e4917e`); run 2 ended green. Its holds: W2-01 is closed; W2-51 closes before this run starts.
- **The owner's re-plan (DEC-941, 2026-10-29):** the nine held tickets are merged back, re-verified and closed. W2-49 (the Contract text to v4.2) is one of the four taken in spare lead capacity (item 2), and capacity is spare now (DEC-942). "Deferred to Wave 3" means unbuilt work, not built work waiting for a close.
- **The close order, W2-51, then W2-49, then W2-52:** W2-51 (DAEO-egsy) merges and closes first, since your KPI line 3 and failure line are tested against its validator (DEC-744 item 3, DEC-741 item 4). W2-52 (DAEO-siiz) is stacked on this branch (DEC-786; `19d45246` is in `w2/W2-52`, merged as `29bef106`) and closes after you; W2-16 (DAEO-49o5) is stacked on it too and waits for your close. Each merges into `w2/integrate` and closes before the next. Your return goes to the orchestrator, who merges and closes in that order.
- **Where the branch stands:** 13 commits ahead of `w2/integrate` and 796 behind (at `cbdeb682`, before W2-51's merge); merge base `00fe09b6fc5c`. A dry merge (`git merge-tree --write-tree w2/W2-49 w2/integrate`) reports **no conflict**. Nothing on `w2/integrate` since the merge base touches `docs/contract/**`, `docs/changes/W2-49-*` or `tests/acceptance/W2-49/`.
- **What is still owed, as the register stands:**
  - **Decided, in your paths, for this run:**
    - DEC-745 item 2: the eight rows of `docs/contract/SOURCE_MAP.csv` that CIT-P §8 names (rows 235, 237, 248, 251, 256, 280, 283 and 292) follow v4.2; no other row changes (rows 252 and 282 stay W3, since A9 and A11 do not move). DEC-745 gives them to "the lead that merges `w2/integrate` into W2-49's branch before its close, after W2-51 closes".
    - DEC-750 item 5 (P-W2-16): `docs/contract/capabilities/CAP-45.a.md` is regenerated from the approved v4.2 (today it has a 4.2 version line over 4.1 item text, since D (ii)), and every capability record's `status:` line is set to the Contract's ACCEPTED.
    - Your KPI success line 3 and failure line, pending W2-51 since run 1: their tests, against W2-51's validator (`docs/plan/tools/validate_w2.py`).
  - **Not decided as a change, and not this run's (they go back as PACKAGES):**
    - **DEC-841:** nine Contract items (CAP-04.a, CAP-04.d, CAP-22.b, CAP-22.c, CAP-30.c, CAP-30.g, CAP-32.d, CAP-37.e, CAP-53.b) move to Wave 3, "carried by W2-49's CIT-P, as part of Contract v4.2 (Q-14), in W2-49's resume". The approved CIT-P (DEC-741) predates it, and `contract.yaml` here still has all nine at `wave: W2`. DEC-841's status line says the Contract changes only through W2-49's CIT-P, **which the owner approves**: an addendum to the CIT-P needs its independent review and the owner's approval before any Contract text changes (CAP-33). The sweep of 2026-10-20 also has the lead adding a DEC-841 KPI to the ticket file; a lead never edits ticket files (the orchestrator's).
    - **DEC-825 item 3:** "W2-49's resume adds the missing providers, records by decision which Contract form is the authority, and adds a check that compares the forms (or generates the readable form from the YAML)". The decision record is the owner's (through the orchestrator), and a check is code outside your paths.
- **No owner commit is needed for this run's steps.** The Contract text was approved by DEC-741; DEC-745 and DEC-750 approve the source-map rows, CAP-45.a and the status lines; the orchestrator, not the owner, commits records of owner decisions (DEC-861). `Role: owner` commits stay for ratchet, accepted-history and `acceptance_exemptions` entries only (DEC-862, DEC-906), none of which this run touches.
- **No review, no probe:** W2-49 is STANDARD, so no reviewer before the merge (DEC-498). The CIT-P had its independent review in run 1 (CAP-33). No probe record exists under `docs/probes/DAEO-ha8z/` to go stale (DEC-895 does not apply).

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-49`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-ha8z`, `Implements: DEC-941` and `Role: orchestrator` in the final trailer block). Never `-s ours`, never drop this ticket's side (DEC-750 item 3).
   - A conflict on `docs/contract/**`, `docs/changes/W2-49-*` or `tests/acceptance/**`: `git merge --abort`, and return PACKAGES naming each file (the Contract text is the owner's). Any other conflict that a mechanical fix resolves (both sides kept as written, neither side's behaviour changed): resolve it and say how in the return. Anything else: `git merge --abort`, and return PACKAGES.
   - After the merge:
     - `grep -c '^### DEC-941' docs/DECISION_REGISTER.md` must show 1;
     - `test -f docs/plan/tools/validate_w2.py` must succeed (W2-51's validator is in the tree).
     If either check fails, stop and return PACKAGES.
2. **Tests first, by a fresh independent test designer** (`gov launch`, sandboxed, `--effort xhigh`), in `tests/acceptance/W2-49/`, as described behaviours. New tests only; an existing case changes only where DEC-750 item 5 contradicts it, with a `Rewrite-Reason:` naming DEC-750 item 5 and no expectation lowered (DEC-906):
   - **KPI line 3:** on this tree, W2-51's validator (`python3 docs/plan/tools/validate_w2.py --root <tree>`) passes `cit-p-moved-items` and `cit-p-lines-applied`, naming the three items moved to Wave 2, lite (CAP-43.b, CAP-44.f, CAP-44.h), and the six CIT-P lines (those three plus the split's CAP-43.d, CAP-44.k and CAP-44.l), as W2-51's run 1 saw on these files.
   - **The failure line:** on a copy of the plan files (in the test's own temporary folder), a Contract item moved to Wave 2 with no CIT-P line fails the validator by name; so does a CIT-P line with no change in the Contract.
   - **DEC-745 item 2:** the eight source-map rows state v4.2's wave for the moved parts; rows 252 and 282 still say W3; no other row differs from the merge base's `SOURCE_MAP.csv`.
   - **DEC-750 item 5:** `CAP-45.a.md`'s item text is v4.2's (D (ii)'s Wave 2 wording); every record under `docs/contract/capabilities/` says `status: ACCEPTED`, as both Contract files do.
   - The tests must not need DEC-841's move, and must not fix the nine items' wave either way: that is the owner's open question.
   
   Then **check red yourself.** The validator lines may already pass (the validator and v4.2 are both in the tree): name each such case as green at the red check, with why. The DEC-745 and DEC-750 cases must be red, each for its stated reason.
3. **A fresh product-spec worker** (`gov launch`, sandboxed, `--effort high`), in the ticket's allowed paths only, in two commits, each with `Task: DAEO-ha8z` and `Role: product-spec`:
   - the eight `SOURCE_MAP.csv` rows (`Implements: DEC-745`);
   - `CAP-45.a.md` regenerated from the approved `contract.yaml`, and the `status:` line of every capability record set to ACCEPTED (`Implements: DEC-750, DEC-614`);
   - and one line each in the CIT-E (`docs/changes/W2-49-CIT-E.md`) saying what this round applied and under which entry. The CIT-P is not changed, and no Contract text changes (DEC-841's nine items stay as they are).
   - If the guard refuses any of these writes, return PACKAGES.
4. **Verification: in full,** in the close's form (LEAD-w2-common), plus `pytest --collect-only -q` over `tests` (DEC-868).
   - Rebuild from this worktree's code (check `gov.__file__` first), under the machine's rebuild lock: `flock /tmp/gov-os-rebuild.lock` around the rebuild command, never `--no-embeddings`. Name every entry or record the load lists as `invalid`; `invalid: []` is expected (276 records now say ACCEPTED: watch the record load).
   - The full run goes under `flock /tmp/gov-os-verify.lock` (one run at a time, machine-wide; a close queue holds that lock while it closes), split over several background jobs with a runner that resumes (run 2's single job hit the 2-hour background limit).
   - Look hardest at:
     - `tests/acceptance/W2-49/` and `tests/acceptance/W2-51/`;
     - the suites that read the Contract or the records: W1-48, W1-41, W1-30, and W1-11 (records with an ACCEPTED status);
     - `gov check`: name every check that is not green, with its cause.
   - Run W2-51's validator over the merged tree once, and quote it. A FAIL there that is not one of your KPI lines is a plan finding, not a red.
   - Never run `docs/plan/tools/validate_s1.py` (DEC-738).
   - **The nightly:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite. Between 00:30 and 05:30, start no worker and no suite run (DEC-942 item 5). From about 01:00, start no full verification run that cannot finish before 02:00. A close queue may be running in the main tree: run your suites only when the 1-minute load is under 20.
   - **Known:** W1-42's accepted reds; the load-sensitive cases, re-run alone; W1-46's network case (curl exit 56), re-run alone. Any other red is named with its cause.
5. **Repair: at most one batch.**
   - A red in this ticket's files: a fresh product-spec worker (`gov launch`, sandboxed, `--effort high`), in the ticket's allowed paths only.
   - A red in `tests/acceptance/**`: a fresh independent test designer (DEC-906), each change with a `Rewrite-Reason:` and no expectation lowered.
   - Then the red cases and their suites again; a second full run only if a file changed.
6. **Reviews: none.** W2-49 is STANDARD (DEC-498).
7. **Checkpoint and trailers:** `gov checkpoint` at the end (DEC-511), committed with this ticket's trailers. Run `trailer_gate.py` on your worktree before you return (LEAD-w2-common, DEC-927 item 2).
8. **Return PACKAGES** (P-A and P-B below, which the owner decides; DEC-220 delegates no Contract scope), with the branch state as DONE would give it: the final head (W2-52's lead merges it before its probe, and W2-16's later: DEC-752 item 1), each suite's result, and whether the branch is ready to merge into `w2/integrate` after W2-51's close.
   - **P-A, DEC-841 (the owner's):** the nine items' move needs a CIT-P addendum, its independent review, an answer round and the owner's approval before the text changes (CAP-33, DEC-105). Give the three options with their costs: (a) apply now, in a run 4 of this ticket (the addendum, review, approval, tests first, `contract.yaml`, `CONTRACT_v4.md`, the nine records, the source map's rows if any, the CIT-E, re-verification), with its size in hours and what waits on it (W2-52, W2-16, W2-28 and W2-30 through DEC-825 item 3, exit criterion 7); (b) close W2-49 on v4.2 as built and approved, and carry DEC-841's move to a new ticket; (c) re-baseline. Note DEC-880's change to DEC-841 (W2-38's lite form back in Wave 2 as W2-66) and what it means for CAP-53.b. Your recommendation and confidence.
   - **P-B, DEC-825 item 3:** what "the missing providers" are on this tree, which form `contract.yaml`'s records already name as the authority (DEC-614), and where a form-comparing check would live (outside your paths). Your recommendation and confidence.
   - Carry run 2's residuals as they stand (W2-I017, carried under J (i) at W2-30's close; W2-L343, done in `90c4d20a`), mark those this run closed (CAP-45.a, the record status, the eight rows), and add any new one. Name the temporary folder run 2 left, `.gov-runtime/scratch/ps-run2/` in this worktree, with its size.

**The park rule (DEC-941 item 2):** if the repair grows beyond this one run, stop and return PACKAGES naming the cost. That covers a second repair batch, a fix outside the ticket's paths, a red whose cause is another ticket's code, and any step that would change the Contract text beyond DEC-741's approved v4.2 (DEC-841's move among them). Name what is left, its size in lines and hours, and what waits on it (W2-52 and W2-16, both stacked on this branch; W2-28 and W2-30, whose entry criterion is your merge).

**Running beside you:**
- W2-52's lead (stacked on this branch) works in its own worktree. It does not touch your paths and you do not touch its; it merges your final head before its probe.
- W2-03's lead holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`.
- W2-05's lead holds the git-environment lines across `src/gov/**/*.py`, `src/gov/util/gitenv.py` and the lefthook files.
- W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
- W2-61 holds `src/gov/retrieval/measure.py`.
- W2-60a holds `src/gov/launch/launcher.py`, `role.py` and `record.py`.
- W2-77 holds `src/gov/close/nightly.py`.

Do not touch them. If a fix needs a change there, return PACKAGES.

**Estimate:** about 5 hours:
- the merge and the rebuild, about 30 minutes;
- the test design and the red check, about 1 hour;
- the product-spec worker, about 1 hour (eight rows, one record, 276 one-line changes, the CIT-E lines);
- one full run, about 95 minutes (the last two nightly runs took 5,623 s and 5,707 s);
- the packages and the return, about 30 minutes.

With one repair batch, up to 7 hours.

---
