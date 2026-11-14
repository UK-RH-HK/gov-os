# Brief: product-spec, DAEO-6icv (W2-101), run 3, batch 4: L1, each skill's `output:` as a path class

You are a fresh product-spec worker. Ticket: `DAEO-6icv` (W2-101), profile STANDARD: three kernel domain skills for
the engineer role (`frontend`, `ui-ux`, `devops`), already written and committed on `w2/W2-101`. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-101` on branch `w2/W2-101`. One red case from another ticket's suite (W2-11,
the skill template's own acceptance tests) fails on the three skills. You are given the failing output only, below.
Fix the cause. The ticket's context packet (built by the lead) is
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
  tool; never open the evaluation sets' root or any hidden or memory-verdict folder. W2-11's tests
  (`tests/acceptance/W2-11/`) are another ticket's and open to you.
- **Search (DEC-1065):** no `gov retrieve` or `gov context` inside the sandbox; Read and Grep tools, naming the folder
  a search starts at; search once more in other words if the first does not answer. Grep the register only by id.
- **Forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no backticks, no `bash -c`, no
  long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; scratch
  scripts go under your session's own `$TMPDIR`. Keep the sandbox's `$TMPDIR`; never set it.
- **Every pytest** goes through the slot:
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <path or node id> -q -p no:cacheprovider`
- **Refused twice for the same call: stop and say so** (DEC-1142 (9)); never work around a refusal; report it.
- Install nothing; no subagents that write; never ask or notify the owner; commit hashes as 12 digits in your return
  (DEC-911). No real model call: you do not run `gov skilleval`; the lead re-runs all nine scenarios after your commit.
- **Never edit** a `scenario-records.yaml`, a `scenario-summaries.md`, a `scenarios.md` or a `check_domain_skill.py`:
  the records and summaries are refreshed after the lead's re-run, and the scenarios must stay as committed (S4: the
  scenarios precede the skill text).

## The failing output (L1)

```
tests/acceptance/W2-11/test_w2_11_round2.py::test_every_write_step_lies_in_the_skills_output_class[frontend] FAILED
tests/acceptance/W2-11/test_w2_11_round2.py::test_every_write_step_lies_in_the_skills_output_class[ui-ux] FAILED
tests/acceptance/W2-11/test_w2_11_round2.py::test_every_write_step_lies_in_the_skills_output_class[devops] FAILED
AssertionError: <skill> tells its role to write outside its output class "the ticket's own allowed paths":
  ['output is neither none nor a path class: "the ticket\'s own allowed paths"']
```

## What to do

- Read how the W2-11 suite reads `output:` (`tests/acceptance/W2-11/w2_11_support.py`: `output_classes`,
  `declares_none`, `write_targets`, `stray_writes`; and `test_w2_11_round2.py` around `_output_findings`) and the skill
  template `template/governance/kernel/templates/skill.md` (what it says `output` is).
- Give each of the three skills an `output:` that is `none` or a path class (a token holding `/` or `*`) and that is
  honest about what the method tells the engineer to write. Every write step in the skill folder's Markdown must then
  lie inside it (the same case checks `stray_writes` on every `.md` in the folder, scenarios included; if a scenario's
  text would be flagged, report it as a finding and stop rather than editing the scenario). State your choice and why
  in the return.
- A skill whose text changes raises its version (the template): raise each of the three skills' `version` (and
  `metadata.version` if present) by one minor step (frontend 1.1.0 → 1.2.0; ui-ux and devops 1.0.0 → 1.1.0).
- Keep everything else passing: each skill's own check
  (`python3 template/governance/kernel/skills/<skill>/check_domain_skill.py template/governance/kernel/skills/<skill>/SKILL.md` → `PASS`),
  the validator (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.check.skill_validator template/governance/kernel/skills/frontend template/governance/kernel/skills/ui-ux template/governance/kernel/skills/devops` → no finding),
  the body ≤ about 150 lines, and the whole W2-11 suite: run `tests/acceptance/W2-11/` through the slot and report
  every red that names `frontend`, `ui-ux` or `devops` (none should remain); name any other red as not yours.
- Then refresh the byte copies of each changed file in `.rulesync/skills/<skill>/` and
  `template/.rulesync/skills/<skill>/`, and show `diff -r` of each kernel folder against its two copies is empty.

## Commit

One commit: the three `SKILL.md` files and their copies. Trailers in one final paragraph, your paths only:

    git commit -m "W2-101: each domain skill's output is a path class (L1); versions raised; copies refreshed" --trailer "Task: DAEO-6icv" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-616, DEC-645" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

## Return

Your last message. **The twelve fields first, each a labelled line** ("none" where nothing): task / status /
work_completed / files_changed / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Include the sandbox check first in `evidence`, the commit (12-digit hash, subject), the
`output:` value chosen per skill and why, each check's output, the W2-11 suite's counts and any red, and the guard
refusals you met (time, form, reason). Status is one of DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED,
LAUNCH_BLOCKED, AUTH_REQUIRED.
