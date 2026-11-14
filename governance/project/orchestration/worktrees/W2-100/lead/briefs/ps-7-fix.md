# Brief: product-spec, DAEO-uw5h (W2-100), fix batch 4 — two examples that quote the scenarios' own nouns

You are a fresh product-spec worker. Ticket: `DAEO-uw5h` (W2-100), profile STANDARD, class C2. You work only in the
ticket's worktree `/home/usain/gov-os-worktrees/W2-100` on branch `w2/W2-100`. Two example phrases in the api and data
skills (added by the previous fix, commit `3318e42f6`) reuse the nouns of the skills' own test scenarios. A skill is
judged by its scenarios on fresh sessions, so its text must not carry a scenario's specific endpoint, field or table:
that teaches to the test. Replace each example with a neutral one that makes the same point.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uw5h','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK (its exit may be 1
  only because it lists the four modified `scenario-records.yaml` files as needing update).
- If (a) wrote the file or (b) failed otherwise, stop there and return (status ESCALATION, with what you saw). Do not
  delete any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-uw5h`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-100` and `w2/W2-100`),
  `git rev-parse --short=12 HEAD` (expect `3318e42f6...`) and `git status --short` (expect exactly the four modified
  `template/governance/kernel/skills/{backend,api,data,security}/scenario-records.yaml`: the lead's runs; never touch,
  add or commit them). Anything else: stop and say so.
- **Your paths for this batch:** `template/governance/kernel/skills/api/SKILL.md`,
  `template/governance/kernel/skills/data/SKILL.md` and their copies `.rulesync/skills/{api,data}/SKILL.md` and
  `template/.rulesync/skills/{api,data}/SKILL.md` (byte-equal). Nothing else; never `scenarios.md`.
- **Never read `tests/acceptance/W2-100/`** in any tree or branch (DEC-820 (c)). Reads are open otherwise, except
  secrets and keys, the held-out material's contents and the hidden half of any evaluation set.
- No `git checkout`, `reset`, `clean`, amend, rebase, merge, push, tag, stash or `worktree`. No model call.
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no backticks,
  no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute paths; `cp` of
  a named file to a named literal path is fine.
- Install nothing. No subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal (DEC-1142 (9)).

## The two phrases

- `template/governance/kernel/skills/api/SKILL.md` line 84: `(for example "old v1 client: GET /v1/orders/{id} still
  returns `total`, as published")` — `/v1/orders/{id}` and `total` are api scenario 2's.
- `template/governance/kernel/skills/data/SKILL.md` line 80: `(for example "test_missing_id: a row with a blank
  `shipment_id` is rejected as `id_missing` and kept in the rejected rows")` — `shipment_id` is data scenario 2's.

Read `template/governance/kernel/skills/{api,data}/scenarios.md` to know which nouns to avoid; then, in both skills'
whole text, make sure no other phrase carries a scenario's specific endpoint, field, table, file or value (the method
stays general). Keep the example's point and its form; keep the body within about 150 lines. Both skills stay at
version `"1.0.2"` (no run or record was made at 1.0.2 before this fix; the lead records it). Change nothing else.

## Checks, quoted in your return

- `python3 template/governance/kernel/skills/<skill>/check_domain_skill.py template/governance/kernel/skills/<skill>/SKILL.md`
  for api and data: PASS.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.check.skill_validator template/governance/kernel/skills/api template/governance/kernel/skills/data`: exit 0.
- A grep of both SKILL.md files for each scenario's specific nouns (list the ones you checked): none found.
- `diff` of each changed SKILL.md against its two copies: empty; `git diff --stat`: only the six SKILL.md files (plus
  the four records you never touch).

## Commit

Check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (if one is, stop
and return; never `--no-verify`). Every trailer in the one final block:

    git commit -m "W2-100 (DAEO-uw5h): api and data 1.0.2: the test-naming examples no longer quote the scenarios' own nouns (fix batch 4)" --trailer "Task: DAEO-uw5h" --trailer "Role: product-spec" --trailer "Implements: DEC-959" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- template/governance/kernel/skills/api/SKILL.md template/governance/kernel/skills/data/SKILL.md .rulesync/skills/api/SKILL.md .rulesync/skills/data/SKILL.md template/.rulesync/skills/api/SKILL.md template/.rulesync/skills/data/SKILL.md

Then `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing): the
sandbox check first in `evidence`; the commit's 12-digit hash and trailers; the diff of each changed line; the checks'
output; the read refusals you met.

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
