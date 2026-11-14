Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-2: engineer for DAEO-0cd2 (W2-187), fix batch, profile FULL, class C2

You are a fresh engineer for ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden set, judged every week at
95 %, counts only; the weekly maintenance pass). The code is built and its independent acceptance suite
`tests/acceptance/W2-187/` is merged into your branch. Fourteen cases are red on the code's side. Make them pass,
conforming to the ticket's `## Interface` (I1-I12), which is binding; never change it. A case you cannot meet within the
Interface or your allowed paths comes back as a package (question, options with cost, recommendation, confidence, what
it blocks).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187 |
| branch | w2/W2-187 (head c0dbba313) |
| your allowed paths | src/gov/memaudit/**, src/gov/adopt/memory_sets.py, governance/project/orchestration/tools/memaudit_cron.sh, tests/unit/memaudit/**, tests/unit/adopt/test_w2_187*, docs/changes/W2-187-evidence.md |
| the ticket (the KPI lines named below and the Interface at its end) | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the acceptance suite (read it: README.md maps each KPI line to its cases; read, never edit) | tests/acceptance/W2-187/ |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Never open the
real sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`), any hidden half or memory-verdict folder; never
print a question id, question, answer, path or span of any hidden set (DEC-820).

## The failing output (tests/acceptance/W2-187 at c0dbba313)
The lead's one reading, for the two `test_s1_a_wave_0_set_...` cases: I3's "the spent check skips only that Wave 0
run's own `runs/<set>/misses.jsonl` and `miss-classes.json`" holds for the set's own run folder whether or not the Wave 0
conditions then hold; a Wave 0 set lacking its record or at another commit is then `STANDING_SPENT 0`, as I3's second
refusal says.

```
_ test_s10_a_store_three_commits_behind_is_refreshed_once_and_the_new_head_printed _

make_world = <function make_world.<locals>.make at 0x7bfbe1c4f2e0>

    def test_s10_a_store_three_commits_behind_is_refreshed_once_and_the_new_head_printed(make_world):
        world = world_of(make_world)
        head = M.behind(world, 2)  # the template's own later commit is the third
        M.plan_rebuild(world, advance_to=head)
        run = world.maintain()
        assert run.code == 0, run
        calls = M.rebuild_calls(world)
        assert len(calls) == 1 and calls[0]["argv"][:2] == ["rebuild", "--integration"] and calls[0]["argv"][2] in ("main", "refs/heads/main")
>       assert head[:12] in parse_maintain(M.maintain_line(run))["store"]
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/acceptance/W2-187/test_w2_187_s10_maintain.py:49: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

line = 'MAINTAIN 1 store refreshed e5834f264b78 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

    def parse_maintain(line: str) -> dict:
        import re
        m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                         r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                         r"6 reanchor (?P<reanchor>\d+)", line)
>       assert m, f"not the MAINTAIN line of I10: {line!r}"
               ^
E       AssertionError: not the MAINTAIN line of I10: 'MAINTAIN 1 store refreshed e5834f264b78 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

tests/acceptance/W2-187/w2_187_world.py:455: AssertionError
_ test_s10_a_failing_rebuild_keeps_the_old_store_names_the_failure_and_the_pass_still_exits_0 _

make_world = <function make_world.<locals>.make at 0x7bfbe1c4df80>

    def test_s10_a_failing_rebuild_keeps_the_old_store_names_the_failure_and_the_pass_still_exits_0(make_world):
        world = world_of(make_world)
        M.behind(world, 2)
        M.plan_rebuild(world, exit=1)
        run = world.maintain()
        assert run.code == 0, run
>       word = parse_maintain(M.maintain_line(run))["store"]
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/acceptance/W2-187/test_w2_187_s10_maintain.py:61: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

line = 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 1) 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

    def parse_maintain(line: str) -> dict:
        import re
        m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                         r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                         r"6 reanchor (?P<reanchor>\d+)", line)
>       assert m, f"not the MAINTAIN line of I10: {line!r}"
               ^
E       AssertionError: not the MAINTAIN line of I10: 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 1) 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

tests/acceptance/W2-187/w2_187_world.py:455: AssertionError
_________________ test_s10_a_store_at_the_head_is_not_rebuilt __________________

make_world = <function make_world.<locals>.make at 0x7bfbe1c4e660>

    def test_s10_a_store_at_the_head_is_not_rebuilt(make_world):
        world = world_of(make_world)
        world.relink(world.repo_git("rev-parse", "main").strip())
        run = world.maintain()
        assert run.code == 0 and M.rebuild_calls(world) == [], run
>       word = parse_maintain(M.maintain_line(run))
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/acceptance/W2-187/test_w2_187_s10_maintain.py:72: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

line = 'MAINTAIN 1 store current 345b12531809 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

    def parse_maintain(line: str) -> dict:
        import re
        m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                         r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                         r"6 reanchor (?P<reanchor>\d+)", line)
>       assert m, f"not the MAINTAIN line of I10: {line!r}"
               ^
E       AssertionError: not the MAINTAIN line of I10: 'MAINTAIN 1 store current 345b12531809 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

tests/acceptance/W2-187/w2_187_world.py:455: AssertionError
___ test_s10_a_stale_layout_is_rebuilt_once_and_named_when_the_rebuild_fails ___

make_world = <function make_world.<locals>.make at 0x7bfbe1c84220>

    def test_s10_a_stale_layout_is_rebuilt_once_and_named_when_the_rebuild_fails(make_world):
        world = world_of(make_world)
        world.relink(world.repo_git("rev-parse", "main").strip())
        M.stamp_layout(world, 1)
        M.plan_rebuild(world, fix_layout=True)
        run = world.maintain()
        assert run.code == 0 and len(M.rebuild_calls(world)) == 1, run
>       assert "stale" not in parse_maintain(M.maintain_line(run))["layout"]
                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/acceptance/W2-187/test_w2_187_s10_maintain.py:83: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

line = 'MAINTAIN 1 store current 345b12531809 2 layout rebuilt 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

    def parse_maintain(line: str) -> dict:
        import re
        m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                         r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                         r"6 reanchor (?P<reanchor>\d+)", line)
>       assert m, f"not the MAINTAIN line of I10: {line!r}"
               ^
E       AssertionError: not the MAINTAIN line of I10: 'MAINTAIN 1 store current 345b12531809 2 layout rebuilt 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

tests/acceptance/W2-187/w2_187_world.py:455: AssertionError
_ test_s10_the_new_link_findings_are_counted_first_from_the_mark_then_since_the_last_passs_commit _

make_world = <function make_world.<locals>.make at 0x7bfbe1c84680>

    def test_s10_the_new_link_findings_are_counted_first_from_the_mark_then_since_the_last_passs_commit(make_world):
        world = world_of(make_world)
        world.write_x_plan(links={"new": 3})
        first = world.maintain()
>       assert first.code == 0 and parse_maintain(M.maintain_line(first))["links"] == "3", first
                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/acceptance/W2-187/test_w2_187_s10_maintain.py:97: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

line = 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 0) 2 layout current 3 links 3 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

    def parse_maintain(line: str) -> dict:
        import re
        m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                         r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                         r"6 reanchor (?P<reanchor>\d+)", line)
>       assert m, f"not the MAINTAIN line of I10: {line!r}"
               ^
E       AssertionError: not the MAINTAIN line of I10: 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 0) 2 layout current 3 links 3 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

tests/acceptance/W2-187/w2_187_world.py:455: AssertionError
_______ test_s10_a_refused_links_check_is_none_and_never_fails_the_pass ________

make_world = <function make_world.<locals>.make at 0x7bfbe1c4cc20>

    def test_s10_a_refused_links_check_is_none_and_never_fails_the_pass(make_world):
        world = world_of(make_world)
        world.write_x_plan(links={"refuse": True})
        run = world.maintain()
>       assert run.code == 0 and parse_maintain(M.maintain_line(run))["links"] == "none", run
                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/acceptance/W2-187/test_w2_187_s10_maintain.py:114: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

line = 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 0) 2 layout current 3 links none 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

    def parse_maintain(line: str) -> dict:
        import re
        m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                         r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                         r"6 reanchor (?P<reanchor>\d+)", line)
>       assert m, f"not the MAINTAIN line of I10: {line!r}"
               ^
E       AssertionError: not the MAINTAIN line of I10: 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 0) 2 layout current 3 links none 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

tests/acceptance/W2-187/w2_187_world.py:455: AssertionError
_ test_s10_the_not_found_answers_and_second_searches_of_the_latest_standing_week_and_fresh_run_are_counted _

make_world = <function make_world.<locals>.make at 0x7bfbe1c84a40>

    def test_s10_the_not_found_answers_and_second_searches_of_the_latest_standing_week_and_fresh_run_are_counted(make_world):
        world = world_of(make_world)
        a, b = M.plant_reader_runs(world)
        run = world.maintain()
>       got = parse_maintain(M.maintain_line(run))
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/acceptance/W2-187/test_w2_187_s10_maintain.py:130: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

line = 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 0) 2 layout current 3 links 0 4 unindexed none 5 not_found 3 second 5 6 reanchor 0'

    def parse_maintain(line: str) -> dict:
        import re
        m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                         r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                         r"6 reanchor (?P<reanchor>\d+)", line)
>       assert m, f"not the MAINTAIN line of I10: {line!r}"
               ^
E       AssertionError: not the MAINTAIN line of I10: 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 0) 2 layout current 3 links 0 4 unindexed none 5 not_found 3 second 5 6 reanchor 0'

tests/acceptance/W2-187/w2_187_world.py:455: AssertionError
_ test_s10_a_changed_cited_block_is_listed_by_id_and_entry_and_a_moved_unchanged_one_is_not _

make_world = <function make_world.<locals>.make at 0x7bfbe1c84cc0>

    def test_s10_a_changed_cited_block_is_listed_by_id_and_entry_and_a_moved_unchanged_one_is_not(make_world):
        world, d2 = reanchor_world(make_world)
        run = world.maintain()
>       assert run.code == 0 and parse_maintain(M.maintain_line(run))["reanchor"] == "1", run
                                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/acceptance/W2-187/test_w2_187_s10_maintain.py:145: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

line = 'MAINTAIN 1 store current 37d7cf5f1462 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 1'

    def parse_maintain(line: str) -> dict:
        import re
        m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                         r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                         r"6 reanchor (?P<reanchor>\d+)", line)
>       assert m, f"not the MAINTAIN line of I10: {line!r}"
               ^
E       AssertionError: not the MAINTAIN line of I10: 'MAINTAIN 1 store current 37d7cf5f1462 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 1'

tests/acceptance/W2-187/w2_187_world.py:455: AssertionError
_ test_s10_a_pass_that_cannot_finish_in_time_still_exits_0_quickly_and_keeps_the_store _

make_world = <function make_world.<locals>.make at 0x7bfbe1c84fe0>

    def test_s10_a_pass_that_cannot_finish_in_time_still_exits_0_quickly_and_keeps_the_store(make_world):
        world = world_of(make_world)
        M.behind(world, 2)
        M.plan_rebuild(world, sleep=30, advance_to=world.repo_git("rev-parse", "main").strip())
        began = time.monotonic()
        run = world.maintain(env={"GOV_MEMAUDIT_MAINTAIN_TIMEOUT_S": "2"}, timeout=60)
        assert run.code == 0 and time.monotonic() - began < 25, run
>       assert parse_maintain(M.maintain_line(run))["store"].startswith("kept "), run
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/acceptance/W2-187/test_w2_187_s10_maintain.py:196: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

line = 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 124) 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

    def parse_maintain(line: str) -> dict:
        import re
        m = re.fullmatch(r"MAINTAIN 1 store (?P<store>.+?) 2 layout (?P<layout>.+?) 3 links (?P<links>\S+) "
                         r"4 unindexed (?P<unindexed>\d+) 5 not_found (?P<nf>\d+) second (?P<second>\d+) "
                         r"6 reanchor (?P<reanchor>\d+)", line)
>       assert m, f"not the MAINTAIN line of I10: {line!r}"
               ^
E       AssertionError: not the MAINTAIN line of I10: 'MAINTAIN 1 store kept 9afdddca6960 (refresh exit 124) 2 layout current 3 links 0 4 unindexed none 5 not_found 0 second 0 6 reanchor 0'

tests/acceptance/W2-187/w2_187_world.py:455: AssertionError
_ test_s1_a_wave_0_set_without_its_record_or_at_another_commit_is_spent_with_zero[no-record] _

make_world = <function make_world.<locals>.make at 0x7bfbe1c86660>
flaw = 'no-record'

    @pytest.mark.parametrize("flaw", ["no-record", "other-commit"])
    def test_s1_a_wave_0_set_without_its_record_or_at_another_commit_is_spent_with_zero(make_world, flaw):
        world = wave0_world(make_world, record=flaw != "no-record", commit="1" * 40 if flaw == "other-commit" else None)
        run = world.standing_declare(WAVE0)
>       assert run.code == 1 and run.lines == ["STANDING_SPENT 0"], run
E       AssertionError: <exit 1; stdout 'STANDING_SPENT 3
E         '; stderr ''>
E       assert (1 == 1 and ['STANDING_SPENT 3'] == ['STANDING_SPENT 0']
E        +  where 1 = <exit 1; stdout 'STANDING_SPENT 3\n'; stderr ''>.code
E         
E         At index 0 diff: 'STANDING_SPENT 3' != 'STANDING_SPENT 0'
E         Use -v to get more diff)

tests/acceptance/W2-187/test_w2_187_s1_declare.py:161: AssertionError
_ test_s1_a_wave_0_set_without_its_record_or_at_another_commit_is_spent_with_zero[other-commit] _

make_world = <function make_world.<locals>.make at 0x7bfbe1c87420>
flaw = 'other-commit'

    @pytest.mark.parametrize("flaw", ["no-record", "other-commit"])
    def test_s1_a_wave_0_set_without_its_record_or_at_another_commit_is_spent_with_zero(make_world, flaw):
        world = wave0_world(make_world, record=flaw != "no-record", commit="1" * 40 if flaw == "other-commit" else None)
        run = world.standing_declare(WAVE0)
>       assert run.code == 1 and run.lines == ["STANDING_SPENT 0"], run
E       AssertionError: <exit 1; stdout 'STANDING_SPENT 3
E         '; stderr ''>
E       assert (1 == 1 and ['STANDING_SPENT 3'] == ['STANDING_SPENT 0']
E        +  where 1 = <exit 1; stdout 'STANDING_SPENT 3\n'; stderr ''>.code
E         
E         At index 0 diff: 'STANDING_SPENT 3' != 'STANDING_SPENT 0'
E         Use -v to get more diff)

tests/acceptance/W2-187/test_w2_187_s1_declare.py:161: AssertionError
_ test_s6_fewer_than_70_live_questions_prints_standing_thin_with_the_live_count _

ran_std = <function ran_std.<locals>.get at 0x7bfbe1c4c2c0>

    def test_s6_fewer_than_70_live_questions_prints_standing_thin_with_the_live_count(ran_std):
        world, run = ran_std("thin69")
        assert run.code == 0, run
        block = world.std_digest_lines()
        assert W.digest_line(block, "QUESTIONS").startswith("QUESTIONS live 69 of 80; dropped 11"), block
        assert any("STANDING_THIN 69" in line for line in block), "in the digest"
        assert any("STANDING_THIN 69" in line for line in run.lines), "and on standard output with it"
        (line,) = world.history_kind("standing")
>       assert "STANDING_THIN 69" in json.dumps(line["word"]), line
E       AssertionError: {'at': '2026-11-10T12:00:00Z', 'audit': 'memory-standing-20261101', 'churn': 1.0, 'commit': '9afdddca6960ac14034a5f78e789432dfb7bef2f', ...}
E       assert 'STANDING_THIN 69' in '"pass"'
E        +  where '"pass"' = <function dumps at 0x7bfbe3301080>('pass')
E        +    where <function dumps at 0x7bfbe3301080> = json.dumps

tests/acceptance/W2-187/test_w2_187_s6_stale.py:78: AssertionError
_ test_s8_the_repair_opens_on_two_misses_or_on_a_miss_5_points_below_the_last_pass[open_boundary] _

ran_std = <function ran_std.<locals>.get at 0x7bfbe1c4c2c0>
name = 'open_boundary'

    @pytest.mark.parametrize("name", ["open_boundary", "open_twice"])
    def test_s8_the_repair_opens_on_two_misses_or_on_a_miss_5_points_below_the_last_pass(ran_std, name):
        world, run = ran_std(name)
        assert run.code == 0, run
        opened = [x for x in world.history_kind("repair")]
        assert len(opened) == 1 and opened[0]["word"] == "MEMORY_REPAIR open", opened
        assert (opened[0]["set"], opened[0]["week"]) == (W.STD, world.week)
>       assert "REPAIR open" in world.std_digest_lines()
E       AssertionError: assert 'REPAIR open' in ['STANDING memory-standing-20261101 week 2026-W46 commit 9afdddca6960', 'VERDICT right 75 of 80; wrong 2; not found 3;..., 'BESIDE hit5 52 of 79; first bundle 58; A1 75 A2 75: 0 gains 0 losses, exact McNemar p 1.0000', 'MAINTAIN none', ...]
E        +  where ['STANDING memory-standing-20261101 week 2026-W46 commit 9afdddca6960', 'VERDICT right 75 of 80; wrong 2; not found 3;..., 'BESIDE hit5 52 of 79; first bundle 58; A1 75 A2 75: 0 gains 0 losses, exact McNemar p 1.0000', 'MAINTAIN none', ...] = std_digest_lines()
E        +    where std_digest_lines = <w2_187_world.SW object at 0x7bfbe1c1a9f0>.std_digest_lines

tests/acceptance/W2-187/test_w2_187_s8_cadence_repair.py:199: AssertionError
_ test_s8_the_repair_opens_on_two_misses_or_on_a_miss_5_points_below_the_last_pass[open_twice] _

ran_std = <function ran_std.<locals>.get at 0x7bfbe1c4c2c0>, name = 'open_twice'

    @pytest.mark.parametrize("name", ["open_boundary", "open_twice"])
    def test_s8_the_repair_opens_on_two_misses_or_on_a_miss_5_points_below_the_last_pass(ran_std, name):
        world, run = ran_std(name)
        assert run.code == 0, run
        opened = [x for x in world.history_kind("repair")]
        assert len(opened) == 1 and opened[0]["word"] == "MEMORY_REPAIR open", opened
        assert (opened[0]["set"], opened[0]["week"]) == (W.STD, world.week)
>       assert "REPAIR open" in world.std_digest_lines()
E       AssertionError: assert 'REPAIR open' in ['STANDING memory-standing-20261101 week 2026-W46 commit 9afdddca6960', 'VERDICT right 75 of 80; wrong 2; not found 3;..., 'BESIDE hit5 52 of 79; first bundle 58; A1 75 A2 75: 0 gains 0 losses, exact McNemar p 1.0000', 'MAINTAIN none', ...]
E        +  where ['STANDING memory-standing-20261101 week 2026-W46 commit 9afdddca6960', 'VERDICT right 75 of 80; wrong 2; not found 3;..., 'BESIDE hit5 52 of 79; first bundle 58; A1 75 A2 75: 0 gains 0 losses, exact McNemar p 1.0000', 'MAINTAIN none', ...] = std_digest_lines()
E        +    where std_digest_lines = <w2_187_world.SW object at 0x7bfbe1b2d220>.std_digest_lines

tests/acceptance/W2-187/test_w2_187_s8_cadence_repair.py:199: AssertionError```

## Rules
- The one judged path stays one: never copy the reader path into a second module; `prompts.py` unchanged. `maintain` is
  never a gate (exit 0 always, 4 for usage). Counts only: no id or text of a standing set outside its run folder.
- Keep green what is green: `tests/unit/memaudit`, `tests/acceptance/W2-170`, `W2-171` (but for the two cases of the
  lead's open package P1, `test_the_ledger_events_have_item_3s_fields` and
  `test_s5_a_verdict_below_the_bar_stands_as_recorded_and_is_a_result`, which pin the old bar outside the ticket's
  paths), `W2-172` (but for two cases the test designer is fixing in parallel: `test_s6_a_log_present_but_empty_is_empty`
  and `test_f2_no_question_gold_answer_answer_or_source_path_reaches_the_digest_the_output_or_a_log`), `W2-173`, `W2-88`.
  Two W2-187 cases are also being revised by the test designer and may stay red here:
  `test_s2_a_run_writes_the_declaration_then_used_before_any_search` and
  `test_s8_the_owners_decision_id_closes_it_and_is_recorded`. Never edit `tests/acceptance/`.
- Add or update unit tests under `tests/unit/memaudit/` for what you change, and update
  `docs/changes/W2-187-evidence.md` (per KPI line, the cases and their result; the pytest summary lines).
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187/src python3 -m pytest tests/acceptance/W2-187 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same for each folder above, one folder per run; a single case: append `::<name>`. A heavy-slot or resource
  gate refusal is a wait: run again when it opens.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-187/.gov-runtime/scratch/eng/,
  run with `bash <file>` or `python3 <file>`. Literal paths only as write targets.
- **Commit** your paths only, the trailers in ONE final paragraph:
  `git commit -m "W2-187: <subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: engineer" --trailer "Implements: DEC-1179, DEC-1176, DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1092, DEC-1074, DEC-1072" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). A permission denial of a Write or a Bash form is a refusal too: do not
  redo the same edit by another form; report it.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of each folder) / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
