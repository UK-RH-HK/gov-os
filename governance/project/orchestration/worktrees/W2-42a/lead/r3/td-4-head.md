# Brief: independent test designer, W2-42a (DAEO-03ub), the apostrophe cases (DEC-1174 (1))

Role: independent-test-designer. Ticket DAEO-03ub (W2-42a), profile FULL, class C2 (one defect fix, narrow check).
Rewrite-Reason: DEC-1174 (1). You are a fresh test designer; you write tests from the behaviour stated here and read
no implementation diff that does not yet exist (the engineer starts after you).
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a-tests, branch w2/W2-42a-tests, head d73bd2756.
Your paths: tests/acceptance/W2-42a/** only (new files; do not edit the existing test files or fixtures).
Commit with (all trailers in ONE final paragraph, no blank line between them):
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1174 (1)" --trailer "Implements: DEC-1028, DEC-958" -- <your paths>`

## The defect (the behaviour to pin)
The product guard `decide()` in `src/gov/guard/decide.py` (it reads Bash through `src/gov/guard/bash_writes.py`)
refuses a Bash call whose heredoc body, read by a shell, holds a comment with an apostrophe, with "the command cannot
be read", even when the call writes nothing. Today:
- `bash -euo pipefail <<'EOF'` / `# don't overwrite` / `echo hi` / `EOF` is refused.
- `bash <<'EOF'` / `# it's fine` / `ls` / `EOF` is refused.
- The same bodies without the comment are allowed.
The fix to come (the engineer's, not yours): comment text in a shell body is dropped before the body is tokenised
(a `#` that starts a word, outside quotes and not part of `${…}` or `$#`, to the end of its line). A body still
unreadable after that stays refused.

A probe that calls `decide()` as an engineer on DAEO-03ub (copy it, do not import it):
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/r3/product_probe.py — the call is
`decide("Bash", {"command": cmd}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")` returning `(decision, why)`.
Build your own project root in `tmp_path` (see the `at`/`root` fixtures and `w2_42a_support.py` in
tests/acceptance/W2-42a/ for how the existing cases do it; you may import `w2_42a_support`).

## The cases to add (a new file tests/acceptance/W2-42a/test_w2_42a_apostrophe.py, with a fixture file if you like)
Use one body with an apostrophe in a comment that writes nothing, e.g. `# don't overwrite` / `echo hi`, and also
`# it's fine` / `ls`. Target T = `tests/acceptance/X/zz.py` (an engineer may never write the acceptance folder).
- (a) **Allowed:** each options form of W2-42a's F1 fixture (fixtures/f1_shell_options.json): `bash -euo pipefail`,
  `bash -o pipefail`, `bash -O extglob`, `bash --rcfile <f>`, `bash /dev/stdin`, `cat <<'EOF' | bash -o pipefail`,
  and plain `bash <<EOF`; each with a quoted and an unquoted delimiter where the form allows; body = an apostrophe
  comment and a harmless command. `decide()` returns allow.
- (b) **Still refused:** the same forms where the call then writes T after the heredoc: by `> T`, by `cp x.py T`, and
  by `python3 -c "open('T','w').write('x')"` (ACT-GUARD-FIX-5 round 2's four reversal calls are the probe's cases a, b,
  c, d). `decide()` returns deny.
- (c) **Still refused:** a body that itself writes T (`echo x > T`, `cp x.py T`) after such a comment. Deny.
  Also the fix's edge, so a too-wide comment drop is caught (each a body line that writes T, deny): a `#` that does
  not start a word (`echo a#b > T`), `${#v}` (`v=ab; echo ${#v} > T`), `$#` (`echo $# > T`), and a `#` inside quotes
  followed by a write on the same line (`echo "a # b" > T`, `echo 'it # s' > T`).
- (d) **Still refused, as today:** a body with a real unclosed quote outside a comment (e.g. `echo 'unclosed` /
  `ls`) is refused (deny, "cannot be read" or the unresolvable target's refusal).
Name each test so it states the behaviour (`test_apostrophe_a_…`, `_b_`, `_c_`, `_d_`). No xfail marks.

## Red check (report it)
Run your file on your head (the unfixed parser). Expected: every (a) case FAILS, each with the decision deny and the
reason "the command cannot be read" (assert the decision; put the reason in the assertion message so the red shows
it); (b), (c), (d) pass today. If an (a) case is green on the base, or red for another reason, say so in your return.
Run pytest only this way (one line):
`env HOME=/home/usain/gov-os-worktrees/W2-42a-tests/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-42a-td4/tmp PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-42a/test_w2_42a_apostrophe.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
(make the two folders first with `mkdir -p /tmp/w2-42a-td4/tmp /home/usain/gov-os-worktrees/W2-42a-tests/.gov-runtime/scratch/empty-home`).
Also run the whole folder once (same line, `tests/acceptance/W2-42a` and `-m "not local_only" -k "not real and not green_here and not time_limit"`) and report counts: nothing else may change.

## Return (your last message; nothing else is read)
The twelve labelled lines: task / status / work_completed / files_changed / evidence / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. In `evidence`: your commit's hash (12), the red
run's counts and the reason line of one (a) failure; in `tests`: the case count per group (a)-(d).
A refusal twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around it.
Search with Read and Grep only (no gov retrieve, no gov context in the sandbox); search again once, in other words.

## The ticket's context packet (gov context DAEO-03ub --role independent-test-designer)
