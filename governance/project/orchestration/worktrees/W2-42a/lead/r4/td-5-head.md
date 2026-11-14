# Brief: independent test designer, W2-42a (DAEO-03ub), the cases for F1, F4 and departure 1 (DEC-1174 (1), APOS-3/APOS-4)

Role: independent-test-designer. Ticket DAEO-03ub (W2-42a), profile FULL. You are a fresh test designer: you write
tests from the behaviour stated here (DEC-136); the engineer starts after you and you read no fix (none exists yet).
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a-tests, branch w2/W2-42a-tests, head 692bc41bd.
Your paths: tests/acceptance/W2-42a/** only. Add a NEW file tests/acceptance/W2-42a/test_w2_42a_apostrophe_2.py (and a
fixture file under tests/acceptance/W2-42a/fixtures/ if you like). Do not edit the existing test files or fixtures.
Commit with (all trailers in ONE final paragraph, no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1174 (1), APOS-3/APOS-4" --trailer "Implements: DEC-1028, DEC-958" -- <your paths>`

## The product under test
The product guard `decide()` in `src/gov/guard/decide.py` reads a Bash call through `src/gov/guard/bash_writes.py` and
refuses a write outside the role's allowed paths. Call it as the existing file
tests/acceptance/W2-42a/test_w2_42a_apostrophe.py does (its `proj` fixture, its helpers, its T and its allowed path;
copy what you need or import `w2_42a_support`). Target T = `tests/acceptance/X/zz.py` (an engineer on DAEO-03ub may
never write the acceptance folder); the allowed path is the one that file's
`test_apostrophe_a_the_call_then_writing_an_allowed_path_is_allowed` uses (call it A below).

## The behaviour to pin (the CTO's decisions P-03ub-APOS-3 (1) and P-03ub-APOS-4 (a), DEC-1174 (1))

### F1: a `#` inside `${…}` never starts a comment
Bash never takes a `#` inside a parameter expansion `${…}` for a comment, at any depth, quoted or not. Today the
guard drops the rest of the line after such a `#` (after a blank) as a comment, and with it a write that bash runs:
the call is allowed and bash writes T (a fail-open). The behaviour wanted: the write is seen; it is refused when the
target is T, and allowed when the target is A. Cases, each with T (deny) and with A (allow):
- `v='a # b'; echo ${v%% #*} > T`
- `echo ${x:- #a}; echo x > T` and `v='a #b'; echo ${v/ #/} > T`
- `while read -r l; do echo ${l%% #*}; done < f > T`
- `while read -r l; do k=${l%% #*}; echo $k >> T; done < f`
- a write placed before the `${…}` on the same line: `echo ${X:- #} > A; cp x.py T` (deny; T is the second write)
- a nested and a quoted form: `echo "${v%% #*}" > T`, `echo ${v:-${w%% #*}} > T`
- the same forms inside a shell heredoc body: `bash <<'EOF'` / `v='a # b'` / `echo ${v%% #*} > T` / `EOF`
  (and the `while read` form as the body), and inside `bash -c`: `bash -c 'v="a # b"; echo ${v%% #*} > T'`
- the forms that never were comments, kept as guards: `v=ab; echo ${#v} > T`, `echo ${v#a} > T`, `echo $# > T`
  (deny), each also inside `bash <<'EOF'` and `bash -c`.
- a guard that a real comment is still a comment: `echo hi # it's fine` with no write is allowed, and
  `echo hi > T # it's fine` is denied.

### F4: a here-string holding ` #` is read, not refused as unreadable
Today `grep -c b <<< "a # b"`, `wc -w <<< "one # two"` and `jq -r '.x' <<< '{"x": "a # b"}'` are refused with "the
command cannot be read" though they write nothing. The behaviour wanted: they are allowed; a here-string whose command
writes is judged as usual: `grep -c b <<< "a # b" > T` and `tr a b <<< 'x # y' > T` are refused for T (the reason
names the target, not "cannot be read"; assert the decision and put the reason in the assertion message), and the same
two writing A are allowed. Do NOT add cases for `bash <<< "…"` (a here-string fed to bash; pre-existing, out of scope).

### Departure 1 (accepted by name): `python3 -c` writes are write targets
`python3 -c "open('T','w').write('x')"` is refused (T outside the role's paths); the same writing A is allowed; plain
read-only one-liners stay free: e.g. `python3 -c "import json; print(json.dumps({'a': 1}))"`,
`python3 -c "import os; print(os.listdir('.'))"`, `python3 -c "import pathlib; print(pathlib.Path('README.md').read_text()[:10])"`
are allowed. Add these only where test_w2_42a_apostrophe.py does not already pin them (its (b) cases hold a
`python3 -c` write after a heredoc; a standalone one-liner is not there, so add it).

Name each test so it states the behaviour (`test_apos2_f1_…`, `test_apos2_f4_…`, `test_apos2_dep1_…`). No xfail marks.

## Red check (report it)
Run your file on your head (the unfixed parser). Expected, and say per group whether it held:
- RED: each F1 case with T that has a `#` after a blank inside `${…}` (fails open today: decision allow, want deny);
  the F4 no-write cases and the F4 writes of A (deny "cannot be read" today, want allow); the F4 writes of T if you
  assert the reason names T (refused as unreadable today).
- GREEN today (guards that the fix must keep): the F1 cases with A, the `${#v}`/`${v#a}`/`$#` forms, the real-comment
  guards, and the departure 1 cases (departure 1 is already in the head).
If a case expected red is green, or red for another reason, say so in your return. Run pytest only this way (one line,
TMPDIR is your sandbox's own `$TMPDIR`; make the folder first with `mkdir -p $TMPDIR/empty-home`):
`cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-42a/test_w2_42a_apostrophe_2.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
Also run the whole folder once (same line, `tests/acceptance/W2-42a`, adding `-m "not local_only" -k "not real and not green_here and not time_limit"`)
and report its counts: nothing outside your new file may change. You may run any command through real bash in
`$TMPDIR` to confirm what bash writes; never write outside `$TMPDIR` and your paths.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit's hash (12), the red
run's counts and the reason line of one F1 and one F4 failure; in `tests`: the case count per group (F1, F4, dep1) and
which are red. A refusal twice for the same call by the guard, the sandbox or a hook: stop and say so; never work
around it. Search with Read and Grep only (no gov retrieve, no gov context in the sandbox); search again once, in
other words. Never open the evaluation sets' root or any hidden folder. No merge in the sandbox. A resource gate's
refusal is a wait.

## The ticket's context packet (gov context DAEO-03ub --role independent-test-designer --budget 12000)
