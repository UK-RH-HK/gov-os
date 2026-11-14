Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief td-4: independent test designer for DAEO-0cd2 (W2-187), fix batch 3, profile FULL, class C2

You are a fresh independent test designer (MR-3) for ticket DAEO-0cd2 (W2-187). The suite `tests/acceptance/W2-187/`
(S1-S12, F1-F7) is merged with the engineer's code. Three cases are red on the tests' side, judged by your lead. Fix
exactly those three, as described behaviour (DEC-136), and change nothing else. If you read one differently from the
reading below, return a package (question, options with cost, recommendation, confidence, what it blocks) and do not
change it.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187-tests |
| branch | w2/W2-187-tests (now at e2ea9b0df + the engineer's code) |
| your allowed paths | tests/acceptance/W2-187/** |
| the ticket (allowed_paths at its top; S12, F7, I11 and I13 at its end) | /home/usain/gov-os-worktrees/W2-187-tests/.tickets/DAEO-0cd2.md |

You may run the engineer's code; do not read the engineer's changes under `src/gov/memaudit/`,
`src/gov/adopt/memory_sets.py` or `governance/project/orchestration/tools/memaudit_cron.sh`. Search with the Read, Grep
and Glob tools (DEC-1065); no `gov retrieve` or `gov context`. Everything planted under `tmp_path`; never the real sets
root, the real runs folder or any hidden or memory-verdict folder (DEC-820).

## The three cases and the lead's reading
1. `test_w2_187_f_guards.py::test_scope_the_branch_changes_only_the_tickets_allowed_paths_and_its_acceptance_folder`:
   its `ALLOWED` list (line ~25) lacks the two W2-171 files the CTO added to `allowed_paths` (path case W2-187-P1 (a)):
   `tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py` and `tests/acceptance/W2-171/test_w2_171_s5_misses_f2.py`.
   Add them (or read the list from the ticket's front matter, which keeps it in step); nothing else.
2. and 3. `test_w2_187_s12_push.py::test_s12_a_repository_with_no_declaration_runs_neither_step_and_says_so[unset]` and
   `[empty]` expect a no-declaration `push` to add a `cron.log` line. I13's literal "one more `cron.log` line" for the
   `PUSH none` case cannot hold with W2-172 S9's unchanged cases. There, on today's path with a started `run` and no
   declaration, the wrapper calls `push`, and the unchanged cases assert exactly one `cron.log` line and nothing written
   but `cron.log` (`tests/acceptance/W2-172/test_w2_172_s9_cron_gate.py:79-80` and `:107`). The lead's reading, sent to
   the CTO:
   - `push` writes its `cron.log` line (the six keys, step `push`) and its `DIGEST.txt` line only when a push is
     declared, that is, when the scan or the push started.
   - A no-declaration `push` prints `PUSH none: no declaration`, exits 0, calls no gitleaks, pushes nothing and **writes
     nothing**: no `cron.log` line, no digest line, no file.

   The CTO accepted this reading (an I13 note, DEC-1157 (3)) with one condition from S12's "skips both steps, named":
   the line `PUSH none: no declaration` must reach the **wrapper's own stdout** (the wrapper does not swallow it).
   Revise the two cases to assert the direct `push` run's stdout line, exit 0, no gitleaks call, nothing pushed, and
   nothing written (`cron.log` and the key folder unchanged). Also assert, through the wrapper on a cycle where an audit
   step started with no declaration, that `PUSH none: no declaration` is on the wrapper's stdout and nothing more is
   written by the push. Keep the rest of each case.

Their failing output at e2ea9b0df follows.

```
_ test_scope_the_branch_changes_only_the_tickets_allowed_paths_and_its_acceptance_folder _

    def test_scope_the_branch_changes_only_the_tickets_allowed_paths_and_its_acceptance_folder():
        """Judges the branch ``w2/W2-187`` only (the engineer's); it skips on any other branch or where ``w2/integrate`` is absent."""
        git = lambda *a: subprocess.run(["git", "-C", str(W.TREE), *a], capture_output=True, text=True)  # noqa: E731
        branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        if branch != "w2/W2-187" or git("rev-parse", "--verify", "--quiet", "w2/integrate").returncode != 0:
            pytest.skip(f"judges the branch w2/W2-187 only (this is {branch})")
        base = git("merge-base", "HEAD", "w2/integrate").stdout.strip()
        changed = [p for p in git("diff", "--name-only", f"{base}...HEAD").stdout.splitlines() if p]
        stray = [p for p in changed if not any(fnmatch.fnmatchcase(p, g) for g in ALLOWED)]
>       assert stray == [], f"changed outside the ticket's allowed paths: {stray}"
E       AssertionError: changed outside the ticket's allowed paths: ['tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py', 'tests/acceptance/W2-171/test_w2_171_s5_misses_f2.py']
E       assert ['tests/accep...misses_f2.py'] == []
E         
E         Left contains 2 more items, first extra item: 'tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py'
E         Use -v to get more diff

tests/acceptance/W2-187/test_w2_187_f_guards.py:135: AssertionError
_ test_s12_a_repository_with_no_declaration_runs_neither_step_and_says_so[unset] _

pw = <w2_187_push.PushWorld object at 0x79dc6ef813d0>, declared = None

    @pytest.mark.parametrize("declared", [None, ""], ids=["unset", "empty"])
    def test_s12_a_repository_with_no_declaration_runs_neither_step_and_says_so(pw, declared):
        run = pw.push(declared=declared)
        assert run.code == 0, run
        assert line_of(run) == "PUSH none: no declaration", run
        assert pw.fake.calls() == [], "gitleaks is not called"
        assert pw.remote_head() == pw.first, "nothing is pushed"
>       check_logged(pw, "PUSH none: no declaration", 0)

tests/acceptance/W2-187/test_w2_187_s12_push.py:180: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6ef813d0>
line = 'PUSH none: no declaration', code = 0

    def check_logged(world, line: str, code: int, *, before_cron: int = 1) -> None:
        """The line is the last of the latest digest (an older digest, and the lines before it, are untouched) and one more
        ``cron.log`` line carries the six keys and the step ``push``."""
        lines = world.digest_lines()
        assert lines[-1] == line and lines[:-1] == P.WEEK_DIGEST, lines
        assert world.digest_lines("2026-W45") == P.OLD_DIGEST, "an older digest is not the cycle's"
        cron = world.cron_lines()
>       assert len(cron) == before_cron + 1, cron
E       AssertionError: [{'at': '2026-11-16T21:00:00Z', 'due': True, 'exit': 0, 'mode': 'weekly', ...}]
E       assert 1 == (1 + 1)
E        +  where 1 = len([{'at': '2026-11-16T21:00:00Z', 'due': True, 'exit': 0, 'mode': 'weekly', ...}])

tests/acceptance/W2-187/test_w2_187_s12_push.py:52: AssertionError
_ test_s12_a_repository_with_no_declaration_runs_neither_step_and_says_so[empty] _

pw = <w2_187_push.PushWorld object at 0x79dc6ef81d90>, declared = ''

    @pytest.mark.parametrize("declared", [None, ""], ids=["unset", "empty"])
    def test_s12_a_repository_with_no_declaration_runs_neither_step_and_says_so(pw, declared):
        run = pw.push(declared=declared)
        assert run.code == 0, run
        assert line_of(run) == "PUSH none: no declaration", run
        assert pw.fake.calls() == [], "gitleaks is not called"
        assert pw.remote_head() == pw.first, "nothing is pushed"
>       check_logged(pw, "PUSH none: no declaration", 0)

tests/acceptance/W2-187/test_w2_187_s12_push.py:180: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6ef81d90>
line = 'PUSH none: no declaration', code = 0

    def check_logged(world, line: str, code: int, *, before_cron: int = 1) -> None:
        """The line is the last of the latest digest (an older digest, and the lines before it, are untouched) and one more
        ``cron.log`` line carries the six keys and the step ``push``."""
        lines = world.digest_lines()
        assert lines[-1] == line and lines[:-1] == P.WEEK_DIGEST, lines
        assert world.digest_lines("2026-W45") == P.OLD_DIGEST, "an older digest is not the cycle's"
        cron = world.cron_lines()
>       assert len(cron) == before_cron + 1, cron
E       AssertionError: [{'at': '2026-11-16T21:00:00Z', 'due': True, 'exit': 0, 'mode': 'weekly', ...}]
E       assert 1 == (1 + 1)
E        +  where 1 = len([{'at': '2026-11-16T21:00:00Z', 'due': True, 'exit': 0, 'mode': 'weekly', ...}])

tests/acceptance/W2-187/test_w2_187_s12_push.py:52: AssertionError```

## Rules
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`, a Bash timeout of 3600000 ms:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187-tests/src python3 -m pytest tests/acceptance/W2-187/test_w2_187_s12_push.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Report the summary line. The two revised push cases may stay red until the engineer's parallel batch lands (say what
  they fail on). The scope case judges only branch `w2/W2-187` and skips elsewhere; check it by reading.
- Literal paths only as write targets; if a Write into `.gov-runtime/scratch/` is refused, write no script.
- **Commit** your paths only, one commit, the trailers in ONE final paragraph:
  `git commit -m "<subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1182, DEC-1179, DEC-1156" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-187`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/` or the register.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). A permission denial of a Write is a refusal too.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then
`commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).
