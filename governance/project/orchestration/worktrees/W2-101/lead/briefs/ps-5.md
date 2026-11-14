# Brief: product-spec, DAEO-6icv (W2-101), run 3, batch 5: run 3's scenario records and their summaries

You are a fresh product-spec worker. Ticket: `DAEO-6icv` (W2-101), profile STANDARD: three kernel domain skills for
the engineer role (`frontend`, `ui-ux`, `devops`), written and committed on `w2/W2-101`. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-101` on branch `w2/W2-101`. After the last skill change (`3cd17b73e3ee`:
each skill's `output:` a path class, versions frontend 1.2.0, ui-ux 1.1.0, devops 1.1.0), the lead re-ran all nine
scenarios on the real model with `gov skilleval` (run 3, 03:44 to 03:55 UTC; 9 of 9 pass). The harness appended three
entries to each skill's `scenario-records.yaml` (now modified, uncommitted). The harness now leaves
`scenario-summaries.md` out of the session's copy (W2-104's fix, merged at `57ea2d40bb9f`). The `--json` envelope
carries no reply text, so the lead captured each process's reply with a pass-through wrapper on `PATH`. Your job: add
run 3's entries to each skill's `scenario-summaries.md` from that capture (the ticket's `## Interface`, S4), and
commit them with the records and the refreshed copies. The ticket's context packet:
`/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/briefs/ctx-product-spec.md` (read-only).

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
- **Every pytest** (if you run one) goes through
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest ...`.
- **Refused twice for the same call: stop and say so** (DEC-1142 (9)); never work around a refusal; report it.
- Install nothing; no subagents that write; never ask or notify the owner; commit hashes as 12 digits (DEC-911). No
  model call; you do not run `gov skilleval`.
- **Never edit** a `scenario-records.yaml` (the harness's own record), a `SKILL.md`, a `scenarios.md` or a check
  script; never change an existing summary entry. You only add run 3's entries, then commit the records as they are and
  refresh the copies.

## What you read

- The ticket `/home/usain/gov-os-worktrees/W2-101/.tickets/DAEO-6icv.md`: its S4 line and the `## Interface`.
- The three `scenario-records.yaml` and `scenario-summaries.md`, in
  `template/governance/kernel/skills/{frontend,ui-ux,devops}/`: the summaries already hold one entry per earlier record
  entry; follow their form exactly.
- The capture extract (read-only):
  `/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/briefs/ps-5-r3-replies.md`: run 3's nine scenarios,
  each with its record line (verdict, `run_at`, version), the session's reply and the judgement. The raw capture is
  `/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/capture/replies.jsonl`, lines 31 to 48.

## What to write

- In each of the three `scenario-summaries.md`: one new entry per new record entry (the last three of each records
  file), after the existing ones, in the records' order, in the same form as the existing entries (a `### ` heading
  such as `### Run 3, scenario 2: <title>`, then the labelled lines `Scenario`, `Verdict`, `run_at` (copied exactly),
  `Skill version`, and `Summary` with exactly three lines saying what the reply did and why the judgement passed it,
  from the capture). Accurate to the capture: never claim more than the reply shows.
- If the file's opening lines describe which runs it covers, update that description to include run 3 (after the
  L1 change, with the harness leaving the summaries out of the session's copy). Change nothing else.

Then:
- Copy each kernel folder's changed files (`scenario-summaries.md`, `scenario-records.yaml`) byte for byte into
  `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/`, and show `diff -r` of each kernel folder
  against its two copies is empty.
- Check nothing else broke: `python3 template/governance/kernel/skills/<skill>/check_domain_skill.py template/governance/kernel/skills/<skill>/SKILL.md` → `PASS` for each, and
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.check.skill_validator template/governance/kernel/skills/frontend template/governance/kernel/skills/ui-ux template/governance/kernel/skills/devops` → no finding;
  and that the entry count of each summaries file equals its records file's entry count.

## Commit

One commit: the three `scenario-records.yaml` (as the harness wrote them), the three `scenario-summaries.md`, and
their copies. Trailers in one final paragraph, your paths only:

    git commit -m "W2-101: run 3's scenario records (after L1, 9 of 9 pass) and their summaries, with the copies" --trailer "Task: DAEO-6icv" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-616, DEC-645" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

## Return

Your last message. **The twelve fields first, each a labelled line** ("none" where nothing): task / status /
work_completed / files_changed / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Include the sandbox check first in `evidence`, the commit (12-digit hash, subject), each
check's output, the entry counts per skill (records and summaries), and the guard refusals you met (time, form,
reason). Status is one of DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED, AUTH_REQUIRED.
