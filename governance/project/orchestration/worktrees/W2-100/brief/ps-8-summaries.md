# Brief: product-spec, DAEO-uw5h (W2-100), batch 4 — the summaries of runs 6 to 8 (clean runs), and the copies

You are a fresh product-spec worker. Ticket: `DAEO-uw5h` (W2-100), profile STANDARD, class C2. You work only in the
ticket's worktree `/home/usain/gov-os-worktrees/W2-100` on branch `w2/W2-100`. The four domain skills are committed:
backend and security at 1.0.1, api and data at 1.0.2 (commits `3318e42f6` and `05fcc8f2e`). The independent auditor
found that run 5's sessions had `scenario-summaries.md` in their skill folder (the harness copies every file but
`scenarios.md` and the record), so they could read earlier replies. The lead then ran clean runs, with every
`scenario-summaries.md` moved out of the skill folders for the run and put back unchanged after it: run 6 (03:17-03:21
UTC, all four at 1.0.1: backend and security 3/3, api scenario 2 and data scenario 2 judged FAIL); after the api and
data fix to 1.0.2, run 7 (api and data, 3/3 each) and run 8 (api and data, 3/3 each). Each run appended its entries to
the skill's `scenario-records.yaml` (modified, uncommitted). Each skill's `scenario-summaries.md` already holds one entry
per earlier record entry (through run 5). You add one entry per new record entry, copy both files to the skill's two
`.rulesync` folders, and commit.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uw5h','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-uw5h`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-100` and `w2/W2-100`),
  `git rev-parse --short=12 HEAD` (expect `05fcc8f2e...`), and `git status --short` (expect exactly the four modified
  `template/governance/kernel/skills/{backend,api,data,security}/scenario-records.yaml`). Anything else: stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- **Your paths for this batch:** in each of the four skill folders `template/governance/kernel/skills/<skill>/`:
  `scenario-records.yaml` (commit it exactly as the lead's runs wrote it: never edit, reorder or reformat it) and
  `scenario-summaries.md` (add entries; keep every existing entry byte for byte); and the same two files, byte-equal,
  in `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/`. Nothing else.
- **Never read `tests/acceptance/W2-100/`** in any tree or branch (DEC-820 (c)). Reads are open otherwise, except
  secrets and keys, the held-out material's contents and the hidden half of any evaluation set; never open an
  evaluation set's root or any hidden or memory-verdict folder.
- No `git checkout`, `reset`, `clean`, amend, rebase, merge, push, tag, stash or `worktree`. No model call (never run
  `gov skilleval` or `claude`).
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no backticks,
  no `bash -c '…'`, no long inline `python3 -c` with braces. Write with the Write and Edit tools at literal absolute
  paths; `cp` of a named file to a named literal path is fine. Anything longer than one line goes in a script file in
  your sandbox's `$TMPDIR`.
- Install nothing. No subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal (DEC-1142 (9)).
- Write commit hashes as 12 digits in your return.

## What you read

- Each skill's `scenario-records.yaml` and `scenario-summaries.md` (the existing entries show the form and voice).
- The lead's index of the captured replies, read-only:
  `/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval/transcripts-index.md`. For each record
  entry, in record order, a heading `### Scenario <n>: <title> | verdict <v> | run_at <run_at> | skill_version <v>`
  and the session's full reply and the judge's last lines (or "reply not kept" for run 1). The new entries are those
  with `run_at` from 03:17 UTC on: backend 3 and security 3 (run 6), api 9 and data 9 (runs 6, 7, 8). For the two run 6
  fails, the judge's full reply is in `/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval/fail-api-2-run6.md`
  and `fail-data-2-run6.md` beside it.

## The form (unchanged; the ticket's interface)

    ## Scenario <n>: <title>
    - verdict: <pass|fail|not-run>
    - run_at: <the record entry's run_at, exactly as the record holds it>
    - summary:
      <line 1 of a three-line summary of the session's reply>
      <line 2>
      <line 3>

`<title>`, `verdict` and `run_at` are the record entry's, exactly. The summary is exactly three non-empty lines, each
indented two spaces, each one sentence; nothing else follows them before the next `##` heading. For each new entry:
what the session did and concluded, as the reply shows it, ending with how it meets (or, for a fail, misses: the
judge's reason) the pass line; one of the three lines names the skill version it ran and that it was a clean run (no
summaries in the skill folder). Append the new entries after the existing ones, in record order. In the file's opening
paragraph add two sentences: that run 5's sessions had this file in their skill folder and could read earlier replies
(the independent auditor's finding F1), so its passes are not clean evidence; and that from run 6 on the file was moved
out of the skill folder for each run (clean runs). Change no other existing line.

## Steps

1. Add the twelve entries (three per skill).
2. Copy `scenario-records.yaml` and `scenario-summaries.md` of each skill to `.rulesync/skills/<skill>/` and
   `template/.rulesync/skills/<skill>/`.
3. Checks, each quoted in your return:
   - for each skill, the number of `## Scenario` entries equals the number of record entries (backend 12, api 18,
     data 18, security 15), and a short script of yours in `$TMPDIR` shows each entry's (scenario, title, verdict,
     run_at) equal to the record entry at the same position and each summary three lines;
   - `git diff` of each `scenario-summaries.md` shows only added lines (and at most the opening paragraph's two added sentences);
   - `diff -r` of each skill folder against each of its two `.rulesync` copies: empty;
   - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.adapters.portability` (in the worktree): no
     `SOURCE_DIFFERS`, `SOURCE_MISSING` or `SOURCE_WITHOUT_KERNEL`; the `GENERATED_DIFFERS` findings for the four
     skills' `.claude/skills/` copies are expected (the copies ACT): give their count.
4. Commit (check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if one
   is, stop and return; never `--no-verify`), every trailer in the one final block, the 24 files named:

    git commit -m "W2-100 (DAEO-uw5h): the clean runs 6 to 8's scenario records and their summaries, with the .rulesync copies (DEC-959 item 5)" --trailer "Task: DAEO-uw5h" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-616, DEC-645" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <the 24 paths>

   Then `git log --oneline -2` and `git status --short` (expect nothing).

## Return

Your last message, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing): the
sandbox check first in `evidence`; the commit's 12-digit hash and trailers; the checks' output; the read refusals you
met; your scratch figures (`du -s --inodes` and `du -sh` of your `$TMPDIR`).

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
