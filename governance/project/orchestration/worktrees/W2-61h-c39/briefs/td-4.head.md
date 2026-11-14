# Independent test designer: W2-61h (DAEO-h2k3) — the S4/F3 check judged at each source's own commit (DEC-1178 (1))

You are a fresh independent test designer. Headless: only your last message is read.

## Where you work
- Your tree (write here only): /home/usain/gov-os-worktrees/W2-61h-c39-tests, branch w2/W2-61h-c39-tests (at w2/integrate e0381969c).
- Files you may change: `tests/acceptance/W2-61h/w2_61h_support.py`, `tests/acceptance/W2-61h/test_w2_61h_hidden_form.py`,
  `tests/acceptance/W2-61h/test_w2_61h_visible_new.py`, `tests/acceptance/W2-61h/README.md`. Nothing else
  (not `test_w2_61h_families.py`, not `tests/optin-lifted*.txt`, not the question files).
- Scratch: the sandbox's own `$TMPDIR` for every planted repository and planted sets root.

## The decision you implement
DEC-1178 (1) (`docs/DECISION_REGISTER.md`, grep `### DEC-1178`, read item (1) only) and the ticket's reworded S4 and F3
lines (`.tickets/DAEO-h2k3.md` `kpis:`, the 4th success line and the 4th failure line; also its last paragraph,
"Reopened 2026-11-14"). The background: `governance/project/orchestration/packages/P-W2-61H-HEAD-1.md`.

**Why:** the owner's operator's walled run of 2026-11-14 gave 6 passed, 1 failed: one hidden question's cited lines
changed at HEAD; six others whose blocks moved unchanged had been re-anchored by hand before. `source_faults()`
(`w2_61h_support.py:204-246`) judges every line-cited block against **HEAD**, so ordinary work on a cited file turns the
check red. W2-134 (closed) now re-anchors in memory when the measure runs (`tests/acceptance/W2-134/README.md` states
the rule: the block read at the source's own commit, found once at the measured root).

## The revision (hidden and visible cases alike)
1. **Each gold source is judged at its own commit** (the source alternative's `commit`, else the question's `commit`):
   the path is a file there, and its heading or lines are a span there (the measure's span rule, `span_of`). For the
   visible q21-q24 the span at the own commit also holds the designer's anchor (`ANCHORS`); for the hidden half, that
   the span holds the answer is the operator's cross-check, not a test.
2. **At HEAD, a cited block that moved unchanged is no fault**: the own commit's block is found again at HEAD (at the
   same lines, or exactly once elsewhere, as W2-134's measure and `repin_gold.py` find it).
3. **A cited block whose lines changed at HEAD is listed by question id and entry number only.** Never failed; never
   blocks a close. The list is the case's output: file names (or ids) and entry numbers only, never a question, an
   answer, a path, a category or span text. Your call, stated in the README: what counts as "changed" (the block
   found nowhere at HEAD, found more than once, the path no longer a file at HEAD, a heading no longer found at HEAD;
   say which and why), and how the list is shown in a passing run so the owner's operator's record can quote it (a
   warning in the default summary, or printed with a flag named in the README's walled command; the list must be
   visible in the command's own output with no extra file written).
4. **A source that does not hold its answer at its own commit stays red** (path not a file there, span does not
   resolve there; for q21-q24 also the anchor missing from the span there), naming the file name and entry number only.

Everything else in both modules keeps its point and its failure wording rules (`_fail`, untraced, file names and
entry numbers only). **Keep every existing test function's name** (the ticket's KPI lines and
`governance/project/orchestration/packages/` cite them; `tests/optin-lifted-breadth.txt` holds
`rep: tests/acceptance/W2-61h/test_w2_61h_visible_new.py`, so in the full run **only the first row of a parametrised
function runs**). You may add functions; make each proof that must run in the full run a single non-parametrised
case (or put the row that matters first). The old message about "a re-anchor: repin_gold.py --write" goes: a moved
block is no longer a fault. The support functions that read git may take a `root` argument (default `REPO_ROOT`) so the
same rule runs on a planted repository.

## Prove it on planted data only
- **In the visible module, an always-run case** (no sets root, no hidden file) builds in `tmp_path` a planted git
  repository with two commits and a planted folder of question YAMLs (the "planted sets root") holding:
  (a) a source whose block moved unchanged at HEAD; (b) a source whose lines changed at HEAD; (c) a source that
  never held its answer at its own commit; (d) a control. Expected: (a) passes, not listed; (b) passes and is listed by
  id and entry number; (c) is red, naming file name and entry number only (assert the message holds no planted
  question, answer, path or span text); (d) passes, not listed. It must judge with the same support function the real
  hidden and visible cases use.
- **The hidden-form module against a throwaway sets root under `$TMPDIR`** (planted questions in the form the module
  expects, citing real commits and real non-evaluation files of this repository, e.g. a block of a visible question's
  source that moved or changed since; never anything from `/home/usain/gov-os-eval`): show its S4 case gives (a) pass,
  (b) pass with the list, (c) red with file name and entry number only, (d) pass. Other hidden cases may be red on a
  synthetic plant for reasons of their own (count, S5); report the S4 case's outcomes. Also show the module still skips
  without `GOV_EVAL_SETS_ROOT` and under `GOV_ROLE=engineer`.
- **The visible module at HEAD** (q21-q24 against the repository) must pass in an ordinary run.

## Check your change
Every pytest through heavy_slot.sh (a resource gate's refusal is a wait, not a refusal):
```
mkdir -p /home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home
cd /home/usain/gov-os-worktrees/W2-61h-c39-tests && bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39-tests/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
For the throwaway sets root run, add `GOV_EVAL_SETS_ROOT=<your $TMPDIR root>` and `-rA` (or your list's flag) and run
only `tests/acceptance/W2-61h/test_w2_61h_hidden_form.py`. Report counts and outcomes only.

## README
Update the KPI map (S4 and F3 rows: the new rule, the list, where the list shows), the "How to run" walled command
(the form the owner's operator runs: `env -u GOV_ROLE -u GOV_TICKET GOV_EVAL_SETS_ROOT=<root> python3 -m pytest
tests/acceptance/W2-61h/test_w2_61h_hidden_form.py -p no:cacheprovider <flags>`), and add a dated section "DEC-1178 (1):
judged at each source's own commit" recording the planted proofs by outcome only. Correct any older sentence the
revision makes false (e.g. "the measure ... re-anchors nothing").

## Commit
Your paths only; trailers in one final paragraph (no blank line between them):
```
git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests commit -m "<subject>" --trailer "Rewrite-Reason: DEC-1178 (1)" --trailer "Task: DAEO-h2k3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-828, DEC-820, DEC-1084, DEC-1178" -- tests/acceptance/W2-61h/w2_61h_support.py tests/acceptance/W2-61h/test_w2_61h_hidden_form.py tests/acceptance/W2-61h/test_w2_61h_visible_new.py tests/acceptance/W2-61h/README.md
```
Check with `git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests log -1 --format='%(trailers)'` that all four read as trailers.

## Rules
- **Never open `/home/usain/gov-os-eval` or any hidden, retired-hidden or memory-verdict folder; read no hidden content.**
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- No hidden question, answer or gold path in any commit message, file, log or your return.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context` in the sandbox); search again once, in other words.
- You may read `src/gov/retrieval/measure.py` and `tests/acceptance/W2-134/` for the span and re-anchor rules.

## Return (your last message; nothing else is read)
Twelve labelled lines, "none" where nothing: task / status (DONE or PACKAGES) / work_completed / files_changed /
evidence / tests (the visible run's counts; the planted case's four outcomes; the throwaway-root S4 outcomes; the skip
checks) / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then
`commits: <hash12> <subject>` and `guard_refusals: none | - <form> | <reason>`.
PACKAGES: each as question, options with cost, recommendation, confidence, what it blocks.

## The ticket's context packet (gov context DAEO-h2k3 --role independent-test-designer --budget 36000)

```
