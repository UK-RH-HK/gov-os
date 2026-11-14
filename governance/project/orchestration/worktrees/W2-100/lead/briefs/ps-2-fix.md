# Brief: product-spec, DAEO-uw5h (W2-100), fix batch 1 — one red acceptance case

You are a fresh product-spec worker. Ticket: `DAEO-uw5h` (W2-100), profile STANDARD, class C2. You work only in the
ticket's worktree `/home/usain/gov-os-worktrees/W2-100` on branch `w2/W2-100`. One acceptance case is red; you are
given its failing output only. Make it green with the smallest change to the scenario text, keep everything else as it is.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uw5h','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-uw5h`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-100` and `w2/W2-100`),
  `git rev-parse --short=12 HEAD` (expect `8ce2dd2681d8`). `git status --short` shows four untracked
  `template/governance/kernel/skills/<skill>/scenario-records.yaml` files: the lead's real runs; never touch, move,
  add or commit them. Anything else differs: stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- **Your paths for this batch:** `template/governance/kernel/skills/security/scenarios.md` and its two copies
  `.rulesync/skills/security/scenarios.md` and `template/.rulesync/skills/security/scenarios.md` (byte-equal to the
  kernel file). Nothing else: not SKILL.md, not `check_domain_skill.py`, not the other skills, not `tests/`, not `src/`.
- **Never read `tests/acceptance/W2-100/`** in any tree or branch (the counterpart's work, DEC-820 (c)). Reads are open
  otherwise, except secrets and keys, the held-out material's contents and the hidden half of any evaluation set;
  never open an evaluation set's root or any hidden or memory-verdict folder.
- No `git checkout`, `reset`, `clean`, amend, rebase, merge, push, tag, stash or `worktree`. No model call (never run
  `gov skilleval` or `claude`): the lead reruns the scenarios after you.
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute
  paths; `cp` of a named file to a named literal path is fine.
- Install nothing. No subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal (DEC-1142 (9)).
- Write commit hashes as 12 digits in your return.

## The failing output (the lead's run of `tests/acceptance/W2-100` at 8ce2dd2681d8; 205 passed, 25 failed: 24 of them wait for the lead's records, summaries and the copies ACT, this one does not)

```
______ test_a_security_scenario_holds_a_finding_whose_pass_line_wants_p1 _______
tests/acceptance/W2-100/test_w2_100_scenarios.py:55: in test_a_security_scenario_holds_a_finding_whose_pass_line_wants_p1
    assert hits, "no security scenario has a finding in its Situation and P1 in its Pass line"
E   AssertionError: no security scenario has a finding in its Situation and P1 in its Pass line
E   assert []
```

The interface (the ticket's `## Interface` and the lead's reading, which you may read in
`/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/brief/ps-1.md` under "The interface you build to"): the
security skill's scenarios include one with a security finding, whose pass line holds only when the reply routes it
as P1. Keep the scenario's meaning, its title, its Expected and its Pass line; the session must still not be told
the answer (the Situation never says how to route it). The form stays `gov skilleval`'s (three scenarios, each
`## <n>. <title>` with the three bullets).

## Checks, quoted in your return

- `diff` of the kernel `security/scenarios.md` against each copy: empty; `git diff --stat` shows only the three files.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.check.skill_validator template/governance/kernel/skills/security`: exit 0.
- `python3 template/governance/kernel/skills/security/check_domain_skill.py template/governance/kernel/skills/security/SKILL.md`: PASS.

## Commit

Check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (if one is, stop
and return; never `--no-verify`). Every trailer in the one final block:

    git commit -m "W2-100 (DAEO-uw5h): security scenario 2 names the security finding in its Situation (fix batch 1)" --trailer "Task: DAEO-uw5h" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-957" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- template/governance/kernel/skills/security/scenarios.md .rulesync/skills/security/scenarios.md template/.rulesync/skills/security/scenarios.md

Then `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):
the sandbox check first in `evidence`; the commit's 12-digit hash and trailers; the diff of the Situation line; the
checks' output; the read refusals you met.

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
