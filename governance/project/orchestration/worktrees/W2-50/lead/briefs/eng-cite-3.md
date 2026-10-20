# Brief: engineer (the record only) — DAEO-kl5e (W2-50), FULL: the CIT-E's §11 for the DEC-774/DEC-778 round

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`, at head `1c80aa97`. The repair of this round is committed and green; the engineer who made it ran out of time before writing the record. **Your one job: add §11 to `docs/changes/W2-50-CIT-E.md` and commit it.** You change no code and no test. Keep the session short: run no acceptance suite (the lead has run them; the results are below).

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`), and `git log --oneline -1` (expect `1c80aa97`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- The guard's hook in your session runs this worktree's `src/` (DEC-751 item 6): the code of this round confines you.
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase.
- Run no glob, no search and no listing over `governance/project/`. Never read `.claude/settings.json` or `.claude/settings.local.json`. Nothing under `~/.claude/` is read. Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525); the record names it only as "the held-out file". Never read or name the qualification oracle.
- Never write in `~/gov-os-workbench`, and never list, glob or search it (DEC-723). Never create, write, list or remove anything in the real `~/gov-os-runs/`, `~/gov-os-worktrees/` (other than this worktree) or `~/gov-os-workbench/`. Before you return, run `test -e ~/gov-os-runs && echo PRESENT || echo ABSENT` and quote the output.
- Never copy the repository or a folder of it. No subagents that write. Install nothing. No push, merge or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2). Never write under `src/gov/close/**` or `tests/unit/close/**`.
- Refused twice for the same call: stop and say so; no third try (AR-6). On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## The owner's DEC-774 and DEC-778 (2026-10-18; staged for the owner's commit, not in this worktree's register)

- **DEC-774, finding D:** `cp -b` (`--backup`), `install`, `mv` and `cp --remove-destination` onto a symbolic link replace the link with a new file at the link's own path, while the guard judged the link's target. **The guard refuses as doubt a write that replaces a link rather than following it** (the four forms and any other form of `cp`, `install` or `mv` whose write replaces the link at its own path). Ordinary writes through a link to an allowed target, and every copy, install and move run 6 allows into allowed folders, still pass. **The change record is corrected:** a new section states what holds after this round and corrects §10's overclaim; §10 is not rewritten in place.
- **DEC-778, one option reader:** the guard's read rule for the protected pair (the settings file and the held-out file) read `mv` and `cp -l` with the old option reader (a `t` inside an option's value read as `-t`; `--` ignored). It now uses the reader the write rule uses (DEC-765), so the guard reads every copy-like command one way, for writes and for reads. The ticket's `allowed_paths` gained `src/gov/guard/protected.py` and `tests/unit/guard/test_protected*` (`b4172c59`).

## What you read

- `docs/changes/W2-50-CIT-E.md` in full, §10 in particular, and its frontmatter against `template/governance/kernel/schemas/change-execution-record.schema.json`.
- The change: `git show 1c80aa97` (`src/gov/guard/decide.py`, `src/gov/guard/protected.py`, `tests/unit/guard/test_runs.py`, `tests/unit/guard/test_protected_one_reader.py`).
- The tests of the round and their README sections: `tests/acceptance/W2-50/test_w2_50_link_replaced.py` (D), `tests/acceptance/W2-50/test_w2_50_one_reader.py` (DEC-778), and `tests/acceptance/W2-50/README.md` (what each form does to a link, as the test designer saw it on coreutils 9.4).

## The facts of the round (from the lead)

- Commits: `2956f9e7` (independent-test-designer: 88 cases for D; 58 red at `2d60cdd3`, all "not refused: decision=allow"); `b4172c59` (orchestrator: the ticket's paths widened, DEC-778); `397a80de` (independent-test-designer: 167 cases for DEC-778; red at `b4172c59` plus that file: 104 failed, 509 passed — the 58 D cases, 38 second names of the stand-in protected file allowed for the orchestrator, 8 refused for the engineer by the write rule instead of as reads); `1c80aa97` (engineer: the repair, `decide.py` +32/−34, `protected.py` +16/−6, builder tests +122; 170 added, 40 removed in all).
- After the repair, run by the lead in this worktree with this worktree's `src/`: `tests/acceptance/W2-50` **613 passed**; `tests/unit` **2267 passed, 1 skipped**. The lead's full verification (every suite, the rebuild) follows your commit; write "the lead's full verification follows this record" rather than inventing results for other suites.

## What you write

Add a new section **§11** at the end of `docs/changes/W2-50-CIT-E.md`: "11. The last round, after the review of §10's round (DEC-774, DEC-778)", with:
- what the owner decided (DEC-774, DEC-778), in a few lines;
- **the correction of §10**, stated as a correction: what §10 claimed about backups, the copy forms and W2-H056, and what did not hold at `2d60cdd3` (a link destination replaced by `cp -b`/`--backup`/`-S`, `install`, `mv`, `cp --remove-destination`, while the guard judged the link's target); and that §10 did not name that the read rule for the protected pair still used the older option reader for `mv` and `cp -l`;
- **what holds after this round**, read from the code and the tests: which `cp`, `install` and `mv` forms onto a link are refused as doubt (and why `cp -f` is among them), which writes through a link still pass, how a link moved away is judged, how the read rule now reads `mv` and `cp -l` (the same reader as the write rule; what it does when the options cannot be read); each claim held by a named acceptance or builder test, or marked "not tested";
- **what stays open**: W2-L354 and W2-L350 (unchanged), and any form you can see the code still does not read (say so plainly; do not test it yourself beyond reading);
- what the repair changed, file by file; the commits of the round with their roles; the lines added and removed (estimate for the ticket: 120);
- the verification figures above.
Do not rewrite §10 or any earlier section in place. Bring the frontmatter up to date (add DEC-774 and DEC-778 to `decisions_carried` if that is how earlier rounds were recorded) and keep it valid against the schema (check with a short Python `jsonschema` or `yaml` load if the tools are installed; if not, say so). Say only what holds.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. One commit, only `docs/changes/W2-50-CIT-E.md`, with the trailers in the final block:

    git commit -m "W2-50 (DAEO-kl5e): the CIT-E's §11 for the DEC-774/DEC-778 round, correcting §10's claims" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B`, `git show --stat HEAD` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

In those fields give: your commit's hash and trailers; a summary of §11's claims (what holds, the correction, what stays open); anything in the code you judged not to hold what DEC-774 or DEC-778 asks, as a finding for the lead; the `gov.__file__` line; the `~/gov-os-runs` ABSENT line. Refused twice for the same call: stop and say so.
