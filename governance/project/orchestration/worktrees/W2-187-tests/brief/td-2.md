Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief td-2: independent test designer for DAEO-0cd2 (W2-187), fix batch, profile FULL, class C2

You are a fresh independent test designer (MR-3) for ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden set).
An earlier test designer wrote `tests/acceptance/W2-187/` and revised the W2-170, W2-171 and W2-172 files of the
ticket's paths; the engineer's code is merged with them. Four cases are red for reasons on the tests' side, judged by
your lead against the ticket's `## Interface` (I1-I12). You fix exactly those four, as described behaviour (DEC-136),
and change nothing else. The Interface is binding: if you read one of these four differently from the reading below,
say so as a package (question, options with cost, recommendation, confidence, what it blocks), and do not change it.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187-tests |
| branch | w2/W2-187-tests (now at c0dbba313: the suite, the revisions and the engineer's code merged) |
| your allowed paths | tests/acceptance/W2-187/**, tests/acceptance/W2-172/w2_172_world.py, tests/acceptance/W2-172/w2_172_git.py, tests/acceptance/W2-172/test_w2_172_s7_digest.py |
| the ticket (read it first: S2, S8, S9 and the Interface I2, I8, I12, and the CTO's routing G1) | /home/usain/gov-os-worktrees/W2-187-tests/.tickets/DAEO-0cd2.md |
| the suite's map | tests/acceptance/W2-187/README.md |

You may run the engineer's code; do not read the engineer's changes under `src/gov/memaudit/`,
`src/gov/adopt/memory_sets.py` or `governance/project/orchestration/tools/memaudit_cron.sh` (read the base 5336a6fca's
copies with `git show 5336a6fca:<path>` if you need the existing tool). Search with the Read, Grep and Glob tools; if
the first search does not answer, search once more in different words, then answer from both or say "not found"
(DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Everything planted under `tmp_path`; never the real sets
root, the real runs folder or any hidden or memory-verdict folder (DEC-820).

## The four cases and the lead's reading
1. `tests/acceptance/W2-187/test_w2_187_s2_week.py::test_s2_a_run_writes_the_declaration_then_used_before_any_search`
   asserts the week ledger's first two events are `declaration`, `used`. The fresh path's pre-flight writes a
   `preflight` ledger line (base `src/gov/memaudit/preflight.py:406`), and I2 puts the standing pre-flight's ledger in
   the week folder, so the ledger reads `preflight, declaration, used, search`. S2 asks only that `DECLARATION.json`
   comes before `USED` before the first search. Assert that order (declaration before used before the first search
   event, with only the pre-flight allowed before them), not that the ledger starts with `declaration`.
2. `tests/acceptance/W2-187/test_w2_187_s8_cadence_repair.py::test_s8_the_owners_decision_id_closes_it_and_is_recorded`
   expects a later plain `status --repair` to print `REPAIR residual DEC-1`. I8 gives a plain `status --repair` two
   outputs only: `REPAIR open since <week>` (exit 1) or `REPAIR none` (exit 0); `REPAIR residual DEC-<n>` is the
   `--residual` call's own line. After the residual, the repair is no longer open, so the later call is `REPAIR none`,
   exit 0. Keep the rest of the case (the residual line recorded in HISTORY with its decision).
3. `tests/acceptance/W2-172/test_w2_172_s6_baseline.py::test_s6_a_log_present_but_empty_is_empty` raises
   `FileNotFoundError` writing `<key folder>/indep/AUDITS.log`: the test writes the empty log through the revised
   helper's `audits_log`, and the key folder's `indep/` does not exist yet. `test_w2_172_s6_baseline.py` stays
   byte-unchanged (G1); fix it in the helper (`w2_172_world.py` or `w2_172_git.py`), e.g. by making the parent folder
   when the helper hands out the path.
4. `tests/acceptance/W2-172/test_w2_172_s7_digest.py::test_f2_no_question_gold_answer_answer_or_source_path_reaches_the_digest_the_output_or_a_log`
   looks for `indep/memaudit/<audit>/DIGEST.txt` among the files it collects, but I2 puts it at
   `indep/memaudit/<key>/<audit>/DIGEST.txt`. Revise only the path it expects (the key segment), with
   `Rewrite-Reason: DEC-1179 (5)`.

Their failing output at c0dbba313 follows.

```
_______ test_s2_a_run_writes_the_declaration_then_used_before_any_search _______

ran_std = <function ran_std.<locals>.get at 0x7bfbe1c4c2c0>

    def test_s2_a_run_writes_the_declaration_then_used_before_any_search(ran_std):
        world, run = ran_std("pass")
        assert run.code == 0, run
        declaration, used = world.std_week / "DECLARATION.json", world.std_week / "USED"
        assert declaration.is_file() and used.is_file()
        assert declaration.stat().st_mtime_ns < used.stat().st_mtime_ns, "DECLARATION.json before USED, by file time"
        first = min(c["t"] for c in world.searches())
        assert used.stat().st_mtime_ns / 1e9 <= first, "USED before the first search (the planted gov's own clock)"
        events = [e["event"] for e in world.std_ledger()]
>       assert events[:2] == ["declaration", "used"], f"the ledger's first lines: {events[:4]}"
E       AssertionError: the ledger's first lines: ['preflight', 'declaration', 'used', 'search']
E       assert ['preflight', 'declaration'] == ['declaration', 'used']
E         
E         At index 0 diff: 'preflight' != 'declaration'
E         Use -v to get more diff

tests/acceptance/W2-187/test_w2_187_s2_week.py:43: AssertionError
___________ test_s8_the_owners_decision_id_closes_it_and_is_recorded ___________

make_world = <function make_world.<locals>.make at 0x7bfbe1a2dda0>

    def test_s8_the_owners_decision_id_closes_it_and_is_recorded(make_world):
        world = repair_world(make_world)
        run = world.status_repair("--residual", "DEC-1")
        assert run.code == 0 and run.lines == ["REPAIR residual DEC-1"], run
        last = world.history()[-1]
        assert last["kind"] == "repair" and last["word"] == "MEMORY_REPAIR residual" and last["decision"] == "DEC-1", last
        after = world.status_repair()
>       assert after.code == 0 and after.lines == ["REPAIR residual DEC-1"], after
E       AssertionError: <exit 0; stdout 'REPAIR none
E         '; stderr ''>
E       assert (0 == 0 and ['REPAIR none'] == ['REPAIR residual DEC-1']
E        +  where 0 = <exit 0; stdout 'REPAIR none\n'; stderr ''>.code
E         
E         At index 0 diff: 'REPAIR none' != 'REPAIR residual DEC-1'
E         Use -v to get more diff)

tests/acceptance/W2-187/test_w2_187_s8_cadence_repair.py:249: AssertionError
=========================== 

# tests/acceptance/W2-172 at 87d6fd835
==================================
___________________ test_s6_a_log_present_but_empty_is_empty ___________________

repo = <w2_172_git.Light object at 0x7e9b4227c290>

    def test_s6_a_log_present_but_empty_is_empty(repo):
>       repo.audits_log.write_text("")

tests/acceptance/W2-172/test_w2_172_s6_baseline.py:50: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
/usr/lib/python3.12/pathlib.py:1049: in write_text
    with self.open(mode='w', encoding=encoding, errors=errors, newline=newline) as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = PosixPath('/tmp/gov-w2-187-lead/pytest-of-usain/pytest-2/test_s6_a_log_present_but_empt0/w/launch-log/indep/memaudit/repo-48b42837/indep/AUDITS.log')
mode = 'w', buffering = -1, encoding = 'locale', errors = None, newline = None

    def open(self, mode='r', buffering=-1, encoding=None,
             errors=None, newline=None):
        """
        Open the file pointed by this path and return a file object, as
        the built-in open() function does.
        """
        if "b" not in mode:
            encoding = io.text_encoding(encoding)
>       return io.open(self, mode, buffering, encoding, errors, newline)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       FileNotFoundError: [Errno 2] No such file or directory: '/tmp/gov-w2-187-lead/pytest-of-usain/pytest-2/test_s6_a_log_present_but_empt0/w/launch-log/indep/memaudit/repo-48b42837/indep/AUDITS.log'

/usr/lib/python3.12/pathlib.py:1015: FileNotFoundError
_ test_f2_no_question_gold_answer_answer_or_source_path_reaches_the_digest_the_output_or_a_log _

ran = <function ran.<locals>.get at 0x7e9b4218b2e0>

    def test_f2_no_question_gold_answer_answer_or_source_path_reaches_the_digest_the_output_or_a_log(ran):
        world, run = ran("words")
        assert_ok(run)
        words = [w.encode() for w in W171.UNIQUE]
        planted = {"question": (world.delivery / "hidden" / "q07.yaml").read_bytes(),
                   "answers": (world.run_dir / "misses.jsonl").read_bytes()}
        assert W171.QWORD.encode() in planted["question"] and W171.GWORD.encode() in planted["question"]
        assert W171.PWORD.encode() in planted["question"] and W171.AWORD.encode() in planted["answers"], \
            "the words are really planted: the question, its gold answer, its gold path and the reader's answer"
        assert W171.QWORD.encode() in planted["answers"] and W171.GWORD.encode() in planted["answers"]
        targets = {"stdout": run.out.encode(), "stderr": run.err.encode()}
        for path in sorted(world.runs.rglob("*")):
            if path.is_file():
                targets[str(path.relative_to(world.runs))] = path.read_bytes() + path.name.encode()
>       assert "indep/memaudit/%s/DIGEST.txt" % world.audit in targets
E       assert ('indep/memaudit/%s/DIGEST.txt' % 'memory-audit-20261110') in {'indep/memaudit/repo-f061f2e8/HISTORY.jsonl': b'{"audit": "memory-audit-20261110", "commit": "826c8078691ccce8c9270b0...e8c9270b0ba02b24938737abc2", "run": "20261110T130000Z-auditor-r1", "audit": "memory-audit-20261110"}\nAUDITS.log', ...}
E        +  where 'memory-audit-20261110' = <w2_172_world.World object at 0x7e9b4217f8c0>.audit

tests/acceptance/W2-172/test_w2_172_s7_digest.py:216: AssertionError
=========================== ```

## Rules
- Change only what the four cases need; every other case of the four folders keeps its bytes. Every W2-172 test file
  other than `test_w2_172_s7_digest.py` stays byte-unchanged.
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187-tests/src python3 -m pytest tests/acceptance/W2-172 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Run each of the four cases alone (append `::<name>`), then the whole `tests/acceptance/W2-172` folder, and report
  each summary line. The four must pass against the merged code; W2-172's folder must be green. A heavy-slot refusal is
  a wait; run again when it opens.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- **Commit** your paths only, the trailers in ONE final paragraph:
  `git commit -m "<subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1179, DEC-1156" [--trailer "Rewrite-Reason: DEC-1179 (5)"] --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  (one commit for the W2-187 cases; one for the W2-172 helper and s7 with the Rewrite-Reason). Never `Role: owner` or
  `Decided-by:`. No merge, no push, no edit of `.tickets/` or the register.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). A permission denial of a Write is a refusal too: do not redo it by
  another form.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
