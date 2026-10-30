You are the ticket lead for ticket `DAEO-siiz` (`W2-52`, "The lite A7 and A10 stage records"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-52` on branch `w2/W2-52`.

**This is run 3: the merge-back and the resume (DEC-941 item 2, DEC-802, DEC-814).** `git rev-parse --short=12 HEAD` must show `a21f06a78abc`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-2 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md` ("What the resume lead does", and the residuals);
- the probe record `docs/probes/DAEO-siiz/PR-DAEO-siiz.md` (pass at `643aeeef`);
- the ticket file (`.tickets/DAEO-siiz.md`) and DEC-741, DEC-786, DEC-795, DEC-796, DEC-800, DEC-802, DEC-810, DEC-814, DEC-895 and DEC-941 (item 2).

## Why you start now

- **W2-52 is built and reviewed work,** held since 2026-10-19. It is stacked on the held W2-49 (DEC-786): `w2/W2-49` at `19d452461125` is in this branch, merged as `29bef106`. Run 2's loop ended green and its probe passed. Two packages were left:
  - P-6 is decided by DEC-814: the paths gain `.claude/skills/adopt/SKILL.md`, rulesync's output only, and a fresh engineer regenerates it in this resume, before the resume's fresh probe.
  - P-7 is decided by DEC-810. F-1 and F-3 are rows W2-M378 and W2-M379 for W2-28.
- **The owner's re-plan (DEC-941, 2026-10-29):** the nine held tickets are merged back, re-verified and closed, those in EXAMIN's minimum first; W2-52 is one of them (item 2).
- **Where the branch stands:**
  - 22 commits ahead of `w2/integrate` (13 of them W2-49's) and 730 behind; merge base `d80a0308afb2`, this ticket's claim.
  - A dry merge (`git merge-tree --write-tree`) reports **no conflict**.
  - Nothing on `w2/integrate` since the merge base touches this ticket's paths, W2-49's paths, `tests/acceptance/W2-49/` or `tests/acceptance/W2-52/`. The merge brings in what the ticket depends on as it now stands: W2-02's adoption verdict (closed 2026-10-21, after your probe) and 730 commits of shared code.
- **The close order:** W2-52 closes after W2-49, and W2-49 after W2-51 (`deps`). Your return goes to the orchestrator, who merges and closes in that order. This run does not wait for it.

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-52`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-siiz`, `Implements: DEC-941` and `Role: orchestrator` in the final trailer block). Never `-s ours`, never drop this ticket's side or W2-49's (DEC-750 item 3).
   - If git reports a conflict that a mechanical fix resolves (both sides kept as written, neither side's behaviour changed) outside `tests/acceptance/**`, resolve it and say how in the return. A conflict in `tests/acceptance/**`, or any other conflict: `git merge --abort`, and return PACKAGES naming each file.
   - After the merge:
     - `grep -c '^### DEC-941' docs/DECISION_REGISTER.md` must show 1;
     - `grep -c '^- .claude/skills/adopt/SKILL.md' .tickets/DAEO-siiz.md` must show 1 (the orchestrator's DEC-814 edit).
     If either check fails, stop and return PACKAGES.
2. **The engineer** (fresh, `gov launch`, sandboxed, `--effort high`) regenerates `.claude/skills/adopt/SKILL.md` with rulesync from `.rulesync/skills/adopt/SKILL.md`, and changes nothing else (DEC-814).
   - If rulesync would change any other generated file, the engineer names it, commits only the one file, and you return the others as PACKAGES.
   - If the guard refuses the write, return PACKAGES.
   - Its commit carries `Task: DAEO-siiz`, `Role: engineer` and `Implements: DEC-814`.
3. **Verification: in full,** in the close's form (LEAD-w2-common), plus `pytest --collect-only -q` over `tests` (DEC-868).
   - Rebuild from this worktree's code (check `gov.__file__` first), under the machine's rebuild lock. Name every entry or record the load lists as `invalid`; `invalid: []` is expected.
   - The merged code has never run as one: W2-49's Contract v4.2, your gates, and 730 commits of `w2/integrate`. Look hardest at:
     - `tests/acceptance/W2-52/`, `tests/acceptance/W2-49/` and `tests/unit/adopt/`;
     - the adopt suites (W1-39, W1-41) and W1-26;
     - `gov check`: **adapter-portability must be green.** Name every other check that is not green, with its cause.
   - **The nightly:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite. Between 00:30 and 05:30, start no worker and no suite run (DEC-942 item 5). From about 01:00, start no full verification run that cannot finish before 02:00. A close queue may be running in the main tree: run your suites only when the 1-minute load is under 20.
   - **Known:** W1-42's accepted reds; the load-sensitive cases, re-run alone. Any other red is named with its cause.
4. **Repair: at most one batch.**
   - A red in this ticket's code: a fresh engineer (`gov launch`, sandboxed, `--effort high`), in the ticket's allowed paths only.
   - A red in `tests/acceptance/**`: a fresh independent test designer (DEC-906), each change with a `Rewrite-Reason:` and no expectation lowered.
   - A red in W2-49's files (`docs/contract/**`, `docs/changes/W2-49-*`, `tests/acceptance/W2-49/`) is not yours to repair: return PACKAGES.
   - Then the red cases and their suites again; a second full run only if code changed.
5. **A fresh FULL reviewer** (brief A3 with `governance/project/briefs/JUDGEMENT.md` word for word, `--effort max`, read-only) on the final head.
   - Launch it sandboxed. If its A3 probes cannot write the code graph's `/tmp/gov-cbm-<uid>` there, use the old form with read-only tools, as in run 2b (DEC-799), and say so in the return.
   - **Why:** DEC-814 and DEC-802 place a fresh probe in this resume. The first probe, at `643aeeef`, judged the gates before W2-02's verdict closed and before the generated skill existed.
   - **Its scope:** the whole ticket at that head, above all:
     - the regenerated `.claude/skills/adopt/SKILL.md` against its rulesync source;
     - the lite A7 and A10 gates and their stage records against the verdict as it now stands on `w2/integrate`;
     - a missing or failing record, never healthy (DEC-795, DEC-796).
   - F-1 and F-3 are rows (DEC-810), not findings of this probe. Every finding carries the two lines (DEC-808 item 4).
   - **Commit a probe record** `docs/probes/DAEO-siiz/PR-DAEO-siiz-run3.md` only if it passes. Its `probed_commit` is the final head. The first record stays as it is.
   - **Before the reviewer starts,** check `git rev-parse --short=12 w2/W2-49`. If W2-49's merge-back has moved it past `19d452461125` with a change to `docs/contract/**`, `docs/changes/**` or `tests/acceptance/W2-49/**`, merge `w2/W2-49` in step 1's form, and run W2-49's and W2-52's suites again first.
6. **Checkpoint and trailers:** `gov checkpoint` at the end (DEC-511). Run `trailer_gate.py` on your worktree before you return (LEAD-w2-common, DEC-927 item 2).
7. **Return** DONE (the probe passed; ready to merge into `w2/integrate` after W2-49's close), or PACKAGES. Carry run 2's residuals in the return as they stand, add any new one, and name the temporary folders left by earlier runs (`/tmp/tmp.5Zrjbt9w4E`, `/tmp/w2-52-probe-NPHQxG`) with their size, for the orchestrator.

**The park rule (DEC-941 item 2):** if the repair grows beyond this one run, stop and return PACKAGES naming the cost. That means any of:
- a second repair batch;
- a probe that fails on a finding an honest agent can hit in ordinary work that fails open or loses work;
- a red in W2-49's files;
- a change needed in a path another lead holds or outside the ticket's paths.

Name what is left, its size in lines and hours, and what waits on it (W2-27, which depends on W2-52; EXAMIN's copy).

**Running beside you:**
- W2-03's lead holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`.
- W2-05's lead holds:
  - the git-environment lines across `src/gov/**/*.py`, among them `src/gov/adopt/project.py`;
  - `src/gov/util/gitenv.py` and the lefthook files;
  - DEC-805's `src/gov/adapters/portability.py` and the `matcher` line in `template/.rulesync/hooks.jsonc`.
- W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
- W2-61 holds `src/gov/retrieval/measure.py`.
- W2-60a holds `src/gov/launch/launcher.py`, `role.py` and `record.py`.
- W2-77 holds `src/gov/close/nightly.py`.

Do not touch them. If a fix needs a change there, return PACKAGES.

**Estimate:** about 5 hours:
- the merge and the rebuild, about 30 minutes;
- the engineer's one file, about 20 minutes;
- one full run, about 95 minutes (the last two nightly runs took 5,623 s and 5,707 s);
- the FULL probe, about 2 hours.

With one repair batch, up to 7 hours.

---
