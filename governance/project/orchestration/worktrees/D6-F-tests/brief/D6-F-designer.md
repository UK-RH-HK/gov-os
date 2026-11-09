Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/D6-F-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-6 part 2, item F — the independent test designer's brief: the link findings left in the tests (DAEO-q7lk)

You are an independent test designer working under **W2-129** (`.tickets/DAEO-q7lk.md`, the link check). This is D-6
part 2's item F (`governance/project/orchestration/packages/LIFT-1/D6-PART2.md`; LINK-INTEGRITY §7's "D-6: the code
and test findings"; DEC-1109 (2)).

`gov links --all` on `w2/integrate` names these findings in the tests, all owned by the independent test designer:
- **45 ENFORCES_SUPERSEDED** in 24 files:
  - DEC-798 → DEC-1033: 39 (23 in READMEs, the rest in `.py` comments, docstrings and code);
  - DEC-876 → DEC-880: 4;
  - DEC-002 → DEC-058: 2 (docstrings in `tests/acceptance/W1-10/test_w1_10_register.py`);
  - 3 of the 45 are in `tests/unit/` (`tests/unit/retrieval/test_semantic_query_vector.py`,
    `tests/unit/semantic/test_semantic.py`).
- **60 UNKNOWN_ID** in comments and docstrings of acceptance tests: planted ids such as W1-90 (24), W2-941, DEC-000
  and DEC-9999. They are mostly in W1-02, W2-141, W2-20, W1-50, W2-72 and W1-30.

To get the list, run `PYTHONPATH=<your tree>/src python3 -m gov.cli.main links --all --json` in your worktree. It
writes only its mark.

## What to do
1. **For each ENFORCES_SUPERSEDED,** read the line and the two register entries (`docs/DECISION_REGISTER.md`: DEC-798
   and DEC-1033, DEC-876 and DEC-880, DEC-002 and DEC-058). Classify it as one of:
   - **(h) history:** the line records why a test was written or rewritten (a `Rewrite-Reason`, a dated note, a
     README history line). Do not edit it; put it on a **Kept list** in your return: path, line, one-line reason.
     The CTO records `**Kept:**` lines in the register (DEC-866's form).
   - **(c) current rule, old citation:** the test checks behaviour that the newer decision keeps. Change the citation
     to the newer decision, comment or docstring only, with `Rewrite-Reason: DEC-1109 (2)` in the commit body and a
     one-line note in that folder's README.
   - **(r) a real finding:** the test enforces behaviour that the newer decision changed. Do not edit it. Report it
     with what the newer decision says.
2. **For each UNKNOWN_ID** in a comment or docstring, reword the comment so the planted id no longer stands as a
   citation:
   - name the constant that holds it (for example "the planted `TEST_FILE`'s ticket"), or
   - write the id inside a string-literal example in the code.

   Change no test's behaviour, only comments and docstrings. Where a docstring must name the planted id, say so in
   your return instead.
3. Leave the 3 unit-file findings as they are; classify them in your return only.

## Verify
- `gov links --all` before and after: the test designer's counts, with the remainder named.
- A scoped run of every acceptance folder you touched, through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=<your tree>/src`, a scratch HOME with `.local` linked in, and `PYTHONUSERBASE=/home/usain/.local`. The
  results must be the same as before your edits; compare on the unchanged tree for any red.

## Where you work
- `/home/usain/gov-os-worktrees/D6-F-tests`, branch `w2/D6-F-tests`, from `w2/integrate`.
- You write `tests/acceptance/**` only, comments, docstrings and READMEs. Never `src/`, `tests/unit/`, `.tickets/` or
  the register.
- **Your record:** your session's final message.

## Rules
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- No GPU, network or installs.
- **DEC-1080:** one simple command per Bash call. **Search again once (DEC-1092 (1)).** Waits by pid only.
- **Commit** on `w2/D6-F-tests` with
  `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1109" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  and `Rewrite-Reason: DEC-1109 (2)` in the body.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md`;
- the classification table (path:line, code, class h/c/r, action);
- **the Kept list** (path, the old id, reason);
- the (r) findings;
- `gov links` counts before and after;
- the scoped runs' counts;
- the commit.
