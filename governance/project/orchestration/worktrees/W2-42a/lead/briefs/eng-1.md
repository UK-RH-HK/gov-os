# Brief: engineer, W2-42a (DAEO-03ub), fix round (review round 1's F1)

Role: engineer. Ticket DAEO-03ub (W2-42a), profile FULL, class C3.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a, branch w2/W2-42a, head 2381791e3.
Your paths: src/gov/guard/decide.py, src/gov/guard/reads.py, src/gov/guard/bash_writes.py, tests/unit/guard/test_w2_42a*,
tests/unit/guard/test_decide.py, docs/changes/W2-42a-evidence.md. Never tests/acceptance/ (the test designer's).
Commit with:
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: engineer" --trailer "Implements: DEC-1028, DEC-958" -- <your paths>`

## The failing output (and nothing else)
The acceptance suite on 2381791e3: `24 failed, 467 passed, 2 xfailed`. All 24 are in
tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py (the spellings are in
tests/acceptance/W2-42a/fixtures/f1_shell_options.json):

```
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[bash-euo-pipefail-auditor]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[bash-euo-pipefail]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[bash-e-u-o-pipefail]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[bash-eu-o-pipefail-unquoted]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[sh-o-errexit]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[bash-O-extglob]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[bash-plus-o-posix]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[bash-rcfile-f]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[cat-pipe-bash-o-pipefail]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[cat-pipe-bash-euo-pipefail]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[bash-dev-stdin]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_reading_a_heredoc_judges_its_body_as_commands[sh-dev-fd-0]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[bash-euo-pipefail-auditor]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[bash-euo-pipefail]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[bash-e-u-o-pipefail]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[bash-eu-o-pipefail-unquoted]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[sh-o-errexit]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[bash-O-extglob]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[bash-plus-o-posix]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[bash-rcfile-f]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[cat-pipe-bash-o-pipefail]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[cat-pipe-bash-euo-pipefail]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[bash-dev-stdin]
FAILED tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py::test_review_f1_a_shell_with_options_body_naming_a_hidden_file_is_refused[sh-dev-fd-0]
```

Their assertion lines:

```
E       AssertionError: no write for a shell's body (the auditor's example: no target on the review head; the base parser gave 3)
E       assert set()
E       AssertionError: no write for a shell's body (combined short options with an option value (pipefail))
E       AssertionError: no write for a shell's body (separate short options; -o's value is not a script name)
E       AssertionError: no write for a shell's body (unquoted delimiter; the body holds no expansion)
E       AssertionError: no write for a shell's body (sh with a long-named -o option)
E       AssertionError: no write for a shell's body (-O takes a shopt name as its value)
E       AssertionError: no write for a shell's body (a + option (unset) with a value)
E       AssertionError: no write for a shell's body (a long option with a separate value (f is not a script name))
E       AssertionError: no write for a shell's body (the body reaches the shell through a pipe from cat)
E       AssertionError: no write for a shell's body (through a pipe, combined options with a value)
E       AssertionError: no write for a shell's body (F4 ride-along: /dev/stdin as the script is standard input)
E       AssertionError: no write for a shell's body (F4 ride-along: /dev/fd/0 as the script is standard input)
E       AssertionError: assert '' == 'the call rea...(d), DEC-845)'
E         
E         - the call reads the hidden part of an evaluation set that measures this session, which is refused to it (DEC-820 (d), DEC-845)
```

## Done when
- The whole acceptance folder passes: `491 passed, 2 xfailed` (the 2 xfails judge the hook fixture, not the product;
  leave them). No existing case turns red: the 467 stay green.
- tests/unit/guard passes; add unit cases in tests/unit/guard/test_w2_42a_parser.py / test_w2_42a_reads.py for what
  you change.
- Fail closed: no form that gave a target or the unresolvable target before your change gives neither after it.
- One short paragraph in docs/changes/W2-42a-evidence.md naming the fix (review round 1, F1) and the new counts.

## How to run (every pytest through the heavy slot, TMPDIR your sandbox's $TMPDIR)
    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"
(mkdir -p $TMPDIR/empty-home first.) Anything longer than one line goes in a script file under $TMPDIR, run with bash
or python3; use a unique heredoc delimiter if you write one. Literal paths as write targets. Search with Read and
Grep (no gov retrieve or gov context in the sandbox); search again once in different words if the first does not
answer. Never open the evaluation sets' root or any hidden folder; never print a secret. If something is refused
twice, stop and say so; never work around a refusal. No merge in the sandbox.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (the pytest summary lines) / tests: / discoveries: /
risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers.
