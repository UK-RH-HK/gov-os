# Brief: product-spec, DAEO-uw5h (W2-100), batch 2 — the scenario summaries, and the records and summaries copied

You are a fresh product-spec worker. Ticket: `DAEO-uw5h` (W2-100), profile STANDARD, class C2. You work only in the
ticket's worktree `/home/usain/gov-os-worktrees/W2-100` on branch `w2/W2-100`. The four domain skills (backend, api,
data, security) are written and committed. The lead has run each skill's three scenarios through the real
`gov skilleval`; each run appended entries to `scenario-records.yaml` in the skill's folder (untracked files now). You
write each skill's hand-written `scenario-summaries.md` beside its record (S4, the ticket's `## Interface`), copy both
files to the skill's two `.rulesync` folders, and commit.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uw5h','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-uw5h`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-100` and `w2/W2-100`),
  `git rev-parse --short=12 HEAD` (expect `fef53fb21...`), and `git status --short` (expect exactly the four untracked
  `template/governance/kernel/skills/{backend,api,data,security}/scenario-records.yaml`). Anything else: stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- **Your paths for this batch:** in each of the four skill folders `template/governance/kernel/skills/<skill>/`:
  `scenario-records.yaml` (commit it exactly as the lead's runs wrote it: never edit, reorder or reformat it) and
  `scenario-summaries.md` (new); and the same two files, byte-equal, in `.rulesync/skills/<skill>/` and
  `template/.rulesync/skills/<skill>/`. Nothing else: not SKILL.md, not scenarios.md, not the check script, not
  `tests/`, not `src/`, never `.claude/`.
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

- Each skill's `scenario-records.yaml` (the entries: `scenario`, `title`, `verdict`, `cause`, `run_at`, ...).
- The lead's index of the captured replies, read-only:
  `/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval/transcripts-index.md`. For each record
  entry, in record order, it gives a heading `### Scenario <n>: <title> | verdict <v> | run_at <run_at>` and either the
  session's full reply and the judge's last lines, or `(reply not kept: run 1, before the capture)`.
  Facts behind it: the `gov skilleval --json` envelope carries no reply text (by design, so no secret can reach a
  record); the lead captured each reply from run 2 on with a pass-through `claude` on `PATH`, so run 1's replies
  (all entries with `run_at` before 01:35 UTC) were not kept. In run 1, api's scenario 2 was judged FAIL; it passed in
  the later run. Security's scenario 2 Situation was reworded after run 3 (commit `fef53fb21`: it now names the
  security finding); its run 4 entries (01:45-01:48 UTC) ran the reworded text.
- `template/governance/kernel/skills/<skill>/scenarios.md` for each scenario's Situation, Expected and Pass line.

## The form (the ticket's interface, word for word)

`scenario-summaries.md` holds one entry per recorded run, that is one entry for every entry of `scenario-records.yaml`,
in the record's order, under a first line `# <skill>: scenario summaries` and one short paragraph saying where the
replies came from (the facts above, in a sentence or two). Each entry:

    ## Scenario <n>: <title>
    - verdict: <pass|fail|not-run>
    - run_at: <the record entry's run_at, exactly as the record holds it>
    - summary:
      <line 1 of a three-line summary of the session's reply>
      <line 2>
      <line 3>

- `<title>` is the record entry's `title`, exactly; `verdict` and `run_at` are the entry's, exactly.
- The summary is exactly three non-empty lines, each indented two spaces, each one sentence, and nothing else follows
  them before the next `##` heading. For an entry with a kept reply: what the session did and concluded, as the
  reply shows it, ending with how it meets (or misses) the pass line; quote no secret-like value (there is none; keep
  it that way). For a run 1 entry: three lines saying that the reply was not kept (run 1 came before the capture), what
  the judgement recorded (for a fail, its `cause`), and that a later entry of the same scenario holds a kept reply;
  for security scenario 2's run 1 and run 3 entries, say in one of the three lines that they ran the earlier wording.

## Steps

1. Write the four `scenario-summaries.md` files.
2. Copy `scenario-records.yaml` and `scenario-summaries.md` of each skill to `.rulesync/skills/<skill>/` and
   `template/.rulesync/skills/<skill>/`.
3. Checks, each quoted in your return:
   - for each skill, the number of `## Scenario` entries equals the number of record entries (backend 6, api 6,
     data 6, security 9), and a short script of yours in `$TMPDIR` shows each entry's (scenario, title, verdict,
     run_at) equal to the record entry at the same position and each summary three lines;
   - `diff -r` of each skill folder against each of its two `.rulesync` copies: empty;
   - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.adapters.portability` (in the worktree): no
     `SOURCE_DIFFERS`, `SOURCE_MISSING` or `SOURCE_WITHOUT_KERNEL`; the `GENERATED_DIFFERS` findings for the four
     skills' `.claude/skills/` copies are expected (the copies ACT): name them;
   - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.check.skill_validator template/governance/kernel/skills/backend template/governance/kernel/skills/api template/governance/kernel/skills/data template/governance/kernel/skills/security`: exit 0.
4. Commit (check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if one
   is, stop and return; never `--no-verify`), every trailer in the one final block, the 24 files named:

    git commit -m "W2-100 (DAEO-uw5h): the scenario records of the lead's real gov skilleval runs and their summaries, with the .rulesync copies (DEC-959 item 5)" --trailer "Task: DAEO-uw5h" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-616, DEC-645" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <the 24 paths>

   Then `git log --oneline -2` and `git status --short` (expect nothing).

## Return

Your last message, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing): the
sandbox check first in `evidence`; the commit's 12-digit hash and trailers; the checks' output; the read refusals you
met; your scratch figures (`du -s --inodes` and `du -sh` of your `$TMPDIR`).

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
