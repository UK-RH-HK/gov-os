# W2-148 — the engineer's brief, round 3: the owner's exception round, F15 and the freeze (DAEO-xafn)

You are a fresh engineer for **W2-148** (`.tickets/DAEO-xafn.md`: read it in full, with its note on DEC-1106 and its
fifteenth failure line; and `governance/project/orchestration/packages/OPERATOR-AGENT-1.md` §1 to §6). Rounds 1 and 2
built the operator agent in `governance/project/operator/` (round 2's head `85a5cf655`: `gov accept` 157/157, unit
153/153). The second and last review found one blocking defect, **F15**, and the owner decided it as **DEC-1106**, one
exception round to DEC-1010 (its text: `.gov-runtime/scratch/ref/DEC-1106.md` in your worktree; the review's finding:
`.gov-runtime/scratch/ref/review-r2-F15.md`). This is that round: **one pass**, then one narrow review.

**F15 in short:** round 2's live re-hash around G8, and the (a) after-check's undo, restore *every* live difference to
its earlier bytes and delete files created meanwhile. They cannot tell the dry run's or the ACT's change from someone
else's: a CTO commit or merge landing in the live tree during the dry run or the apply is reverted, a guard tightening
merged in that window silently stops applying, and the P1 blames the dry run.

## Your job
1. **The restore rule (DEC-1106 (1)),** at both sites (`Run.live_changed` after G8, and the after-check's undo through
   `restore_controls` / `undo_live`): restore only a file you can show is your own change (a touched file whose live
   bytes equal the frozen `after/` copy); for anything else write nothing, refuse, hold the lock, and send a P1 naming
   each file. The ACT's own touched files are still undone in the (a) undo. Exactly as the interface below states it.
2. **The two new test-hook points** `in-G8` and `in-apply-checks`, as the interface states (the run waits for the
   hook, ignores its exit code, holds no `.git/index.lock` on the live repository while it runs).
3. **The commit freeze (DEC-1106 (3))** at `<operator root>/install/act-in-progress.txt`, the `freeze` setting's
   default; never in either `log/`; not counted by the APPROVED check nor by the install's control-file hash; a stale
   one holds G9 and is never removed by a run that did not write it. The CTO's tools, the landing hook and the guard's
   deny for it come with ACT-OPERATOR-1, not here.
4. **Not in this round:** F3 (the guard's call log: its own ACT, DEC-1106 (2)); F7 (kept, DEC-1106 (4)); the rows F16
   to F20, unless one is a line or two and touches the same code (then say so).
5. Update your unit tests (unit cases for each rule: own change restored, foreign change left, both at once, the (a)
   undo with a concurrent control change, the stale freeze), re-run the trial (S23), and add a "Round 3 (DEC-1106)"
   section to `docs/changes/W2-148-evidence.md`; fix its defaults table (F19: `push_cmd` unset means the three
   channels; `freeze` the install folder).

## Where you work
- `/home/usain/gov-os-worktrees/W2-148`, branch `w2/W2-148` (the designer's DEC-1106 cases merged in at `5053a0407`:
  166 cases, 39 lines). Your paths are the ticket's `allowed_paths`: `governance/project/operator/**`,
  `tests/unit/operator/test_w2_148*`, `docs/changes/W2-148-evidence.md`.
- **You never read `tests/acceptance/W2-148/`** (G-14; DEC-820 (c)): only `gov accept`'s results. **The exclusion line
  (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=W2-148`; every Grep or Glob call that
  could reach the folder carries `!tests/acceptance/W2-148/**`; find carries `-path '*/W2-148' -prune`. Start searches
  from relative paths inside your worktree, never from its absolute path. If a search shows you a line of the cases
  anyway, stop reading it and say so.
- The rest of the interface is unchanged: the round-1 brief's copy is at `.gov-runtime/scratch/brief/W2-148-engineer.md`.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148/src` and a scratch HOME (link `.local/lib` to the user site, as
  you did before): your unit tests; the trial; then
  `python3 -m gov.cli.main accept W2-148 --root /home/usain/gov-os-worktrees/W2-148` (counts per line; all 166 must be
  green). Name every red with its cause. Commit as you go.

## Rules
- **Nothing live:** never write `~/gov-os-operator/`, `~/.claude/`, the crontab, the live hook, settings or git hooks;
  no real `claude` session, no real notice.
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, model, network, installs or service.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Waits and stops by pid or
  pgid only. Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-148` with
  `--trailer "Task: DAEO-xafn" --trailer "Implements: DEC-1106" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it; it is the record): the twelve
labelled fields of `EMG-common.md` (sandbox and `ps` checks first), each change (commit, unit case), `gov accept
W2-148`'s counts per line, the unit counts, the trial re-run's counts, every red named, and any place where the
interface and a KPI line or DEC-1106 disagree (DEC-1106 and the KPI lines win: say so, with the case's message).

---

# The interface lines the designer changed for DEC-1106 (its README, as written)


> **`install/APPROVED`:** one line per install file, `<sha256>  <path relative to install/>` (sha256sum's form), every file under `install/` but `APPROVED` itself, `__pycache__/` and the commit freeze `act-in-progress.txt`. Any file not matching its line refuses every run and every launch. Every result prints `approved_sha256` (the sha256 of `install/APPROVED`).

> **The commit freeze (DEC-1106 (3)):** `<operator root>/install/act-in-progress.txt` (the default of the `freeze` setting; the tests leave the setting out). The run writes it before `apply.sh apply` and removes it at the end; it is never in either `log/` (the operator root's or the scratch's). The APPROVED check never counts it: a freeze present during the run never makes an APPROVED check fail, and a stale one left from an earlier run never makes a later run refuse on APPROVED; it holds G9 (a `G9` line with result `held`) until it is gone, and the run never removes a freeze it did not write. The install's control-file hash (S15, F15) leaves it out too. G9 still also holds on the CTO's `<scratch>/log/act-in-progress.txt`.

> Settings, added key: … `freeze` (the commit freeze's file; default `<operator_root>/install/act-in-progress.txt`, DEC-1106 (3)).

> - **Test hook:** `GOV_OPERATOR_TEST_HOOK=<executable>` is run as `<exe> <point> <frozen folder>` at the points `after-G1` (the copy made and hashed) and `after-G6` (G6 passed; the recompute comes next and classifies the frozen bytes as they are then). The walled session's clean environment never carries it.
>   DEC-1106 (1) adds two points, called the same way:
>   - `in-G8`: after the dry run's steps in the clone (`check`, `apply`, the checks, `undo`) and before the live re-hash that ends G8 (F15 below); the pre-dry-run hashes are already taken.
>   - `in-apply-checks`: for every class, after the live `apply.sh apply` and the manifest's checks have passed, and before the after-check (S15) begins; before or after the run's own commit is the engineer's.
>   At every point the run waits for the hook to exit before going on and ignores its exit code; it holds no git lock on the live repository (`.git/index.lock`) while the hook runs; the hook gets the run's own environment (HOME, PATH) and any cwd. The tests' hooks use absolute paths and their own git environment, write live files, and commit in the live repository with `git commit -- <paths>` (only those paths: anything the run has staged stays staged); a hook ignores every point but its own.

> … The commit freeze is `<operator root>/install/act-in-progress.txt`, never in either log (DEC-1106 (3), above); it must exist during the apply and be gone after.

> **The control files (S15), as planted:** the hook folder `.claude/hooks/**`, `.claude/settings*.json`, the rest of `.claude/**`, `<repo>/.git/hooks/**`, `crontab -l`, the pin `<home>/.local/bin/gov`, the dead-man's and the sentinel's code `governance/project/orchestration/tools/deadman.py` and `sentinel-brief.md`, and the install. After an (a) ACT changed one of them, the ACT's own touched files are undone and the control file is left exactly as it is (the agent cannot tell that change from someone else's), the lock held and a P1 naming it (DEC-1106 (1), the restore rule below).

> **The restore rule (F15, DEC-1106 (1)).** The agent never writes a live file it cannot show is its own change.
> - **After the G8 dry run** the agent re-hashes the live touched files and the control files above, with the path map `governance/project/path-map.yaml` among them, as the sets of files under each (a file created or removed under `.claude/**` is a difference), against the hashes it took before the dry run. A touched file whose live bytes equal the frozen `after/` copy is its own dry-run change: it restores that file to its pre-dry-run bytes, refuses (`gate` `G8`) and sends a P1 whose `text` holds the phrase `live files changed` and names the file. Any other difference (a control file, a file created or removed, a touched file whose bytes are neither its before- nor its after-copy) is left exactly as it is: nothing written, the run refused at `G8`, the lock held (the next queued ACT is not launched, S22's form), and a P1 whose `text` names each such file. Both at once: its own file restored, the rest left, the lock held, every other file named.
> - **In the (a) after-check's undo (S15):** a difference that is not the ACT's own (a control file the ACT does not list, or a touched file whose bytes are neither the ACT's after-copy nor its before-copy) is left exactly as it is, the lock held, a P1 whose `text` names each such file; the ACT's own touched files are undone as before; the result is `undone` or `refused`, never `applied`. A commit someone else made meanwhile stays in HEAD's history.
> - A P1 names a file by its path relative to its root (`crontab` for the crontab); an absolute path holding it counts. A launch while the lock is held changes none of those files.