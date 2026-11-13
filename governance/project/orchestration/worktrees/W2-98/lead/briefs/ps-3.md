You are a fresh product-spec worker. Ticket: DAEO-wi46 (W2-98, "The spec-writing skill for product-spec"), profile STANDARD, run 3, fix batch 3 after review round 1 (DEC-136). You work only in the ticket's worktree `/home/usain/gov-os-worktrees/W2-98` (branch `w2/W2-98`, head 384c92b8b429); you are its one writer while you run.

Your budget: about 40 minutes. A fix to the skill's check and its form reference, and their two byte copies.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wi46','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.
Then: `printenv GOV_ROLE GOV_TICKET` (expect `product-spec`, `DAEO-wi46`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-98`, `w2/W2-98`). If anything differs, stop and say so.

## What you read and may not read
- The ticket `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-wi46.md` (its `## Interface` I1-I4 binds the words and exits) and the skill folder `template/governance/kernel/skills/spec-writing/` (SKILL.md, spec-form.md, check_spec.py, imports.yaml).
- **You never read the acceptance tests** (`tests/acceptance/W2-98/`, DEC-820 (c)); you may run them and read their pass/fail lines. Read and Grep only (no `gov retrieve`, no `gov context`). Never open the evaluation sets' root or any hidden or memory-verdict folder.

## What to do
Make `check_spec.py` hold every behaviour below, keeping every existing output word and exit; state the new rules briefly in `spec-form.md` (the KPI form, the Test data cells, the imports rule) and, only if a Done-when or Steps line becomes untrue, in SKILL.md (keep its body under 150 lines and the validator at exit 0). Keep check_spec.py standard library only and readable (about 300 lines at most). Then copy the changed files with `cp` to `.rulesync/skills/spec-writing/` and `template/.rulesync/skills/spec-writing/` (byte copies; never edit a copy by hand). Never write `.claude/`.

## The described behaviours (review round 1 of W2-98, findings F1, F2, F4 and part of F3; DEC-136)

The skill's check is `python3 template/governance/kernel/skills/spec-writing/check_spec.py <spec.md>` (and `--imports <folder>`); its words and exits are the ticket's I3/I4 and stay as they are: `REFUSED <part>: <reason>` lines and exit 1; `P1 Test data: <source> cannot be secured` and exit 2; `PASS` alone and exit 0; `REFUSED import <part>: <reason>` and exit 1. Each behaviour below holds on an otherwise clean spec (the nine `##` parts, clean KPIs `- K<n>: <behaviour>` each with an indented `  Fails if: <text>` line, a clean Test data table).

- **B1 (F1, fails open today).** Under `## KPIs`, a list item (a line starting with `-`, `*`, `+` or a number and `.` or `)`) that is neither a KPI line in form nor a `Fails if:` line is refused with a `REFUSED KPIs:` line whose reason names the line (it quotes the line, so an id-like text such as `K2` in it appears in the reason); exit 1, no PASS, even when the other KPIs are clean. In form means: a `-` or `*` bullet, then `K<n>:` (digits only, the colon right after the digits; the id may be bold as `**K1**:` or `**K1:**`), then the behaviour. Examples that must be refused: `- K2 : The member sees it.` (a space before the colon), `2. K2: The member sees it.` (a numbered item), `- K2a: The member sees it.`, `- K3 (new): The member sees it.`, `- **K2** — the member sees it.`. A plain prose line (not a list item) before the first KPI is allowed and never refused.
- **B2 (F1, fails open today).** A non-blank line after a KPI line, up to that KPI's `Fails if:` line, the next list item or the next section, is part of that KPI's behaviour whether it is indented or starts at column 0 (a Markdown lazy continuation), and is judged for code: `- K1: A member sees the page after` / `send_welcome() runs.` / `  Fails if: no page.` gives `REFUSED KPIs: K1 names code (...)`. Non-blank lines after the `Fails if:` line, up to the next list item or section, are part of the failure text and judged the same way (`REFUSED KPIs: K<n> names code in its Fails if: line (...)`).
- **B3 (F2, fails open today).** In the Test data table, an empty `privacy` cell or an empty `secrets` cell is refused, naming the source and the column: `REFUSED Test data: <source> has no privacy` / `REFUSED Test data: <source> has no secrets`. `none` (or any other stated text) is a valid value for both.
- **B4 (F2, fails open today).** An `owner`, `source` or `licence or recipe` cell holding only a placeholder is refused exactly as if it were empty, with the same words (`<source> has no owner`, `row <n> has no source`, `<source> has no licence` for an imported row, `<source> has no recipe` for a synthetic one). Placeholders, matched case-insensitively with surrounding spaces and `*`/`_` emphasis ignored: `-`, `—`, `–`, `TBD`, `TODO`, `unknown`, `?`, `n/a`, `none`.
- **B5 (F4, fails open today).** `--imports <folder>`: records are read only from the list under the top-level `imports:` key; an entry under any other top-level key is no record (a marked part recorded only there is refused, `REFUSED import <part>: no licence record`). A part with more than one record is refused unless every one of its records carries an allowed licence: one GPL-3.0 record and one MIT record for the same part give `REFUSED import <part>: licence GPL-3.0 is not in the allowed list`.
- **B6 (F3, fails closed today).** The failure line may carry Markdown emphasis on its label: `**Fails if:** <text>`, `*Fails if:* <text>` and `_Fails if:_ <text>` each count as the KPI's `Fails if:` line (no refusal for a missing failure line, and the `_` emphasis is not taken as a snake_case identifier). A `Fails if:` label with its text on the next indented line counts as present. A word in underscore emphasis with no underscore inside it (`_quickly_`) is emphasis, not a snake_case identifier; `send_welcome` and `__all__` still are code.

## Check your work (every pytest through the heavy slot)
- Your own planted specs and folders go under your sandbox's `$TMPDIR` (a folder such as `$TMPDIR/ps3`; `/tmp/gov-os-lead-W2-98` and `.gov-runtime/scratch/ps/` were not writable for earlier workers). Write a script there with the Write tool and run it: each example in B1-B6 gives the stated result; a clean spec still passes; an intro prose line before K1 passes; `none` in privacy and secrets passes. Remove the folder before you return.
- `cd /home/usain/gov-os-worktrees/W2-98 && TMPDIR=/tmp/gov-os-lead-W2-98 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-98 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line` (if that TMPDIR is not writable, your sandbox's `$TMPDIR` written out literally). Never `-x`, never `--basetemp`. Expected: 92 passed, 2 failed (`test_the_claude_copy_matches_the_kernel_source`, `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`, until the CTO's copies ACT). The test designer is writing cases for B1-B6 in parallel; they are merged later. Remove any `pytest-of-*` folder pytest leaves in the worktree root, by its exact path.
- `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src python3 -m gov.check.skill_validator template/governance/kernel/skills/spec-writing/SKILL.md` exits 0; `diff -r` of each `.rulesync` copy against the kernel folder is empty.

## Commands the guard can read (DEC-941 item 4a)
No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; write files with the Write and Edit tools and absolute paths. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so** (DEC-1142 (9)). A resource gate's refusal is a wait (DEC-1146). On an authentication error, return `AUTH_REQUIRED`.

## Commit
- Check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if one is there, stop. Never `--no-verify`. No amend, rebase, reset, merge or push.
- `git commit -m "<subject>" --trailer "Task: DAEO-wi46" --trailer "Role: product-spec" --trailer "Implements: DEC-959, DEC-957, DEC-616, DEC-645, DEC-1083, DEC-1084, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- template/governance/kernel/skills/spec-writing .rulesync/skills/spec-writing template/.rulesync/skills/spec-writing`

## Never
Never write `.claude/`, `tests/`, `src/`, `docs/`, a ticket file, the register or a plan file; never run `gov close`, `gov adopt`, `gov pause`, `gov accept`; never ask or notify the owner; install nothing.

## Return
One message, your last. The twelve fields first, each a labelled line; then the change, the hand-check output, the pytest counts and red names, the validator and diff results, the sandbox check.
```
task: / status: (DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, with one line why) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
