# Independent test designer: W2-61h (DAEO-h2k3) — a red in the visible cases

You are a fresh independent test designer. Headless: only your last message is read.

## Where you work
- Your tree (write here only): /home/usain/gov-os-worktrees/W2-61h-c39-tests, branch w2/W2-61h-c39-tests (head 00a2f3e25).
- The file you may change: `fixtures/evaluation/memory-retrieval/visible/q22.yaml` (one of the ticket's own visible
  questions, q21-q24). Nothing else. Never open `/home/usain/gov-os-eval` or any hidden or retired-hidden folder.
- Use the sandbox's own `$TMPDIR`.

## The failing output (W2-61h's visible run at 00a2f3e25)
```
FAILED tests/acceptance/W2-61h/test_w2_61h_visible_new.py::test_s4_f3_every_new_visible_gold_source_resolves_at_head
E       AssertionError: q22.yaml: source entry 1: its cited lines at HEAD differ from the question's commit
E         q22.yaml: source entry 2: its cited lines at HEAD differ from the question's commit
FAILED tests/acceptance/W2-61h/test_w2_61h_visible_new.py::test_f3_each_new_visible_gold_source_holds_its_answer
E       AssertionError: q22.yaml: source 1 does not hold ['set_fault(']
E         q22.yaml: source 2 does not hold ['set_fault(']
2 failed, 19 passed, 7 skipped, 9 deselected
```
Read the tests (`tests/acceptance/W2-61h/test_w2_61h_visible_new.py`, `w2_61h_support.py`, the README's S4 row) and
q22's history (`git log -- fixtures/evaluation/memory-retrieval/visible/q22.yaml`) to find the cause and the form a fix
takes. Never change a test; never change the question's asked fact.

## Check
```
bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-61h-c39-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-61h-c39-tests/src python3 -m pytest tests/acceptance/W2-61h -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
Every pytest through heavy_slot.sh; never set `GOV_EVAL_SETS_ROOT`. A resource gate's refusal is a wait.

## Commit
Your path only; all trailers in one final paragraph (no blank line between them):
```
git -C /home/usain/gov-os-worktrees/W2-61h-c39-tests commit -m "<subject>" -m "<body: cause and fix in a line or two>" --trailer "Task: DAEO-h2k3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-828, DEC-1084" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- fixtures/evaluation/memory-retrieval/visible/q22.yaml
```
Check with `git log -1 --format='%(trailers)'` that Task, Role and Implements read as trailers.

## Rules
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
- Searching: Read and Grep only (no `gov retrieve`, no `gov context`); search again once, in other words.

## Return (your last message; nothing else is read)
Twelve labelled lines, "none" where nothing: task / status (DONE or PACKAGES) / work_completed / files_changed /
evidence / tests (counts) / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action.
Then `commits: <hash12> <subject>` and `guard_refusals: none | - <form> | <reason>`.
