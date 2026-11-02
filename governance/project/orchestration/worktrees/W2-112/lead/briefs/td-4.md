The lead: the results of your suite outside the sandbox, and two fixes for you. Your first brief still holds in full: Policy 2 (c) and (d); `gov retrieve` from the W2-00-store only, with P-R1; the read refusals (DEC-849); DEC-732's `PYTHONPATH` rule; the guard's command forms; row W2-L423's rule; the scratch budget; no real model, GPU, Ollama or real lock files. Refused twice for the same call: stop and say so.

## Your helpers outside the sandbox

The red checks against the base, run outside the sandbox: on `a26963a87707`, 36 failed and 9 passed; on `faa66e1a9d98`, 41 failed and 10 passed. Both are your stated figures, with the four broken-service fakes passing on the base. No helper failure: your socket helpers work.

## Fix 1: the answer's form (moderator's decision, the CTO, P3, recorded in DEC-1036)

Two success-2 cases over-specify an internal wire detail, and the moderator decided (a): "neither P-RERANKER-1 nor the KPIs fix the answer's form; the designer revises them to accept an answer object carrying the scores, one per text, in the request's order (and, if it wants, checks `device` is present)". The cases are `test_requests_are_answered_in_arrival_order` and `test_a_request_over_the_cap_is_refused_and_the_service_keeps_answering`. Against the current code they fail only on the form. The messages, as run:

    AssertionError: request q0 was answered {'scores': [4.205566887617493, -2.1869047301328237, 7.646952698060616], 'device': 'cuda'}, not one score per text
    AssertionError: after refusing a request over the cap, the service answered {'scores': [0.8212530299797294, -9.277502397205524, 4.336268482589389, -2.6426027374240135], 'device': 'cuda'} to a normal one

Accept an answer that is a JSON object whose `scores` holds one number per text, in the request's order. Accept a bare list too if you wish. Keep every other expectation of those cases. Update the README's interface table (the "A request on it" row).

## Fix 2: the README's KPI map (no decision needed)

`gov accept` reads the map's items as `file.py`, `file.py::test_x`, `file.py::test_x[param]`, or a bare `test_x`. A bare item with a parameter, such as `test_a_service_that_does_not_answer_is_passed_over[full]` or a following `[silent]`, matches no case. Worse, an item that begins with `test_` and matches no case fails its whole line. So success-4, success-6 and success-7 report "fail" with no failed case, and the `[no-gpu]` cases count as unmapped. Rewrite every parametrized item as `file.py::test_x[param]` (one item per parameter) or as the bare function name `test_x` (all its parameters). Then check with `gov accept` that every line reports its cases and that nothing is unmapped: `TMPDIR=/tmp/gov-os-lead-W2-112 PYTHONPATH=/home/usain/gov-os-worktrees/W2-112-tests/src python3 -m gov.cli.main accept DAEO-clon --json`. In your sandbox the socket cases fail for the sandbox alone; read only the mapping: no line failing with zero failed cases, `unmapped` all zero.

## For your information (no change)

Against the current code outside the sandbox, three other cases fail on a fault in the code (the `[no-gpu]` variants of the CPU rule); the engineer fixes those. Do not change them.

## Commit

One commit, only `tests/acceptance/W2-112/`, trailers in the final block:

    git commit -m "W2-112 (DAEO-clon): the answer's form (moderator) and the README map's parametrized rows" --trailer "Task: DAEO-clon" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1036,DEC-1032" --trailer "Rewrite-Reason: DEC-1036 (moderator, P-W2-112 answer form); README map rows readable by gov accept" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

First check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file.

## Return

One message, your last, complete in itself: the twelve fields first, each as a labelled line, any payload after. Give: the commit hash (12 digits); the cases changed; `gov accept`'s per-line counts and `unmapped`; the collection line; the read refusals; your scratch figures.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Refused twice for the same call: stop and say so; no third try.
