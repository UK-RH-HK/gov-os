# Brief: product-spec, DAEO-uw5h (W2-100), fix batch 2 — four red cases of an earlier suite (W2-11)

You are a fresh product-spec worker. Ticket: `DAEO-uw5h` (W2-100), profile STANDARD, class C2. You work only in the
ticket's worktree `/home/usain/gov-os-worktrees/W2-100` on branch `w2/W2-100`. The lead's verification run is red on
four cases of the skill template's suite (W2-11); you are given their failing output only. Make them green with the
smallest change to the four skills' text, and keep every other check green.

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-uw5h','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (status ESCALATION, with what you saw). Do not delete
  any file (a) made.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `product-spec` and `DAEO-uw5h`),
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-100` and `w2/W2-100`),
  `git rev-parse --short=12 HEAD` (expect `b266cf8a40f2`) and `git status --short` (expect nothing). Anything else:
  stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- **Your paths for this batch:** `template/governance/kernel/skills/{backend,api,data,security}/SKILL.md` and their
  copies `.rulesync/skills/<skill>/SKILL.md` and `template/.rulesync/skills/<skill>/SKILL.md` (byte-equal to the kernel
  file). Nothing else: not `scenarios.md`, not `scenario-records.yaml`, not `scenario-summaries.md`, not the check
  script, not `tests/`, not `src/`, never `.claude/`.
- **Never read `tests/acceptance/W2-100/`** in any tree or branch (DEC-820 (c)). You may read
  `tests/acceptance/W2-11/` (an earlier suite, not this ticket's). Reads are open otherwise, except secrets and keys,
  the held-out material's contents and the hidden half of any evaluation set; never open an evaluation set's root or
  any hidden or memory-verdict folder. Search with the Read and Grep tools, naming the folder a search starts at.
- No `git checkout`, `reset`, `clean`, amend, rebase, merge, push, tag, stash or `worktree`. No model call (never run
  `gov skilleval` or `claude`): the lead reruns the scenarios after you.
- **Command forms the guard can read:** no shell variable or `$(…)` as a write target, no here-document, no
  backticks, no `bash -c '…'`, no long inline `python3 -c` with braces. Edit with the Edit tool at literal absolute
  paths; `cp` of a named file to a named literal path is fine.
- **Every pytest through the heavy slot**, `TMPDIR` your sandbox's own, `PYTHONUSERBASE=/home/usain/.local`:
  `env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-11 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  A slot gate's refusal or wait is a wait, not a refusal.
- Install nothing. No subagents that write. Never write `.gov-runtime/**`. Never ask or notify the owner.
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal (DEC-1142 (9)).
- Write commit hashes as 12 digits in your return.

## The failing output (the lead's verification run at b266cf8a40f2)

```
________ test_every_write_step_lies_in_the_skills_output_class[backend] ________
tests/acceptance/W2-11/test_w2_11_round2.py:218: in test_every_write_step_lies_in_the_skills_output_class
    assert not found, f"{name} tells its role to write outside its output class {front.get('output')!r}: {found}"
E   AssertionError: backend tells its role to write outside its output class 'none': ["template/governance/kernel/skills/backend/SKILL.md: ['claude/skills/']"]
(the same for api, data and security)
FAILED tests/acceptance/W2-11/test_w2_11_round2.py::test_every_write_step_lies_in_the_skills_output_class[api]
FAILED tests/acceptance/W2-11/test_w2_11_round2.py::test_every_write_step_lies_in_the_skills_output_class[backend]
FAILED tests/acceptance/W2-11/test_w2_11_round2.py::test_every_write_step_lies_in_the_skills_output_class[data]
FAILED tests/acceptance/W2-11/test_w2_11_round2.py::test_every_write_step_lies_in_the_skills_output_class[security]
```

(The other reds of the run, `test_the_skill_carries_one_version_in_all_four_places[...]` and this ticket's
`.claude/skills/` cases, wait for the CTO's copies ACT, which generates `.claude/skills/<skill>/`: not yours.)

## The rules that stay

- The skill text keeps everything the ticket and the interface ask for: the template's eight sections in order, the
  five labelled parts, the area's named points (`check_domain_skill.py` must still print PASS for each), the body
  within about 150 lines, no permission line, and for security no line with the word "finding" and P2 or P3.
- **The skill template's rule: a skill whose text changes raises its version.** Raise each changed skill's `version`
  and `metadata.version` from `"1.0.0"` to `"1.0.1"` (both, equal). Change nothing else in the front matter.

## Checks, quoted in your return

- `tests/acceptance/W2-11` through the heavy slot (command above): the four cases green; name every other red with
  its first error line (the `four_places` cases wait for the copies ACT).
- For each skill: `python3 template/governance/kernel/skills/<skill>/check_domain_skill.py template/governance/kernel/skills/<skill>/SKILL.md`: PASS.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-100/src python3 -m gov.check.skill_validator template/governance/kernel/skills/backend template/governance/kernel/skills/api template/governance/kernel/skills/data template/governance/kernel/skills/security`: exit 0.
- `diff -r` of each skill folder against each of its two `.rulesync` copies: empty. `git diff --stat`: only the twelve
  SKILL.md files.

## Commit

Check first that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (if one is, stop
and return; never `--no-verify`). Every trailer in the one final block:

    git commit -m "W2-100 (DAEO-uw5h): the four domain skills 1.0.1: <what changed, in a few words> (fix batch 2, W2-11's output-class case)" --trailer "Task: DAEO-uw5h" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-832, DEC-315" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <the twelve SKILL.md paths>

Then `git log --oneline -2` and `git status --short` (expect nothing).

## Return

Your last message, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):
the sandbox check first in `evidence`; the commit's 12-digit hash and trailers; the diff of each changed line; the
checks' output; the read refusals you met.

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
