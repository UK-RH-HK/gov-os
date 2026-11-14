# Brief: product-spec, DAEO-6icv (W2-101), run 2, fix batch 1 (a red from the real scenario runs)

You are a fresh product-spec worker. Ticket: `DAEO-6icv` (W2-101), profile STANDARD: three kernel domain skills for
the engineer role (`frontend`, `ui-ux`, `devops`), already written and committed on `w2/W2-101`. You work only in the
worktree `/home/usain/gov-os-worktrees/W2-101` on branch `w2/W2-101`. The lead ran each skill's three scenarios on
the real model with `gov skilleval`; one scenario fails. You are given the failing output only, below. Fix the cause.

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
  tool; never open the evaluation sets' root or any hidden or memory-verdict folder.
- **Search (DEC-1065):** no `gov retrieve` or `gov context` inside the sandbox; Read and Grep tools, naming the folder
  a search starts at; search once more in other words if the first does not answer. Grep the register only by id.
- **Forms (DEC-941 item 4a):** no shell variable as a write target, no here-document, no backticks, no `bash -c`, no
  long inline `python3 -c` with braces. Write files with the Write and Edit tools at literal absolute paths; scratch
  scripts go under your session's own `$TMPDIR` (writes under `.gov-runtime/scratch/` may be refused in a launched
  session). Keep the sandbox's `$TMPDIR`; never set it.
- **Refused twice for the same call: stop and say so** (DEC-1142 (9)); never work around a refusal; report it.
- Install nothing; no subagents that write; never ask or notify the owner; commit hashes as 12 digits in your return
  (DEC-911). No real model call: you do not run `gov skilleval`; the lead re-runs it after your commit.
- **Leave alone** the three untracked `scenario-records.yaml` files in the skill folders (the harness's records of the
  lead's runs): never edit, stage, commit or delete them.

## What you read

- The ticket `/home/usain/gov-os-worktrees/W2-101/.tickets/DAEO-6icv.md` (read-only): KPI lines and `## Interface`.
- The frontend skill as committed: `template/governance/kernel/skills/frontend/` (`SKILL.md`, `scenarios.md`,
  `check_domain_skill.py`), and the skill template `template/governance/kernel/templates/skill.md`.
- DEC-957 (the escalation rubric, P3/P2/P1/Emergency) and DEC-959 item 5 in `docs/DECISION_REGISTER.md`, by id.
- How the harness runs a scenario: the docstring and prompts at the top of `src/gov/skilleval/harness.py` (the session
  gets only the skill and the Situation text, in an empty folder; the judge sees only the Pass line, the Expected text
  and the session's reply).

## The failing output (frontend scenario 3, "A feature outside the support list"; failed in both runs)

The session's reply, then the judgement, as captured from the second run:

```
SESSION reply:
I ran the frontend skill. It decides the main question: the transition gets built as an enhancement, and the plain
page change becomes the fallback. But I didn't write any code. The workspace has only the skill's own two files: no
ticket, no spec, no code and no `allowed_paths`. [...]
- The spec doesn't say whether a plain page change is acceptable. The skill calls that a point the ticket leaves open:
  take the simplest reading, don't widen the scope, and record it in `discoveries`. It is not a P1, because nothing in
  the list or an approved flow changes.
- The record goes to you as the session's starter, not to the owner.
What I produced: only the handover below. No files.
[a twelve-field handover; status: blocked; discoveries: the support-list gap, simplest reading taken; proposed
decision: confirm in the spec that browser support means working navigation, with the animation as an enhancement]

JUDGEMENT:
- Support list unchanged: Met.
- Working fallback behind a feature check: Not met. The reply plans the right approach (`document.startViewTransition`
  check, plain page change as the fallback) and lists tests for both paths. But it wrote no code and ran no tests, so
  nothing was shipped.
- P1 rank, or saying it changes the spec: Not met. The reply says outright: "It is not a P1, because nothing in the
  list or an approved flow changes." It treats the question as an open point to note in `discoveries` and settles it
  with the simplest reading. [...]
- Addressed to the ticket lead, not the owner: Met.
The wrong rank alone fails the pass line.
VERDICT: FAIL
```

The full capture is at `/home/usain/gov-os-worktrees/W2-101/.gov-runtime/scratch/lead/briefs/ps-2-failing-output.txt`
(read-only for you). It also holds the run-1 record of ui-ux scenario 2 ("A mock with only the happy path"), which
failed once with no transcript and passed in the second run. Look at whether that scenario's Situation and Pass line
leave the judge room to disagree, and tighten it only if you find a real ambiguity.

## What to do

- Find the cause in the skill and the scenario. The reply followed the skill's text: the skill's Output and handover
  says "A support-list gap ... goes in `discoveries`: take the simplest reading", while its Escalation ranks a change to
  the support list P1. Settle the rule in the skill text so that a design intent the spec leaves open for a browser on
  the list is ranked consistently (decide which rank the method should give, from DEC-957's rubric), and make the
  scenario expect that rank.
- The scenario's Situation gives the session no code to change, so "ships a working fallback" cannot be judged from
  the reply. Give the Situation the material it needs (for example a short component snippet as an inline span, as
  scenarios 1 and 2 do) and keep the Pass line judgeable from the reply alone. Do not weaken what the scenario tests
  (support list unchanged, a fallback behind a feature check, the rank, addressed to the starter not the owner).
- A skill whose text changes raises its version (the template): raise the frontend skill's `version` and
  `metadata.version`.
- Keep everything else passing: the skill's own check (`python3 template/governance/kernel/skills/frontend/check_domain_skill.py template/governance/kernel/skills/frontend/SKILL.md` → `PASS`), the validator
  (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-101/src python3 -m gov.check.skill_validator template/governance/kernel/skills/frontend template/governance/kernel/skills/ui-ux template/governance/kernel/skills/devops` → no finding), the body ≤ about 150 lines, and the scenarios
  file in the form the harness parses (one line per bullet's text after joining; check with the harness's own parser
  if you like).
- Then refresh the byte copies of each changed folder in `.rulesync/skills/<skill>/` and
  `template/.rulesync/skills/<skill>/` (every tracked file; never the `scenario-records.yaml`), and show `diff -r`
  of each kernel folder against its two copies is empty apart from the untracked records.

## Commits

One commit for the scenario revision(s) first, then one for the skill text and copies. Trailers in one final
paragraph, your paths only:

    git commit -m "W2-101: <subject>" --trailer "Task: DAEO-6icv" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-957, DEC-616, DEC-645, CAP-24.b, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

## Return

Your last message. **The twelve fields first, each a labelled line** ("none" where nothing): task / status /
work_completed / files_changed / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Include the sandbox check first in `evidence`, the commits (12-digit hashes, subjects), each
check's output, the rank you chose and why (cite the rubric), what you changed in each scenario and why it does not
weaken it, and the guard refusals you met (time, form, reason). Status is one of DONE, PACKAGES, ESCALATION,
ESCALATION_BLOCKED, LAUNCH_BLOCKED, AUTH_REQUIRED.
