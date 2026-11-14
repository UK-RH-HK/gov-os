Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-4: engineer for DAEO-0cd2 (W2-187), fix batch 3, profile FULL, class C2

You are a fresh engineer for ticket DAEO-0cd2 (W2-187). The code is built and its acceptance suite
`tests/acceptance/W2-187/` (S1-S12, F1-F7) is merged into your branch. Eleven S12 cases are red on the code's side. Make
them pass, conforming to the ticket's Interface (I1-I13, binding) as your lead reads it below. A case you cannot meet
within it or your allowed paths comes back as a package (question, options with cost, recommendation, confidence, what
it blocks).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187 |
| branch | w2/W2-187 (head e2ea9b0df) |
| your allowed paths | src/gov/memaudit/**, src/gov/adopt/memory_sets.py, governance/project/orchestration/tools/memaudit_cron.sh, tests/unit/memaudit/**, tests/unit/adopt/test_w2_187*, docs/changes/W2-187-evidence.md |
| the ticket (S12, F7, I11 and I13 at its end) | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the acceptance cases (read, never edit) | tests/acceptance/W2-187/test_w2_187_s12_push.py, w2_187_push.py, README.md |
| the unchanged W2-172 S9 cases that must stay green | tests/acceptance/W2-172/test_w2_172_s9_cron_gate.py, py_shim.py |

Search with the Read, Grep and Glob tools (DEC-1065); no `gov retrieve` or `gov context`. Never open the real sets root,
the real runs folder, any hidden or memory-verdict folder; never print any hidden set's ids or text (DEC-820).

## The lead's reading of I13 (sent to the CTO; I13 against W2-172 S9's unchanged cases)
1. **`push` itself** writes its `cron.log` line (`<key folder>/cron.log`, else the runs folder's, the same six keys as
   the wrapper's lines, the step named `push`) and its `DIGEST.txt` last line, **only when a push is declared**, that is,
   when the scan or the push started. The wrapper no longer writes the push's `cron.log` line, so there is never a
   double line.
2. **A no-declaration `push`** prints `PUSH none: no declaration`, exits 0, calls no gitleaks and writes nothing.
3. **The wrapper calls `push`** as its last step after any started audit step, on the live path **and today's path**
   (no live set), declared or not. Its exit stays the last audit step's, so W2-172 S9's "the wrapper exits with run's
   code" holds.

The CTO accepted this reading (an I13 note, DEC-1157 (3)) with one condition: the no-declaration line
`PUSH none: no declaration` must reach the **wrapper's own stdout** (the wrapper must not swallow it), so the cron's
output names the skip.

The test designer is revising the two no-declaration cases to (2) in parallel; they may stay red here until merged.

## The failing output (tests/acceptance/W2-187 at e2ea9b0df)
```
==================================
_ test_s12_the_push_line_is_the_last_line_of_the_latest_digest_and_cron_log_gains_one_push_line _

pw = <w2_187_push.PushWorld object at 0x79dc6f4a2690>

    def test_s12_the_push_line_is_the_last_line_of_the_latest_digest_and_cron_log_gains_one_push_line(pw):
        run = pw.push(declared=pw.declare())
        assert run.code == 0, run
>       check_logged(pw, line_of(run), 0)

tests/acceptance/W2-187/test_w2_187_s12_push.py:84: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6f4a2690>
line = 'PUSH pushed /tmp/gov-w2-187-lead/pytest-of-usain/pytest-3/test_s12_the_push_line_is_the_0/pw/remote.git main 6177c3c8f5de'
code = 0

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
_ test_s12_a_scan_with_findings_blocks_the_push_names_the_count_and_never_the_secret[1] _

pw = <w2_187_push.PushWorld object at 0x79dc6f480a70>, k = 1

    @pytest.mark.parametrize("k", [1, 3])
    def test_s12_a_scan_with_findings_blocks_the_push_names_the_count_and_never_the_secret(pw, k):
        """Exit 1 and ``k`` report entries each holding the planted secret (the fake also prints it on its stdout and stderr)."""
        pw.fake.plan(entries=k, exit=1)
        run = pw.push(declared=pw.declare())
        assert run.code == 1, run
        assert line_of(run) == f"PUSH blocked: findings {k}", run
        assert pw.remote_head() == pw.first, "the remote is unchanged"
        (call,) = pw.fake.calls()
        assert not os.path.exists(call["path"]), "the report is deleted"
        assert P.no_stray_files(pw.tmp) == []
        nothing_leaked(pw, run)
>       check_logged(pw, f"PUSH blocked: findings {k}", 1)

tests/acceptance/W2-187/test_w2_187_s12_push.py:128: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6f480a70>
line = 'PUSH blocked: findings 1', code = 1

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
_ test_s12_a_scan_with_findings_blocks_the_push_names_the_count_and_never_the_secret[3] _

pw = <w2_187_push.PushWorld object at 0x79dc6f4837a0>, k = 3

    @pytest.mark.parametrize("k", [1, 3])
    def test_s12_a_scan_with_findings_blocks_the_push_names_the_count_and_never_the_secret(pw, k):
        """Exit 1 and ``k`` report entries each holding the planted secret (the fake also prints it on its stdout and stderr)."""
        pw.fake.plan(entries=k, exit=1)
        run = pw.push(declared=pw.declare())
        assert run.code == 1, run
        assert line_of(run) == f"PUSH blocked: findings {k}", run
        assert pw.remote_head() == pw.first, "the remote is unchanged"
        (call,) = pw.fake.calls()
        assert not os.path.exists(call["path"]), "the report is deleted"
        assert P.no_stray_files(pw.tmp) == []
        nothing_leaked(pw, run)
>       check_logged(pw, f"PUSH blocked: findings {k}", 1)

tests/acceptance/W2-187/test_w2_187_s12_push.py:128: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6f4837a0>
line = 'PUSH blocked: findings 3', code = 1

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
_ test_s12_a_scan_that_fails_or_cannot_run_blocks_the_push_and_is_named_by_one_reason_word[exit-2] _

pw = <w2_187_push.PushWorld object at 0x79dc6ef80680>
how = <function exit_two at 0x79dc6f351800>

    @pytest.mark.parametrize("how", [exit_two, no_binary_by_flag, no_binary_on_path, too_slow],
                             ids=["exit-2", "missing-by-flag", "missing-on-path", "timeout"])
    def test_s12_a_scan_that_fails_or_cannot_run_blocks_the_push_and_is_named_by_one_reason_word(pw, how):
        run, seconds = how(pw)
        assert run.code == 1, run
        assert re.fullmatch(r"PUSH blocked: scan failed \S+", line_of(run)), run
        assert pw.remote_head() == pw.first, "the remote is unchanged"
        if seconds is not None:
            assert seconds < 60, f"a scan past GOV_MEMAUDIT_SCAN_TIMEOUT_S=2 was waited for {seconds:.0f} s"
        nothing_leaked(pw, run)
>       check_logged(pw, line_of(run), 1)

tests/acceptance/W2-187/test_w2_187_s12_push.py:161: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6ef80680>
line = 'PUSH blocked: scan failed exit', code = 1

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
_ test_s12_a_scan_that_fails_or_cannot_run_blocks_the_push_and_is_named_by_one_reason_word[missing-by-flag] _

pw = <w2_187_push.PushWorld object at 0x79dc6f482180>
how = <function no_binary_by_flag at 0x79dc6f3518a0>

    @pytest.mark.parametrize("how", [exit_two, no_binary_by_flag, no_binary_on_path, too_slow],
                             ids=["exit-2", "missing-by-flag", "missing-on-path", "timeout"])
    def test_s12_a_scan_that_fails_or_cannot_run_blocks_the_push_and_is_named_by_one_reason_word(pw, how):
        run, seconds = how(pw)
        assert run.code == 1, run
        assert re.fullmatch(r"PUSH blocked: scan failed \S+", line_of(run)), run
        assert pw.remote_head() == pw.first, "the remote is unchanged"
        if seconds is not None:
            assert seconds < 60, f"a scan past GOV_MEMAUDIT_SCAN_TIMEOUT_S=2 was waited for {seconds:.0f} s"
        nothing_leaked(pw, run)
>       check_logged(pw, line_of(run), 1)

tests/acceptance/W2-187/test_w2_187_s12_push.py:161: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6f482180>
line = 'PUSH blocked: scan failed missing', code = 1

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
_ test_s12_a_scan_that_fails_or_cannot_run_blocks_the_push_and_is_named_by_one_reason_word[missing-on-path] _

pw = <w2_187_push.PushWorld object at 0x79dc6f4a0b60>
how = <function no_binary_on_path at 0x79dc6f351940>

    @pytest.mark.parametrize("how", [exit_two, no_binary_by_flag, no_binary_on_path, too_slow],
                             ids=["exit-2", "missing-by-flag", "missing-on-path", "timeout"])
    def test_s12_a_scan_that_fails_or_cannot_run_blocks_the_push_and_is_named_by_one_reason_word(pw, how):
        run, seconds = how(pw)
        assert run.code == 1, run
        assert re.fullmatch(r"PUSH blocked: scan failed \S+", line_of(run)), run
        assert pw.remote_head() == pw.first, "the remote is unchanged"
        if seconds is not None:
            assert seconds < 60, f"a scan past GOV_MEMAUDIT_SCAN_TIMEOUT_S=2 was waited for {seconds:.0f} s"
        nothing_leaked(pw, run)
>       check_logged(pw, line_of(run), 1)

tests/acceptance/W2-187/test_w2_187_s12_push.py:161: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6f4a0b60>
line = 'PUSH blocked: scan failed missing', code = 1

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
_ test_s12_a_scan_that_fails_or_cannot_run_blocks_the_push_and_is_named_by_one_reason_word[timeout] _

pw = <w2_187_push.PushWorld object at 0x79dc6efa51f0>
how = <function too_slow at 0x79dc6f3519e0>

    @pytest.mark.parametrize("how", [exit_two, no_binary_by_flag, no_binary_on_path, too_slow],
                             ids=["exit-2", "missing-by-flag", "missing-on-path", "timeout"])
    def test_s12_a_scan_that_fails_or_cannot_run_blocks_the_push_and_is_named_by_one_reason_word(pw, how):
        run, seconds = how(pw)
        assert run.code == 1, run
        assert re.fullmatch(r"PUSH blocked: scan failed \S+", line_of(run)), run
        assert pw.remote_head() == pw.first, "the remote is unchanged"
        if seconds is not None:
            assert seconds < 60, f"a scan past GOV_MEMAUDIT_SCAN_TIMEOUT_S=2 was waited for {seconds:.0f} s"
        nothing_leaked(pw, run)
>       check_logged(pw, line_of(run), 1)

tests/acceptance/W2-187/test_w2_187_s12_push.py:161: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6efa51f0>
line = 'PUSH blocked: scan failed timeout', code = 1

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
_ test_s12_a_remote_that_refuses_the_push_is_exit_2_and_gits_output_is_kept_in_a_0600_file_never_printed _

pw = <w2_187_push.PushWorld object at 0x79dc6ef82f90>

    def test_s12_a_remote_that_refuses_the_push_is_exit_2_and_gits_output_is_kept_in_a_0600_file_never_printed(pw):
        P.reject_pushes(pw.remote)
        before = pw.key_files()
        run = pw.push(declared=pw.declare())
        assert run.code == 2, run
        assert line_of(run) == "PUSH failed: git push exit 1", run
        assert len(pw.fake.calls()) == 1, "the scan was clean and ran once"
        assert pw.remote_head() == pw.first
        for text in (run.out, run.err):
            assert P.HOOK not in text and "remote:" not in text and "error:" not in text and "hint:" not in text, text
        kept = [Path(p) for p in pw.key_files() - before if P.HOOK in Path(p).read_text(errors="replace")]
        assert len(kept) == 1, "git's own output is in one new file of the key folder"
        assert (kept[0].stat().st_mode & 0o777) == 0o600
>       check_logged(pw, "PUSH failed: git push exit 1", 2)

tests/acceptance/W2-187/test_w2_187_s12_push.py:197: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6ef82f90>
line = 'PUSH failed: git push exit 1', code = 2

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
_ test_s12_a_declared_remote_that_does_not_exist_is_a_failed_push_not_a_crash __

pw = <w2_187_push.PushWorld object at 0x79dc6f1c0080>

    def test_s12_a_declared_remote_that_does_not_exist_is_a_failed_push_not_a_crash(pw):
        before = pw.key_files()
        run = pw.push(declared=pw.declare(pw.base / "no-such-remote.git"))
        assert run.code == 2, run
        assert line_of(run) == "PUSH failed: git push exit 128", run
        assert "fatal" not in run.err and "does not appear" not in run.err and "does not appear" not in run.out
        new = [Path(p) for p in pw.key_files() - before if (Path(p).stat().st_mode & 0o777) == 0o600 and Path(p).stat().st_size]
        assert new, "git's output is kept in a 0600 file of the key folder"
>       check_logged(pw, "PUSH failed: git push exit 128", 2)

tests/acceptance/W2-187/test_w2_187_s12_push.py:208: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

world = <w2_187_push.PushWorld object at 0x79dc6f1c0080>
line = 'PUSH failed: git push exit 128', code = 2

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
_ test_s12_with_no_live_set_todays_path_also_ends_with_the_push_after_its_run __

make_world = <function make_world.<locals>.make at 0x79dc6ef86020>

    def test_s12_with_no_live_set_todays_path_also_ends_with_the_push_after_its_run(make_world):
        world, done, _ = cycle(make_world, plan(live=False, standing=True))
>       assert keys(world) == ["standing live", "due", "run", "push"], (keys(world), done.stderr)
E       AssertionError: (['standing live', 'due', 'run'], '')
E       assert ['standing li... 'due', 'run'] == ['standing li...'run', 'push']
E         
E         Right contains one more item: 'push'
E         Use -v to get more diff

tests/acceptance/W2-187/test_w2_187_s12_push.py:297: AssertionError
=========================== ```

## Rules
- Counts only (F7): no finding's text, secret, match or line in any output, log or digest; git's own output only in the
  0600 file in the key folder, never printed. `push.py` stays the only gitleaks caller. `say` the only printer.
- Keep green: `tests/unit/memaudit`, `tests/unit/adopt/test_w2_187*`, `tests/acceptance/W2-187` (but the two
  no-declaration cases and `test_scope_...`, which the test designer is revising), `tests/acceptance/W2-172` (whole,
  unchanged files), `tests/acceptance/W2-171`.
- Update the unit tests and `docs/changes/W2-187-evidence.md` (the reading above, under S12).
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`, a Bash timeout of 3600000 ms each:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest tests/acceptance/W2-187 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same per folder above. A heavy-slot refusal is a wait.
- Literal paths only as write targets; if a Write into `.gov-runtime/scratch/` is refused, write no script.
- **Commit** your paths only, the trailers in ONE final paragraph:
  `git commit -m "W2-187: <subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: engineer" --trailer "Implements: DEC-1182, DEC-1179, DEC-1101" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another form (DEC-1142 (9)). A permission denial of a Write or a Bash form is a refusal too: report it.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence (the pytest summary lines) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form |
the hook's reason | true or false-positive).
