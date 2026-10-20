# Brief: engineer — DAEO-kl5e (W2-50), FULL: the change-execution record (CIT-E)

You are a fresh engineer. Ticket: DAEO-kl5e (W2-50, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`. The change is implemented and verified green. Your one task: write and commit `docs/changes/W2-50-CIT-E.md`, the change-execution record (CAP-33): what was done, file by file, against the approved proposal `docs/changes/W2-50-CIT-P.md`, matching it or listing each difference. You change no code and no test.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kl5e`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-50` and `w2/W2-50`). If anything differs, stop and say so.
- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-50/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Run no glob, no search and no listing over `governance/project/`. Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nothing under `~/.claude/` is read. Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path. Never read or name the qualification oracle.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never create, write, list or remove anything in the real `~/gov-os-runs/` (it does not exist; nobody creates it in this run) or the real `~/gov-os-worktrees/`. If you run a test, run no `local_only` live-launch case (they would create the real root).
- Never copy the repository or a folder of it anywhere. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**`. Never run `gov rebuild --no-embeddings`, `gov close`, `gov adopt` or `gov pause`. Do not run `docs/plan/tools/validate_s1.py` (DEC-738 item 2).
- Refused twice for the same call: stop and say so; no third try (AR-6).
- If the guard refuses something you need, do not work around it: return it as a package. On an authentication or access error (401, 403, "Failed to authenticate", "access grant"), stop and return status AUTH_REQUIRED.

## What you read

- The ticket file `.tickets/DAEO-kl5e.md` (read-only).
- The approved proposal `docs/changes/W2-50-CIT-P.md`, in full, with the owner's answers (DEC-743) in its closing section.
- What was done: `git log --format='%h %s%n%b' 689bd17e..HEAD` and `git show 91200c82` (the implementation), `git show 887c288c --stat` (the tests for the owner's answers); the code at HEAD in `src/gov/guard/runs.py`, `src/gov/guard/decide.py`, `src/gov/launch/launcher.py`, `src/gov/secrets/__init__.py`; the acceptance README `tests/acceptance/W2-50/README.md`.
- The form: `docs/changes/S2-CIT-E.md` (a change-execution record: frontmatter and sections) and the schema `template/governance/kernel/schemas/change-execution-record.schema.json`; your frontmatter must be valid against it (`proposal: W2-50-CIT-P`; `state_class` as the schema and S2-CIT-E use).

## The facts the lead gives you (the verification, as the lead ran it at `91200c82`, with this worktree's `src/`)

- One full `gov rebuild --json`: ok; lexical, semantic and codeintel recreated.
- `tests/acceptance/W2-50`: 154 passed. Builder tests `tests/unit`: 2113 passed, 1 skipped.
- Every other acceptance suite W1-01 to W1-50: green, except W1-42's two known reds (RETR-X-02, "no named parent expansion"; the governance share per programme), named exceptions at Wave 1's close (DEC-713, DEC-714), not this ticket's.
- W1-46 and W1-50 ran with `-m "not local_only"`: 36 live-session cases of `tests/acceptance/W1-46/test_w1_46_live_sessions.py` and two of W1-50 (`test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path`, `test_a_flag_put_over_the_placeholder_during_a_command_stays`) were not run: they launch real sessions through `gov launch` with the real HOME, which from this change on makes the real `~/gov-os-runs/<fixture W2 id>/`, and nobody creates it in this run.
- `docs/plan/tools/validate_s1.py`: not run (DEC-738 item 2).
- The list row W2-M355 ("Live clones under /tmp lost on reboot"): taken in by this change (the own folder survives the session's end; R6).

## What you write

`docs/changes/W2-50-CIT-E.md`, with `status: APPLIED`, and these parts:

1. What was applied, against which proposal and decision (DEC-728, DEC-743), with the commits (`a5ef3c69` the CIT-P, `887c288c` the tests for the owner's answers, `91200c82` the implementation).
2. Each change of the CIT-P's §3 ((a) to (d)), file by file: what was done, and whether it matches the proposal and the owner's answers. Every difference is listed with its reason. Find them by reading the code against the proposal yourself; among the points to check: whether the check's file `secrets-indexing.yaml` changed at all (§3(d), §6.1 (i)); what the launcher does when the own folder cannot be named or made (the proposal does not say); how a clone adopted under the root runs its own secrets check; how R7 (scoped to the root), R8, §6.4 and §6.5 were built.
3. The verification (the facts above), and the cases that were not run, with why.
4. The lines added and removed against the estimate of 120 (`git show --shortstat 91200c82`; code and builder tests apart).
5. What stays open, by row or ticket: W2-H055 (`git clone` destinations, W2-09), W2-M359 (Write and Edit in a launched session, W2-21), W2-L342 (CAP-58's text, Wave 3), the live `local_only` launch cases and the real root, and any difference of item 2 that leaves something open.

Describe behaviour; quote no more code than a name.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. Commit only that one file, with the trailers in the final block:

    git add docs/changes/W2-50-CIT-E.md
    git commit -m "W2-50 (DAEO-kl5e): the change-execution record (CIT-E)" --trailer "Task: DAEO-kl5e" --trailer "Role: engineer" --trailer "Implements: DEC-728" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

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

In those fields give: the commit hash and trailers; each difference from the CIT-P you recorded; the schema check you made of the frontmatter; the `gov.__file__` line. Refused twice for the same call: stop and say so.
