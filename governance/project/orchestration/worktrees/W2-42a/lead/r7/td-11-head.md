# Brief: independent test designer, W2-42a (DAEO-03ub), R4/R5 second batch: a blob ref whose path cannot be placed, and git's own --output write (DEC-1157 (12), DEC-1180 (4); the failure line F3)

Role: independent-test-designer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh test designer: you write
tests from the behaviour stated here (DEC-136); you read no fix. The behaviour comes from the lead's probe of the
head (each form checked through `decide()` on a planted repository).
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a-tests, branch w2/W2-42a-tests, head eca7a70176de.
Your paths: tests/acceptance/W2-42a/** only. Add a NEW file tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py
and update tests/acceptance/W2-42a/README.md (its map) in the SAME commit. Do not edit the other test files, the
fixtures or the support module (copy what you need; tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs.py has a
`planted` repository fixture and helpers you may copy).
Commit with (all trailers in ONE final paragraph, no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1157 (12), W2-42a R4 R5" --trailer "Implements: DEC-1157, DEC-1180, DEC-1128, DEC-1133" -- tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py tests/acceptance/W2-42a/README.md`

## The KPI lines (the ticket's)
- **S12 (R4):** `git diff REV:PATH REV:PATH` (one or both sides) and `git show REV:PATH` are judged as reads of those
  paths, under the read rules the path names; a revision word that names no commit, tree or blob is refused, not
  passed.
- **F3:** a call refused today that the fix lets through although it writes into a walled path or reads a refused one
  (a fail-open): never.

## The product under test
`decide()` in `src/gov/guard/decide.py`, called as test_w2_42a_r4_blob_refs.py calls it, on a planted repository
(`git init` under `tmp_path`, one commit) with an evaluation set measuring the roles research and engineer whose
hidden part is `fixtures/evaluation/<set>/hidden/**` holding `q01.txt`, visible files `docs/a.md`, `docs/b.md`, and
`tests/acceptance/X/` present. The engineer's ticket's allowed paths do not hold `tests/acceptance/`. Name the ids with
`git rev-parse` in the fixture: SUB = `HEAD:fixtures/evaluation/<set>` (a subtree's id), HTREE =
`HEAD:fixtures/evaluation/<set>/hidden`, BLOB = `HEAD:fixtures/evaluation/<set>/hidden/q01.txt` (a blob's id).

## The behaviour to pin
**1. A revision-colon-path whose path the guard cannot place is refused (fail-open at eca7a70176de, refused on the
base d9e7dc859).** In `<rev>:<path>`, the path starts at the top of the tree `<rev>` names. When `<rev>` is a commit
(HEAD, a branch, a hash of a commit, `HEAD~1`) or empty (the index: `:<path>`, `:0:<path>`), that is the repository's
top and the path is judged as a read of that path (the S12 cases already pin this). When `<rev>` names a tree that is
not the commit's top (a subtree's id, or any revision that does not name a commit), the path does not name where the
blob lives, so it cannot be judged against the parts refused to the session: for a session with a refused part
(research or engineer here) it is refused, by a ruled refusal (a deny whose reason is a rule's text, not an exception,
not the catch-all "the guard could not work out the reads"). Forms, each for research and engineer, assert deny:
`git diff SUB:hidden/q01.txt HEAD:docs/a.md`, `git diff HEAD:docs/a.md SUB:hidden/q01.txt`,
`git diff HTREE:q01.txt HEAD:docs/a.md`, `git show SUB:hidden/q01.txt` and `git show HTREE:q01.txt` (these two
allowed on the base too: a fail-open older than this round), `git cat-file -p SUB:hidden/q01.txt` and
`git cat-file blob HTREE:q01.txt` (allowed on the base too). Each of these shows the hidden file's text in real git:
check that in `$TMPDIR` first and say so.

**2. An object named by its id alone that git shows as a file's text is refused to a session with a refused part, as
`git show BLOB` already is.** `git cat-file blob BLOB`, `git cat-file -p BLOB` (allowed on the base: an older
fail-open): deny, ruled. Guards that must stay allowed (check them green at your head; leave out any that is not and
say so): `git cat-file -t BLOB`, `git cat-file -s BLOB`, `git cat-file -e BLOB` (no file text), `git cat-file -p HEAD`
(a commit object), `git show HEAD:docs/a.md`, `git diff HEAD:docs/a.md HEAD:docs/b.md`, `git cat-file -p HEAD:docs/a.md`.

**3. git's own `--output=<file>` (and `--output <file>`) writes that file.** git diff, git show and git log take
`--output`; the file is written by git. For the engineer, each form below writes `tests/acceptance/X/zz.txt` and is
refused (the Bash write refusal): `git diff HEAD:docs/a.md HEAD:docs/b.md --output=tests/acceptance/X/zz.txt`,
`git diff --output=tests/acceptance/X/zz.txt HEAD:docs/a.md HEAD:docs/b.md` (both refused on the base by the revision
fault, allowed at eca7a70176de: the fail-open of this round), `git diff --output tests/acceptance/X/zz.txt HEAD~0 HEAD`,
`git diff --output=tests/acceptance/X/zz.txt HEAD~0 HEAD`, `git show --output=tests/acceptance/X/zz.txt HEAD:docs/a.md`,
`git log -p -1 --output=tests/acceptance/X/zz.txt` (allowed on the base: older fail-opens), also after `git -C <root>`
and after a `cd tests && …` with the relative path. Check in real git that each writes the file (and say if one does
not; leave such a form out). A guard: `git diff --output=<a path the engineer may write> HEAD~0 HEAD` stays allowed
(choose a path in the planted ticket's allowed paths; leave it out if the planted project gives the engineer none,
and say so).

Name tests so they state the behaviour (`test_r4_…` for 1 and 2, `test_r45_failure_…` for each fail-open in 1 and 3,
guards `test_r4_…_stays_allowed`). No xfail marks. Planted repositories only under `tmp_path`; git calls with
`-c user.name=t -c user.email=t@t -c commit.gpgsign=false`. Never read, list or name `~/.gov-os/guard-calls`.

## The README map (same commit)
A file-list entry for the new file (td-11, 2026-11-14, R4 R5 second batch, Rewrite-Reason DEC-1157 (12), W2-42a R4
R5); each test by full `file.py::test_name` under its KPI row (the `test_r4_*` under S12, the `test_r45_failure_*`
under F3), and a round-table row with the groups, counts and "Red on eca7a70176de: N failed, M passed". Check the map
reads (`mkdir -p $TMPDIR/empty-home` first):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src python3 -c "import pathlib; from gov.accept import runner; print({k: len(v) for k, v in runner.parse_map(pathlib.Path('tests/acceptance/W2-42a/README.md').read_text()).items()})"`
(never run gov accept itself in the sandbox).

## Red check (report it)
Run your file at your head eca7a70176de. Expected: RED = every refused form in 1, 2 and 3; GREEN = the guards. Say per
group whether it held. Run pytest only this way (one line):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-42a/test_w2_42a_r4_blob_refs_2.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
Also run the whole folder once (same line, `tests/acceptance/W2-42a`, adding `-n auto -m "not local_only" -k "not real and not green_here and not time_limit"`)
and report its counts: nothing outside your new file may change (the folder is green at eca7a70176de). The heavy slot
may queue: that is a wait. Anything longer than one line goes in a script file under `$TMPDIR`, run with bash or
python3 (a unique heredoc delimiter if you write one). Use the sandbox's own `$TMPDIR`; never write outside `$TMPDIR`
and your paths.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit's hash (12), the red
run's counts, one failure's reason line per group, what real git did with each form, and the map reader's output line;
in `tests`: the case count per group and which are red. A refusal twice for the same call by the guard, the sandbox
or a hook: stop and say so; never work around it (not even by another form or tool). Search with Read and Grep only
(no gov retrieve, no gov context in the sandbox); search again once, in other words. Never open the evaluation sets'
root or any hidden or memory-verdict folder. No merge in the sandbox. A resource gate's refusal is a wait.

## The ticket's context packet (gov context DAEO-03ub --role independent-test-designer --budget 20000, from the integration store's root)

```json
