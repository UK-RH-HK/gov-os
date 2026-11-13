You are a fresh independent auditor (read-only reviewer). Ticket: DAEO-wi46 (W2-98, "The spec-writing skill for product-spec"), profile STANDARD, review round 2, the last (round 1 FAILED on 384c92b8b429: F1, F2 failed; F3-F6 rows). The head to probe: `c530a0a1a` (the full hash from `git -C /home/usain/gov-os-worktrees/W2-98 rev-parse HEAD`; code at 55b360a5e80c, tests merged on top) on branch `w2/W2-98`, worktree `/home/usain/gov-os-worktrees/W2-98`. You write nothing in the repository; your return is your whole record (the lead writes the probe record from it).

Your budget: about 45 minutes.

## Step 0, before any work (report it first)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wi46','w').write('x')"` must FAIL.
(b) `git -C /home/usain/gov-os-worktrees/W2-98 rev-parse HEAD` must start with `c530a0a1a`; `printenv GOV_ROLE GOV_TICKET` should print `independent-auditor`, `DAEO-wi46`. If (a) wrote the file or the head differs, stop and return.
Also give `python3 -c "import gov; print(gov.__file__)"` run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src`.

## What changed (the diff to probe: `git -C /home/usain/gov-os-worktrees/W2-98 diff 6c2c3ed93bee c530a0a1a`)
A new kernel skill `template/governance/kernel/skills/spec-writing/` (SKILL.md, spec-form.md, check_spec.py, imports.yaml) and its two byte copies `.rulesync/skills/spec-writing/` and `template/.rulesync/skills/spec-writing/`. `.claude/skills/spec-writing/` is deliberately absent: the CTO's copies ACT generates it (DEC-315, DEC-1112 (3)); two acceptance cases are red for that reason alone (`test_the_claude_copy_matches_the_kernel_source`, `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`).

## What you judge against
- The ticket `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-wi46.md`: its KPI lines (success-1..6, failure-1..5; the `lifted:` lines are optional, DEC-1083) and its `## Interface` I1-I4 (binding words and exits).
- Decisions by id in `/home/usain/gov-os-worktrees/W2-98/docs/DECISION_REGISTER.md` (grep by id only): DEC-959 (items 5, 8), DEC-957, DEC-1156 (5), DEC-1052, DEC-1083, DEC-1084, DEC-616, DEC-645, DEC-1112 (3), DEC-315, DEC-801, DEC-808.
- The skill template `template/governance/kernel/templates/skill.md`; a sibling skill `template/governance/kernel/skills/qa-review/SKILL.md`; `template/governance/kernel/skills/superpowers/vendored.yaml` (I4's form).
- The acceptance suite `tests/acceptance/W2-98/` (README and cases): you may read it, to judge whether the cases test the KPI lines and whether the code passes them honestly (not by special-casing the planted text).

## Round 1 and what was done
Round 1's record (another reviewer's; read it for its reproductions): `/home/usain/gov-os-worktrees/W2-98/.gov-runtime/scratch/lead/rv-1.return.md`. The lead's triage: F1 and F2 (fail open, ordinary work) fixed; F4's two fail-open parts (records outside `imports:`, a part with a forbidden and an allowed record) fixed; F3's `Fails if:` label forms and `_word_` emphasis fixed; F3's other prose forms (domains, emails, `Node.js`, `Member(s)`), F5 (`output:` key) and F6 (hidden half `no` on a measuring row) left as recorded rows. The fix went as described behaviours B1-B6 (`/home/usain/gov-os-worktrees/W2-98/.gov-runtime/scratch/lead/briefs/behaviours-r1.md`) to a test designer (`tests/acceptance/W2-98/test_w2_98_review_r1.py`, merged in c530a0a1a) and an implementer (55b360a5e80c). Re-run every round-1 reproduction of F1, F2 and F4 and say for each whether it is now refused; then probe afresh as below, including what the fix may have broken (ordinary specs now refused, e.g. sub-bullets under a KPI, an intro line, tables).

**Probe files:** last round the Write tool was refused in `$TMPDIR` (a permission prompt in a headless session). Probe in memory as round 1 did (import `check_spec.py` with `importlib` from its path and call its functions on text, or run it on files you can create), and do not retry a refused write form.

## What to probe (in proportion to STANDARD)
1. check_spec.py fails open anywhere a KPI line forbids: a KPI naming code passes (try forms I3 lists, wrapped lines, bold ids, odd spacing, a `K<n>` line in another list style); a KPI with no failure line passes; test data with no source, owner, licence/recipe passes; unsecurable data (`secured: no`) passes or is skipped; PASS printed beside a REFUSED or P1 line; a missing part not named; the imports check passing a marked part with no record or a forbidden licence (try case, spacing and YAML styles).
2. False refusals of ordinary prose that would make the skill unusable (abbreviations, hyphens, numbers, parentheses).
3. SKILL.md against the template and S4: front matter, section order, Sources last, Steps a checklist naming every part, Done when yes/no items, twelve fields, escalation P3/P2/P1/Emergency, body size; the validator: `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src python3 -m gov.check.skill_validator template/governance/kernel/skills/spec-writing/SKILL.md`.
4. The copies: `diff -r` of each `.rulesync` copy against the kernel folder; the adapter check `cd /home/usain/gov-os-worktrees/W2-98 && env PYTHONPATH=src python3 -m gov.adapters.portability` (expect only `GENERATED_DIFFERS`/missing for `.claude/skills/spec-writing`).
5. The suite: run it once (below) and report counts and red names.
Plant your probe files only under your sandbox's own `$TMPDIR` (the worktree and `/tmp/gov-os-lead-W2-98` are read-only for you); write probe scripts there with the Write tool and run them.

Run the suite through the heavy slot: `cd /home/usain/gov-os-worktrees/W2-98 && TMPDIR=<your writable $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-98 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line`. If pytest cannot write its basetemp, add `--basetemp=<your $TMPDIR>/bt`.

## Threat model (DEC-801, DEC-808)
Honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Only "yes" with "fails open" or "loses work" fails the review. Give each finding an id (F1, F2 …), the file:line, a reproduction (input and output), and a suggested described behaviour (not code).

## Rules
Reads are open except: secrets; the held-out qualification material's contents; the hidden half of any evaluation set; never open the evaluation sets' root or any hidden or memory-verdict folder. Search with Read and Grep only, on named folders. No `gov retrieve`, no `gov context`. Write nothing in any worktree. Commands the guard can read: no here-documents, no backticks, no `bash -c`, no shell variable as a write target. **Refused twice for the same call: stop and say so.** A resource gate's refusal is a wait. Never ask or notify the owner.

## Return
One message, your last. The twelve fields first, each a labelled line; then a fenced verdict block:
```verdict
verdict: PASS | FAIL
head: c530a0a1a
findings: <n> (failing: <ids or none>)
```
then the findings, the suite counts, the step 0 lines, the validator and adapter outputs.
```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
