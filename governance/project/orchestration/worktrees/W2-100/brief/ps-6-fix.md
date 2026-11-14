# Brief: product-spec, DAEO-uw5h (W2-100), fix batch 3 — two scenarios fail on fresh sessions (api 2, data 2)

You are a fresh product-spec worker. Ticket: `DAEO-uw5h` (W2-100), profile STANDARD, class C2. You work only in the
ticket's worktree `/home/usain/gov-os-worktrees/W2-100` on branch `w2/W2-100`. The lead ran each domain skill's three
scenarios through the real `gov skilleval` on fresh sessions (run 6, the skills at 1.0.1, with nothing in the skill
folder but `SKILL.md` and `check_domain_skill.py`). Two scenarios failed. You are given their failing output only. Make
the skill text guide an engineer to the behaviour the scenario expects. **The scenarios are the test: never change
`scenarios.md`.**

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uw5h','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK (its exit may be 1
  only because it lists the four modified `scenario-records.yaml` files as needing update).
- If (a) wrote the file or (b) failed otherwise, stop there and return (status ESCALATION, with what you saw). Do not
  delete any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-uw5h`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-100` and `w2/W2-100`),
  `git rev-parse --short=12 HEAD` (expect `f8e7c0fad6c6`) and `git status --short` (expect exactly the four modified
  `template/governance/kernel/skills/{backend,api,data,security}/scenario-records.yaml`: the lead's runs; never touch,
  add or commit them). Anything else: stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- **Your paths for this batch:** `template/governance/kernel/skills/api/SKILL.md`,
  `template/governance/kernel/skills/data/SKILL.md`, and their copies `.rulesync/skills/{api,data}/SKILL.md` and
  `template/.rulesync/skills/{api,data}/SKILL.md` (byte-equal to the kernel file). Nothing else: not `scenarios.md`,
  not the records or summaries, not the check script, not backend or security, not `tests/`, not `src/`, never
  `.claude/`.
- **Never read `tests/acceptance/W2-100/`** in any tree or branch (DEC-820 (c)). Reads are open otherwise, except
  secrets and keys, the held-out material's contents and the hidden half of any evaluation set; never open an
  evaluation set's root or any hidden or memory-verdict folder. Search with the Read and Grep tools, naming the folder
  a search starts at.
- No `git checkout`, `reset`, `clean`, amend, rebase, merge, push, tag, stash or `worktree`. No model call (never run
  `gov skilleval` or `claude`): the lead reruns the scenarios after you.
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no backticks,
  no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute paths; `cp` of
  a named file to a named literal path is fine.
- **Every pytest through the heavy slot**, `TMPDIR` your sandbox's own, `PYTHONUSERBASE=/home/usain/.local`:
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-11 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- Install nothing. No subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal (DEC-1142 (9)).
- Write commit hashes as 12 digits in your return.

## The failing output (read both files in full)

- `/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval/fail-api-2-run6.md`: api, scenario 2 (A
  rename in a published response). The judge: part 1 held (`total` kept, `total_cents` added, `total` deprecated, as an
  option); part 2, "names a backward-compatibility test for the old shape", not met: the session escalated the rename
  as a P2 package and named only a test that the two fields agree, never a test that an old client still gets the old
  v1 shape. (The same scenario also failed in run 1, at 1.0.0, on a fresh session; it passed in two other runs.)
- `/home/usain/gov-os-worktrees/W2-100/.gov-runtime/scratch/lead/skilleval/fail-data-2-run6.md`: data, scenario 2 (An
  import that lets bad rows through). The judge: rules named and rejected rows kept with a reason (met); "a named test
  with a bad row" not met: the session only counted its tests ("9 rule tests, 11 import tests") after its attempt to
  write a test file was refused, and named none with its bad row in the reply.

Facts of the evaluation: the session has only the skill and the scenario's situation text; it has no repository, and
its writes and commands may be refused. It is judged on its reply alone. So the skill's guidance has to make the
reply itself carry the decisive points (in the return's `tests` field and the steps), whether or not files can be
written.

## What to change (your judgement, within these rules)

- Guidance an engineer in the area should follow anyway, not wording aimed at a judge: for example, in api, that a
  breaking change asked for within a published version is made additive where it can be (keep the old field, add the
  new, mark the old deprecated in the contract) with a backward-compatibility test that names the old client and the
  old shape, and only the rest escalated; and, in both skills, that the return names each test with its input (the bad
  row, the old-shape request), written or not.
- Keep everything the ticket and the interface ask for: the template's eight sections in order, the five labelled
  parts, the area's named points (`check_domain_skill.py` PASS), no permission line, the body within about 150 lines
  (api is 132, data 134 body lines now), Output and handover naming the twelve fields, Escalation P3/P2/P1/Emergency.
- **The skill template's rule: a skill whose text changes raises its version.** Raise api's and data's `version` and
  `metadata.version` from `"1.0.1"` to `"1.0.2"` (both, equal). Backend and security are not touched.

## Checks, quoted in your return

- `tests/acceptance/W2-11` through the heavy slot (command above): name every red with its first error line (the four
  `four_places` cases wait for the copies ACT; any other red is yours to fix).
- `python3 template/governance/kernel/skills/<skill>/check_domain_skill.py template/governance/kernel/skills/<skill>/SKILL.md`
  for api and data: PASS.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.check.skill_validator template/governance/kernel/skills/api template/governance/kernel/skills/data`: exit 0.
- Each body's line count; `diff` of each changed SKILL.md against its two copies: empty; `git diff --stat`: only the
  six SKILL.md files (plus the four records you never touch).

## Commit

Check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (if one is, stop
and return; never `--no-verify`). Every trailer in the one final block:

    git commit -m "W2-100 (DAEO-uw5h): api and data 1.0.2: <what changed, in a few words> (fix batch 3, run 6's fresh-session fails)" --trailer "Task: DAEO-uw5h" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-957" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- template/governance/kernel/skills/api/SKILL.md template/governance/kernel/skills/data/SKILL.md .rulesync/skills/api/SKILL.md .rulesync/skills/data/SKILL.md template/.rulesync/skills/api/SKILL.md template/.rulesync/skills/data/SKILL.md

Then `git log --oneline -2` and `git status --short`.

## Return

Your last message, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing): the
sandbox check first in `evidence`; the commit's 12-digit hash and trailers; the diff of each changed passage; the
checks' output; the read refusals you met.

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
