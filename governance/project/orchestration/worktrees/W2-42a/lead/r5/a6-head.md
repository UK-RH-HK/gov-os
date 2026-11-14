# Brief: independent auditor, W2-42a (DAEO-03ub), the narrow check of the R3 fix (DEC-1164 (18), DEC-1154)

Role: independent-auditor, read-only. Ticket DAEO-03ub (W2-42a), profile FULL. A narrow independent check (DEC-1154):
you judge ONLY the change since the merge d3ba8e50b (d3ba8e50b4c6e703eafa41093b580af87a336fe1, w2/integrate merged into
the branch), not the whole ticket and not the earlier rounds again (the ticket passed its FULL review round 2,
docs/probes/DAEO-03ub/PR-DAEO-03ub.md, and the narrow check of the F1/F4 fix, PR-DAEO-03ub-apos-2.md). This is the
CTO's own P2 round (DEC-1164 (18)), not a review round under DEC-1010.
Head to probe: w2/W2-42a at HEAD_FULL, in /home/usain/gov-os-worktrees/W2-42a (read it; write nothing in any tree).
Your one allowed path, named for the launcher only: tests/unit/guard/test_w2_42a_zz.py. Do not write it.
The change: `git -C /home/usain/gov-os-worktrees/W2-42a diff d3ba8e50b..HEAD_FULL`: the test designers' merge
ed77eb353 (tests/acceptance/W2-42a/test_w2_42a_here_string.py, 31 cases, and README map rows) and the engineer's commit
df7468015 (src/gov/guard/bash_writes.py, src/gov/guard/decide.py, tests/unit/guard/test_w2_42a_here_string.py,
docs/changes/W2-42a-evidence.md).

## What the previous check found, and what the CTO decided (the reopening of 2026-11-14, DEC-1164 (18))
- **R3 (fix now):** the line parser split a command at `<<`/`<<<` (decide.py `_line_write_targets`), so a write
  argument after a here-string was missed: `tee <<< "x" T`, `tee -a <<< "x" T` were allowed and real bash writes T.
- **The unreadable fallback's here-string forms (fix now; older than the apostrophe work):** `bash <<< 'touch T'`,
  `xargs touch <<< T`, and a body-less heredoc after a `python3 -c` write (`python3 -c "open('T','w').write('x')"; cat
  <<EOF`, no body, no end line) were allowed.
- **The rule decided:** the word after `<<<` is the here-string's text, never the command's end. The words after it
  stay the command's arguments, so their write targets are judged. The text given to `bash <<<`/`sh <<<` is a command
  and is judged as one. Anything still unreadable fails closed. Read-only forms stay free (`grep -c b <<< "a"`,
  `wc -l <<< "$v"`).
- **Recorded rows, not to be re-judged** (the previous checks' R1, R2, R4, R5 and earlier F2, F5): report them only if
  this change made them worse.
T = `tests/acceptance/X/zz.py` (an engineer on DAEO-03ub may never write the acceptance folder); an allowed path is
`src/ok.py` (the tests' A).

## The engineer's stated claims (judge each; they are claims, not facts)
1. `_line_write_targets` in decide.py keeps `<<<` with its command and skips its one word, so the words after it stay
   the command's arguments; `<` still skips one word, but after a punctuation word it now skips only itself (it says
   this can only add targets).
2. `bash_writes.judge` has new readings for a command the first reading cannot read: the `hstr` reading turns each
   here-string into a heredoc of its own text, so a text given to `bash`/`sh` (or piped to one) is judged as commands;
   `xargs [options] CMD <<< WORDS` is judged as CMD with the words as arguments; a text the guard cannot know
   (`bash <<< "$X"`, `sh <<< "$(…)"`) and xargs `-I`/`-0`/`-d` give the unresolvable target.
3. A body-less heredoc after a `python3 -c` write keeps that write.
4. Known effects it reports: `cat <<< touch T` gave T before (through the split reading) and gives nothing now (it says
   read-only, no write); `python3 <<< "open('T','w')"` stays opaque, answered as `python3 <<EOF` is (KPI 8: a Python
   body goes to the hook's findings, not to product targets); a command the first reading cannot read is now read in
   11 ways instead of 3, not timed against the hook deadline.
5. Unit and acceptance: test_w2_42a_here_string.py 31 passed (12 failed before); tests/acceptance/W2-42a 912 passed,
   2 xfailed; its unit file 51 passed.

## What the lead saw (a pointer, not a finding; check it yourself)
The lead's own probe of the head against d3ba8e50b found every changed decision moving toward deny, and these forms
allowed on both: `python3 <<< "open('T','w')"`, `eval "$(cat <<< 'touch T')"`, `parallel touch <<< T`; and
`tee 0<<< x T` refused naming a target `0`, not T, on both.

## What to judge
- R3 holds at the head (directly through `decide()`, and the acceptance file passes): a write argument after a
  here-string is seen for each writer (tee, tee -a, cp, sort -o, dd of=, and your own variants: `<<<x` with no blank,
  quoted and unquoted texts, `$(…)` texts, an fd prefix, here-strings inside lists, pipelines, `bash -c`, a heredoc
  body); a redirect after a here-string stays judged.
- The fallback forms hold: `bash <<<`/`sh <<<` texts are judged as commands (with wrappers and options), `xargs CMD <<<`
  is judged, an unknowable text fails closed, and the body-less heredoc after a `python3 -c` write keeps the write.
- Read-only forms stay free (`grep -c b <<< "a"`, `wc -l <<< "$v"`, `cat <<< T`, `read -r a b <<< "x y"`,
  `bash <<< 'echo hi'`), and judge any ordinary work the change now refuses.
- DEC-409 holds (read DEC-409 by id in docs/DECISION_REGISTER.md): no form in which d3ba8e50b found the lift form of
  `gov pause` (--off) is now free of it; its cases stay green (grep tests/ for `lift_refusal` and `DEC-409`).
- Fail closed over the change: no form that gave a write target, the unresolvable target or a refusal on d3ba8e50b
  gives none after it (judge claim 4's `cat <<< touch T`). Search for counterexamples, and run each form that moved
  toward allow in real bash under $TMPDIR to see whether it writes T. Judge claims 1 to 4: in scope or not, and does
  each fail open, lose work, or refuse ordinary work. If you can, time the slowest unreadable commands you find
  through `decide()` at the head and the base (claim 4's 11 readings).
Report each finding with what you ran.

Verify lines for the verdict block (use these ids): R3 = a write argument after a here-string is judged;
FALLBACK = the three fallback forms (shell text, xargs, body-less heredoc after `python3 -c`) are judged or fail closed;
RO = the read-only here-string forms stay free; DEC409 = DEC-409's rule and cases held; FC = fail closed over the change.

The lead's runs at this head: `gov accept W2-42a` and the scoped set, in
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/r3-accept.log and r3-scoped.log (SCOPED_LINE).

## How to run
Every pytest through the heavy slot, TMPDIR your sandbox's own $TMPDIR, HOME an empty folder under it (mkdir -p $TMPDIR/empty-home first):

    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

Call `decide("Bash", {"command": cmd}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")` (it returns
`(decision, why)`; pass `root` as a real-path string, not a Path) from a script in your sandbox's $TMPDIR (PYTHONPATH as
above; see /home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/r5/probe_head.py for a probe to copy); for
the base, export d3ba8e50b's src with `git archive d3ba8e50b src | tar -x -C $TMPDIR/base` and run it there; never
check anything out in the tree. Anything longer than one line goes in a script file under $TMPDIR, with a unique
heredoc delimiter if you write one. Search with Read and Grep; search again once in different words if the first does
not answer. Never open the evaluation sets' root or any hidden or memory-verdict folder; never print a secret. If
something is refused twice, stop and say so; never work around a refusal.

