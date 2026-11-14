# Brief: independent auditor, W2-42a (DAEO-03ub), the narrow check of the apostrophe fix (DEC-1164 (18), DEC-1174 (1))

Role: independent-auditor, read-only. Ticket DAEO-03ub (W2-42a), profile FULL. A narrow independent check: you judge
ONLY the change since bb464f2ca (bb464f2caf9f), not the whole ticket again (the ticket passed its FULL review round 2;
probe record docs/probes/DAEO-03ub/PR-DAEO-03ub.md).
Head to probe: w2/W2-42a at HEAD_FULL, in /home/usain/gov-os-worktrees/W2-42a (read it; write nothing in any tree).
The change: `git -C /home/usain/gov-os-worktrees/W2-42a diff bb464f2ca..HEAD_FULL` (three engineer commits:
f16075e43, 669d87c91, c1ee147bd; files src/gov/guard/bash_writes.py, src/gov/guard/decide.py,
tests/unit/guard/test_w2_42a_parser.py, tests/unit/guard/test_decide.py, docs/changes/W2-42a-evidence.md).

## The defect and what was decided
The product guard `decide()` (src/gov/guard/decide.py, reading Bash through src/gov/guard/bash_writes.py) refused a
Bash call whose heredoc body, read by a shell, held a comment with an apostrophe (`bash <<'EOF'` / `# it's fine` /
`ls` / `EOF`) with "the command cannot be read", although it wrote nothing. A test designer pinned the behaviour in
tests/acceptance/W2-42a/test_w2_42a_apostrophe.py (312 cases; b7112b6ca, merged bb464f2ca): 120 red on the base,
70 the lift check's "cannot be read" refusals and 50 fail-opens where two apostrophe comments pair into a quote.

The cases' brief (the original (a) to (d)); T = `tests/acceptance/X/zz.py`, which an engineer may never write:
- (a) Allowed: each options form `bash -euo pipefail`, `bash -o pipefail`, `bash -O extglob`, `bash --rcfile <f>`,
  `bash /dev/stdin`, `cat <<'EOF' | bash -o pipefail`, and plain `bash <<EOF`; quoted and unquoted delimiter where the
  form allows; body = an apostrophe comment and a harmless command.
- (b) Still refused: the same forms where the call then writes T after the heredoc: by `> T`, by `cp x.py T`, and by
  `python3 -c "open('T','w').write('x')"`.
- (c) Still refused: a body that itself writes T (`echo x > T`, `cp x.py T`) after such a comment; and the fix's edge:
  a `#` that does not start a word (`echo a#b > T`), `${#v}`, `$#`, a `#` inside quotes followed by a write on the
  same line (`echo "a # b" > T`, `echo 'it # s' > T`).
- (d) Still refused, as today: a body with a real unclosed quote outside a comment (`echo 'unclosed` / `ls`).

The CTO's decided scope, P-03ub-APOS-1 (A) (DEC-1174 (1)): the engineer fixes src/gov/guard/bash_writes.py, closing
the fail-open cases, and fixes decide.py's `_lift_in`: comment text is dropped only where a shell reads it (the
top-level command and the bodies of heredocs fed to `bash`/`sh`, split out with `bash_writes.heredocs`); every other
body (Python, data) is read as today, so an apostrophe in a Python or data body stays refused. DEC-409's rule is
unchanged: no agent Bash call holds the lift form of `gov pause` (--off). The reading of data bodies stays as it is.
The narrow check includes DEC-409's own cases (read DEC-409 by id in docs/DECISION_REGISTER.md; its cases are found
by grep for `lift_refusal` and `DEC-409` under tests/: tests/unit/guard/test_decide.py, tests/unit/pause,
tests/unit/containment/test_w1_50_freeze_flag.py, tests/acceptance/W1-50, W1-28, W2-16).

## The engineer's stated departures (judge each; they are claims, not facts)
1. `python3 -c` strings' writes are now the product's write targets (669d87c91), beyond the two named fixes; the
   engineer says without it case (b)'s `python3 -c` call is allowed. It also says unparseable `python3 -c` code, or
   code that runs `exec(...)` of a file, is now unresolvable and refused, while plain read-only one-liners stay free.
2. In the lift check it blanks only a comment's quote characters and keeps the comment's words (so a comment holding
   `gov pause --off` stays refused), instead of dropping the comment text.
3. The lift check now refuses a data or Python body holding an odd number of apostrophes followed by a top-level
   `# it's` (the base let it through only by an accidental pairing).
4. A shell heredoc nested inside `$( )` is still refused by the lift check when it holds an apostrophe comment.
5. It reports a fail-closed comparison over 211,200 generated commands (base vs new guard) in its evidence paragraph.

## What to judge
- Each of (a) to (d) holds at the head (directly through `decide()`, and the acceptance file passes).
- The change stays inside (A)'s scope: a comment is no quote only where a shell reads it; Python and data bodies
  are read as before by the lift check; no data body is newly read as commands or as a write.
- DEC-409 holds: no form in which the base found the lift form is now free of it; its existing cases stay green.
- Fail closed: no form that gave a write target, the unresolvable target or a refusal on bb464f2ca gives none after
  the change (search for counterexamples: comments with quotes beside real writes, `#` in words, `$#`, `${#…}`,
  escaped `\#`, comments inside `$( )`, backticks, `bash -c` strings, nested heredocs, here-strings, a lift form
  after or inside a comment, CRLF). Departures 1 to 4: in scope or not, and does each fail open, lose work, or
  refuse ordinary work.
Report each finding with what you ran.

Verify lines for the verdict block (use these ids): A = case (a); B = case (b); C = case (c); D = case (d);
SCOPE = (A)'s scope held; DEC409 = DEC-409's rule and cases held; FC = fail closed over the change.

The lead's runs at this head: `gov accept W2-42a` and the scoped set, in
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/apos-accept.log and apos-scoped.log (SCOPED_LINE).

## How to run
Every pytest through the heavy slot, TMPDIR your sandbox's $TMPDIR, HOME an empty folder under it (mkdir -p $TMPDIR/empty-home first):

    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

Call `decide("Bash", {"command": cmd}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")` (it returns
`(decision, why)`) from a script in your sandbox's $TMPDIR (PYTHONPATH as above; see
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/r3/product_probe.py for a probe to copy); for the base,
export bb464f2ca's src with `git archive bb464f2ca src | tar -x -C $TMPDIR/base` and run it there; never check
anything out in the tree. Anything longer than one line goes in a script file under $TMPDIR, with a unique heredoc
delimiter if you write one. Search with Read and Grep; search again once in different words if the first does not
answer. Never open the evaluation sets' root or any hidden or memory-verdict folder; never print a secret. If
something is refused twice, stop and say so; never work around a refusal.

