# W2-148 — the engineer's brief, round 2: the review's two blocking findings and the cheap rows (DAEO-xafn)

You are a fresh engineer for **W2-148** (`.tickets/DAEO-xafn.md`: read it in full; and
`governance/project/orchestration/packages/OPERATOR-AGENT-1.md` §1 to §6). Round 1 (head `45dd9e2dc` on `w2/W2-148`)
built the operator agent in `governance/project/operator/`; `gov accept W2-148` passes **157/157** (the CTO's run
outside the sandbox) and the unit tests 108/108. The independent review (round 1 of at most two) found it **not READY**:
two findings block (in scope, ordinary work, fail open). Its findings are in your worktree at
`.gov-runtime/scratch/ref/review-r1-findings.md` (F1 to F14, with file and line): read them first.

## Your job
1. **F1 (S6, blocking): the script scan misses commands after shell reserved words.** In `act_class.py`'s `segments`
   and `strip_wrappers`, step over `if`, `then`, `else`, `elif`, `fi`, `do`, `done`, `while`, `until`, `for … in …`,
   `case`/`esac`, `{`, `}`, `(`, `)` and `!` the way `env` and `nohup` are stepped over, so `then sudo …`,
   `do git push`, `{ git tag v1; }`, `then rm -rf ~/x`, `do curl https://…`, `then pip install …`, `! git push` and
   `else git push` all give their hit. Unit cases for each of these, and for a hit inside a function body and a
   heredoc-fed `bash`.
2. **F2 (S12, blocking): the dry run must never touch the live tree.** Two layers:
   - **refuse before running** (at G1 or before G8): an `apply.sh`, a manifest command or a check that names the live
     repository's path or the real HOME literally (absolute, `~`, `$HOME`, `${HOME}`), or `cd`s to either, is refused
     with a reason naming the path rule; the frozen script must work relative to its cwd and HOME;
   - **detect after the dry run:** re-hash the live touched files and the control files (§3's list) after G8; on any
     change, refuse, restore the live files from the frozen `before/` copies, record it in the log and push a P1 that
     says live files changed.
   - Add the path rule to `reviewer-brief.md`'s first check, and to `brief.md` if the session needs it.
   - Your trial's bundles must still pass (re-run S23; replays relative).
3. **The cheap rows, in the same round (each in scope; drop one and name it if it turns an acceptance case red):**
   - **F14:** an empty touched list with any command is at least (b), never (a).
   - **F8:** G1 never removes or replaces an existing `acts/<id>-<sha12>/`: a second request for the same sha reuses
     the frozen copy only if it hashes as the manifest says, otherwise refuses ("changed after review") and leaves the
     existing copy (an applied ACT's undo) untouched.
   - **F9:** the manifest's `author` is required (G1 or G4 refuses without it).
   - **F10:** an unexpected exception after G7 is pushed as a P1 and counted by the digest's `missing_notices`.
   - **F11:** `.git/config` (and `core.hooksPath` wherever it points) joins the control snapshot and the dry run's
     changed set.
   - **F12:** the nightly hold also reads the `NIGHTLY-RUNNING` flag the nightly writes (find it in
     `governance/project/orchestration/nightly/` and `tools/`; a settings key with that default), beside the window.
   - **F13:** `owner_text` excludes `isCompactSummary` lines (and any line with `isMeta`, already).
   - **F6:** the wall's settings `env` sets `BASH_DEFAULT_TIMEOUT_MS` and `BASH_MAX_TIMEOUT_MS` sized to the session's
     timeout, and the brief tells the session to run `operator_run.py` with that timeout.
   - **F4:** the default notice no longer goes through `deadman.py --test` (a "TEST DEADMAN" label, cut at 190
     characters). Send through the same three channels `deadman.py`'s `send()` uses (`pings.log`, the toast, the
     headless `claude -p` PushNotification), from the install's own code (standalone: copy the forms, never import the
     repository), with a notice line built to fit 190 characters (priority and ACT first, then the gate or result, then
     the undo line), no "TEST" label; `push_cmd` stays the setting that overrides it, and the tests' stub still works.
4. **Not in this round (the CTO's or the owner's; leave as is):** F3 (the replay's call source), F5 (the freeze's
   final place and the CTO's hand-over rule), F7 (removing `apply.sh apply|undo` and `git add`/`commit` from the
   session's allowed forms: a change to the approved package, an owner question under DEC-105).
5. Update your unit tests and `docs/changes/W2-148-evidence.md` (a "Round 2" section: each fix, its test, the trial
   re-run's counts).

## Where you work
- `/home/usain/gov-os-worktrees/W2-148`, branch `w2/W2-148`. Your paths are the ticket's `allowed_paths`:
  `governance/project/operator/**`, `tests/unit/operator/test_w2_148*`, `docs/changes/W2-148-evidence.md`.
- **You never read `tests/acceptance/W2-148/`** (G-14; DEC-820 (c)): only `gov accept`'s results. **The exclusion line
  (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=W2-148`; every Grep or Glob call that
  could reach the folder carries `!tests/acceptance/W2-148/**`; find carries `-path '*/W2-148' -prune`. Start your
  searches from relative paths inside your worktree (`.`, `governance/`, `src/`), never from its absolute path. If a
  search shows you a line of the cases anyway, stop reading it and say so in your return.
- The interface the cases call is unchanged: the round-1 brief's copy of it is in your worktree at
  `.gov-runtime/scratch/brief/W2-148-engineer.md` (from "# The interface the acceptance cases assume").

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-148/src` and HOME an empty scratch folder: your unit tests; the
  trial; then `python3 -m gov.cli.main accept W2-148 --root /home/usain/gov-os-worktrees/W2-148` (counts per line,
  results only; all 157 must stay green). Name every red with its cause.
- **Commit as you go**, each fix as it passes.

## Rules
- **Nothing live:** you never write `~/gov-os-operator/`, `~/.claude/`, the crontab, the live hook, settings or git
  hooks, and never start a real `claude` session or send a real notice (stubs in your tests).
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no network, no installs, no service.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Search again once
  (DEC-1092 (1)) if needed. Waits and stops by pid or pgid only.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-148` with
  `--trailer "Task: DAEO-xafn" --trailer "Implements: DEC-1104" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it; it is the record): the twelve
labelled fields of `EMG-common.md` (sandbox and `ps` checks first), each finding fixed (commit, unit case) or dropped
(why), `gov accept W2-148`'s counts per line, the unit counts, the trial re-run's counts, every red named.
