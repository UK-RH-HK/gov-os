You are a fresh independent auditor (read-only reviewer). Ticket: DAEO-wi46 (W2-98, "The spec-writing skill for product-spec"), profile STANDARD. This is **a narrow independent check**, not a review round: review round 2 (the last, DEC-1010) FAILED on c530a0a1a236 with F1-F3; the owner decided P-W2-98-R2 (a) on 2026-11-13: one fix batch, then a narrow independent check of exactly that fix. The head to check: `f0259229e` (the full hash from `git -C /home/usain/gov-os-worktrees/W2-98 rev-parse HEAD`) on branch `w2/W2-98`, worktree `/home/usain/gov-os-worktrees/W2-98`. You write nothing in the repository; your return is your whole record (the lead writes the probe record from it).

Your budget: about 25 minutes.

## Step 0, before any work (report it first)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-wi46','w').write('x')"` must FAIL.
(b) `git -C /home/usain/gov-os-worktrees/W2-98 rev-parse HEAD` must start with `f0259229e`; `printenv GOV_ROLE GOV_TICKET` should print `independent-auditor`, `DAEO-wi46`. If (a) wrote the file or the head differs, stop and return.
Also give `python3 -c "import gov; print(gov.__file__)"` run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src`.

## Exactly what to check (the fix since c530a0a1a236)
`git -C /home/usain/gov-os-worktrees/W2-98 diff c530a0a1a236 f0259229e -- template/governance/kernel/skills/spec-writing .rulesync/skills/spec-writing template/.rulesync/skills/spec-writing tests/acceptance/W2-98`
(the branch also merged w2/integrate in c0f68478a; that merge is not yours to judge). The fix: `0b6d3e077` (product-spec, check_spec.py and spec-form.md and their two byte copies) and the tests `6a1290b8e`, `9cf504f57` (independent test designer, `tests/acceptance/W2-98/test_w2_98_review_r2.py` and README), merged in `f0259229e`.

The described behaviours the fix had to meet: `/home/usain/gov-os-worktrees/W2-98/.gov-runtime/scratch/lead/briefs/behaviours-r2.md` (C1 placeholder KPI behaviour or Fails if: text refused; C2 an unbulleted line starting with a KPI id refused, quoted; C3 placeholder owner, source and licence-or-recipe cells refused as a class, plus the "no licence found" forms). Round 2's record, with its reproductions: `/home/usain/gov-os-worktrees/W2-98/.gov-runtime/scratch/lead/rv-2.return.md` (findings F1-F3) and the probe record `/home/usain/gov-os-worktrees/W2-98/docs/probes/DAEO-wi46/PR-DAEO-wi46.md` (Round 2 table, Options).

Judge only:
1. Every round 2 reproduction of F1, F2 and F3 (from rv-2.return.md and the Round 2 table): is each now refused, with exit 1 and no PASS? List each.
2. C1-C3 as stated: does the code hold them as a class (not a list of the planted examples)? Try near variants of each kind in the class (other deferral words in the stated set with odd case, punctuation, emphasis, backticks, brackets; other `to be <word>` phrases; other lone `<...>` slots; KPI-id line shapes: indented, emphasised, `K12:`, `K2 -`). Say where a variant fails open.
3. What the fix may have broken: ordinary specs now refused (a real owner or licence, a behaviour or Fails if: sentence containing a placeholder word, a continuation line that starts with `K` and a word, prose before the first KPI, `none` in privacy and secrets), and every round 1 behaviour (B1-B6, `/home/usain/gov-os-worktrees/W2-98/.gov-runtime/scratch/lead/briefs/behaviours-r1.md`) still holding.
4. The tests: do `test_w2_98_review_r2.py`'s cases test C1-C3, and does the code pass them honestly (no special case for the planted text)?
5. The copies: `diff -r` of each `.rulesync` copy against the kernel folder is empty; the validator `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src python3 -m gov.check.skill_validator template/governance/kernel/skills/spec-writing/SKILL.md` exits 0.
Do not re-open round 2's rows (F4-F9) or anything outside the fix; name a new observation outside the fix as a row, not a failing finding.

**Probing:** run `check_spec.py` as a subprocess on files you create only under your sandbox's own `$TMPDIR`, with `PYTHONDONTWRITEBYTECODE=1`; or import it in memory **only after** `sys.dont_write_bytecode = True` (round 2's in-memory import wrote a `__pycache__/` into the skill folder and turned 14 other cases red). If the Write tool is refused in `$TMPDIR`, probe in memory as above and do not retry the refused form.

Run the suite once through the heavy slot: `cd /home/usain/gov-os-worktrees/W2-98 && TMPDIR=<your writable $TMPDIR> PYTHONDONTWRITEBYTECODE=1 PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-98/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-98 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line`. Expected: 500 passed, 2 failed (`test_the_claude_copy_matches_the_kernel_source`, `test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`: `.claude/skills/spec-writing/` is absent until the CTO's copies ACT, DEC-315, DEC-1112 (3)).

## Threat model (DEC-801, DEC-808)
Honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. Only "yes" with "fails open" or "loses work", inside the fix's scope (C1-C3 and round 2's F1-F3), fails the check. Give each finding an id (N1, N2 …), the file:line, a reproduction (input and output), and a suggested described behaviour (not code).

## Rules
Reads are open except: secrets; the held-out qualification material's contents; the hidden half of any evaluation set; never open the evaluation sets' root or any hidden or memory-verdict folder. Search with Read and Grep only, on named folders. No `gov retrieve`, no `gov context`. Write nothing in any worktree. Commands the guard can read: no here-documents, no backticks, no `bash -c`, no shell variable as a write target. **Refused twice for the same call: stop and say so.** A resource gate's refusal is a wait. Never ask or notify the owner.

## Return
One message, your last. The twelve fields first, each a labelled line; then a fenced verdict block:
```verdict
verdict: PASS | FAIL
head: f0259229e
findings: <n> (failing: <ids or none>)
```
then the round 2 reproductions with their results, the findings, the suite counts, the step 0 lines, the validator and diff outputs.
```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```
