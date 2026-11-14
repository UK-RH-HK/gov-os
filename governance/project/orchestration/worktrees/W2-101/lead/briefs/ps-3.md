# Brief: product-spec, DAEO-6icv (W2-101), run 2, batch 3: the scenario summaries and the records

You are a fresh product-spec worker. Ticket: `DAEO-6icv` (W2-101), profile STANDARD: three kernel domain skills for
the engineer role (`frontend`, `ui-ux`, `devops`), written and committed on `w2/W2-101`. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-101` on branch `w2/W2-101`. The lead ran each skill's three scenarios on
the real model with `gov skilleval`; the harness wrote `scenario-records.yaml` in each skill folder (untracked). The
`--json` envelope carries no reply text, so the lead captured each process's reply with a pass-through wrapper on
`PATH` (the same run, unchanged). Your job: write each skill's `scenario-summaries.md` from those captures (the
ticket's `## Interface`, S4), and commit it with the records and the refreshed copies.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-6icv','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-6icv`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-101` and `w2/W2-101`).
  If anything differs, stop and say so.
- Foreground only, one command after another. No `git checkout` of another commit, no reset, clean, amend, rebase,
  merge, push or tag. Return only after your commit exists.
- **Reads (DEC-820):** open, except secrets and keys; the held-out qualification material's contents; **the
  counterpart's work: never read `tests/acceptance/W2-101/`** (nor `/home/usain/gov-os-worktrees/W2-101-tests`) by any
  tool; never open the evaluation sets' root or any hidden or memory-verdict folder. A scenario may hold an obviously
  fake planted key in its text; never copy any key-like string into a summary.
- **Search (DEC-1065):** no `gov retrieve` or `gov context` in the sandbox; Read and Grep tools, naming the folder.
- **Forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no backticks, no `bash -c`, no
  long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; scratch
  scripts under your session's own `$TMPDIR`. Keep the sandbox's `$TMPDIR`; never set it.
- **Refused twice for the same call: stop and say so** (DEC-1142 (9)); never work around a refusal; report it.
- Install nothing; no subagents that write; never ask or notify the owner; commit hashes as 12 digits (DEC-911). No
  model call; you do not run `gov skilleval`.
- **Never edit** a `scenario-records.yaml` (the harness's own record), a `SKILL.md`, a `scenarios.md` or a check
  script: you only add the summaries, then commit the records as they are and refresh the copies.

## What you read

- The ticket `/home/usain/gov-os-worktrees/W2-101/.tickets/DAEO-6icv.md`: its S4 line and the `## Interface` (S4: "the
  summary is a hand-written `scenario-summaries.md` beside `scenario-records.yaml`, one entry per run (scenario,
  verdict, the record's `run_at`, a three-line summary of the reply ...)").
- The three `scenario-records.yaml` files, in `template/governance/kernel/skills/{frontend,ui-ux,devops}/`. They hold
  every run, in order: frontend and ui-ux three runs (run 1 at about 01:29 to 01:38 UTC, a diagnostic run at about
  01:40 to 01:46, the final run at about 01:49 to 01:55), devops two (run 1 and the final run at about 01:55 to 02:00).
- The captures (read-only):
  - `/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/briefs/ps-3-final-replies.md`: the final run, all
    nine scenarios, each with its record line (verdict, `run_at`, version), the session's reply and the judgement.
  - `/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/briefs/ps-3-diag-replies.md`: the diagnostic run of
    frontend and ui-ux (six scenarios; frontend scenario 3 failed there, before the fix to frontend 1.1.0).
  - Run 1 was made without the capture: no reply exists for it.

## What to write

In each of the three kernel skill folders, `scenario-summaries.md`:

- A title and two or three lines saying what it is: the summaries of the `gov skilleval` runs in
  `scenario-records.yaml` beside it, the replies taken from the lead's capture of the same run (the envelope carries no
  reply), and that run 1 had no capture.
- **One entry per record entry (per run of each scenario), in the records' order**, each a `### ` heading naming the
  run and scenario (for example `### Final run, scenario 2: <title>`), then labelled lines:
  - `- **Scenario:** <n>`, `- **Verdict:** <pass|fail>`, `- **run_at:** <the record's run_at, copied exactly>`,
    `- **Skill version:** <the record's skill_version>`;
  - `- **Summary:**` followed by exactly three lines (indented as list continuation, or three sub-bullets) summarising
    what the session's reply did and why the judgement passed or failed it, in plain words, from the capture;
  - for a run-1 entry: the summary's three lines say no transcript was captured, and give the record's verdict and
    cause.
- Accurate to the capture: never claim more than the reply shows.

Then:
- Copy each kernel folder's new and changed files (`scenario-summaries.md`, `scenario-records.yaml`) byte for byte into
  `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/`, and show `diff -r` of each kernel folder
  against its two copies is empty.
- Check nothing else broke: `python3 template/governance/kernel/skills/<skill>/check_domain_skill.py template/governance/kernel/skills/<skill>/SKILL.md` → `PASS` for each, and
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.check.skill_validator template/governance/kernel/skills/frontend template/governance/kernel/skills/ui-ux template/governance/kernel/skills/devops` → no finding.

## Commit

One commit: the three `scenario-records.yaml` (as the harness wrote them), the three `scenario-summaries.md`, and
their copies. Trailers in one final paragraph, your paths only:

    git commit -m "W2-101: the scenario records of the real gov skilleval runs and their summaries, with the copies" --trailer "Task: DAEO-6icv" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-616, DEC-645" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

## The acceptance tests

`/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/TESTS-READY` exists. After your commit, run them once
through `PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.cli.main accept W2-101 --root /home/usain/gov-os-worktrees/W2-101`
and report its result per KPI line (cases about `.claude/skills/<skill>/` are expected red until the copies ACT
places those folders: name them; name any other red with its message). Never read a test's source.

## Return

Your last message. **The twelve fields first, each a labelled line** ("none" where nothing): task / status /
work_completed / files_changed / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Include the sandbox check first in `evidence`, the commit (12-digit hash, subject), each
check's output, the entry count per skill, `gov accept`'s result per KPI line, and the guard refusals you met (time,
form, reason). Status is one of DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED, AUTH_REQUIRED.
