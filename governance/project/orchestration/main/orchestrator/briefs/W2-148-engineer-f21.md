# W2-148 — the engineer's brief, the F21 round (DEC-1107) (DAEO-xafn)

You are a fresh engineer for **W2-148** (`.tickets/DAEO-xafn.md`: read it, with its DEC-1106 note and fifteenth
failure line). The operator agent (`governance/project/operator/`) is merged into `w2/integrate` (`511a4a17`):
`gov accept W2-148` 166/166, the narrow DEC-1106 review READY. That review left one row, **F21**, which the owner chose
to fix now: **DEC-1107** (its text in your worktree at `.gov-runtime/scratch/ref/DEC-1107.md`; the finding at
`.gov-runtime/scratch/ref/review-r3-F21.md`). **One tiny pass, for that point only.**

## The point
**The owner-undo path** (`operator_run.py --config C undo <ACT> <sha>`, on the owner's `undo ACT-<id> <sha8>` line)
**and the crash-recovery path** (the launcher's recovery of an unfinished journal) **must exit non-zero and say
`refused` whenever they leave another's file untouched**, with the P1 naming each file and the lock held as before
(DEC-1106 (1)); the ACT's own touched files (at their after-copy) are still undone. Today the owner's undo returns
`result: "undone"` with exit 0 when files are left (around `operator_run.py:1515-1528`), and the recovery returns
`undone` (exit 1, around `:1590-1593`).

The test designer's new cases (`gov accept` results only; you never read them) also show a second shape: **the owner's
undo, when one of the ACT's touched files has been changed by someone else to third bytes, today refuses up front
("moved since the apply") and undoes nothing.** Under DEC-1106 (1) it must undo the ACT's own touched files that are at
their after-copy, leave the third-bytes file exactly as written, and then (DEC-1107) say `refused`, exit non-zero, P1
naming the file, lock held. Do that through the same `undo_live` / `foreign_differences` rule the run path uses.

**Unchanged:** with nothing left, the owner's undo says `undone` with exit 0, and the recovery says `undone`. An undo
after the next ACT on the same files stays a plain refusal (the package's "undo stays ready until the next ACT on the
same files"). Nothing else changes.

## The interface line the designer changed (its README, as written)
> Exit 0 when applied, undone (the undo step) or launched; non-zero on a refusal. **The undo step and the recovery
> leaving a file (DEC-1107):** the undo step (`... undo <ACT> <sha>`, on the owner's line) and the launcher's recovery
> of an unfinished journal print `result` `refused` and exit non-zero whenever they leave any file untouched that is
> not the ACT's own (a touched file whose bytes are neither its before- nor its after-copy); then no JSON object on the
> launcher's stdout, nested ones included, carries `result` `undone`; the ACT's own touched files (at their
> after-copy) are still undone, a P1 names each file left, and the lock is held. With nothing left, the undo step says
> `undone` with exit 0 and the recovery's result (on the launcher's stdout, at any nesting) is `undone`.

## Where you work
- `/home/usain/gov-os-worktrees/W2-148-f21`, branch `w2/W2-148-f21` (from `w2/integrate` at `b134a760b`, the
  designer's cases merged at `68af526af`). Your paths are the ticket's `allowed_paths`:
  `governance/project/operator/**`, `tests/unit/operator/test_w2_148*`, `docs/changes/W2-148-evidence.md`.
- **You never read `tests/acceptance/W2-148/`** (G-14; DEC-820 (c)): only `gov accept`'s results. **The exclusion line
  (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=W2-148`; every Grep or Glob call that
  could reach the folder carries `!tests/acceptance/W2-148/**`; find carries `-path '*/W2-148' -prune`. Start searches
  from relative paths inside your worktree. If a search shows you a line of the cases anyway, stop and say so.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148-f21/src` and a scratch HOME (link `.local/lib` to the user
  site): your unit tests (add cases for both paths and both shapes); then
  `python3 -m gov.cli.main accept W2-148 --root /home/usain/gov-os-worktrees/W2-148-f21` (all 169 must be green; today
  167 pass, the 2 new reds). Add a short "F21 (DEC-1107)" section to `docs/changes/W2-148-evidence.md`. Commit as you go.

## Rules
- **Nothing live:** never write `~/gov-os-operator/`, `~/.claude/`, the crontab, the live hook, settings or git hooks;
  no real `claude` session, no real notice.
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, model, network, installs or service.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Waits and stops by pid or
  pgid only. Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-148-f21` with
  `--trailer "Task: DAEO-xafn" --trailer "Implements: DEC-1107" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it; it is the record): the twelve
labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the change (commit, unit cases), `gov accept
W2-148`'s counts per line, the unit counts, every red named.
