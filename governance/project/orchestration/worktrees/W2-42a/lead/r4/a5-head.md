# Brief: independent auditor, W2-42a (DAEO-03ub), the narrow check of the F1/F4 fix (DEC-1164 (18), DEC-1174 (1), APOS-3/APOS-4)

Role: independent-auditor, read-only. Ticket DAEO-03ub (W2-42a), profile FULL. A narrow independent check (DEC-1154):
you judge ONLY the change since 692bc41bd (692bc41bd177), not the whole ticket and not the earlier apostrophe fix again
(the ticket passed its FULL review round 2, probe record docs/probes/DAEO-03ub/PR-DAEO-03ub.md; the previous narrow
check, docs/probes/DAEO-03ub/PR-DAEO-03ub-apos.md, failed on FC with F1). This is not a review round under DEC-1010.
Head to probe: w2/W2-42a at HEAD_FULL, in /home/usain/gov-os-worktrees/W2-42a (read it; write nothing in any tree).
The change: `git -C /home/usain/gov-os-worktrees/W2-42a diff 692bc41bd..HEAD_FULL`: the test designer's merge
c461d79de (tests/acceptance/W2-42a/test_w2_42a_apostrophe_2.py, 80 cases, README rows) and four engineer commits
fa77bb331, 1388fcec6, 07fb14799, a62cd8c11 (src/gov/guard/bash_writes.py, tests/unit/guard/test_w2_42a_apos2.py,
docs/changes/W2-42a-evidence.md). decide.py is not changed.

## What the previous check found, and what the CTO decided (DEC-1174 (1), the CTO's P2 round DEC-1164 (18))
- **F1 (fix now, P-03ub-APOS-3 (1)):** a `#` after a blank inside an unquoted `${…}` was taken for a comment and a
  write after it was dropped (`v='a # b'; echo ${v%% #*} > tests/acceptance/X/zz.py`: the base 692bc41bd's parent
  denied, 692bc41bd allowed, real bash writes). Decided: a `#` inside `${…}` (at any depth, quoted or not) never starts
  a comment; the same in a top-level command, inside a `bash <<'EOF'` body and inside `bash -c`. The write is seen and
  refused when its target is outside the role's paths, allowed when inside. `${#v}`, `${v#a}`, `$#` are no comment.
- **F4 (joins this batch, P-03ub-APOS-4 (a)):** a here-string holding ` #` (`grep -c b <<< "a # b"`) is read, not
  refused as unreadable, and its writes are judged as usual. `bash <<< "…"` (a here-string fed to bash; F6) is out of
  scope and must not get freer.
- **Departure 1 (accepted by name, P-03ub-APOS-4 (a)):** `python3 -c` writes are write targets, so the call is refused
  when they fall outside the role's paths; read-only one-liners stay free.
- **Recorded rows, not to be re-judged** (ordinary work no): F2 (a commented backtick plus a multi-line backtick that
  hides a write; fails open) and F5 (a one-line backtick comment refused). Report them only if this change made them
  worse.
T = `tests/acceptance/X/zz.py` (an engineer on DAEO-03ub may never write the acceptance folder); an allowed path is
`src/ok.py` (the tests' A).

## The engineer's stated claims (judge each; they are claims, not facts)
1. The scan tracks `${…}` like bash 5.2: a `#` in it starts no comment; the first plain `}` closes it, a nested `${`
   nests; quotes, backticks and `$(…)` nest inside it; `<<` inside it is text; an unclosed `${` is an unclosed quote.
2. `<<<` is a here-string, not a heredoc. A here-string only data readers take is read normally; one a command may run
   (`bash <<< …`, `cat <<< … | sh`, an unknown program) stays unreadable as before, in the write path and in DEC-409's
   `comment_spans`.
3. Fail-closed second readings: when the new reading cannot read a command, `judge()` reads it again with here-strings
   as data and with the old comment rule, and returns those targets with decide's unreadable fallback's answer.
4. Beyond F1/F4 (07fb14799): an unquoted shell heredoc body's substitutions are judged on the whole body, comments
   included (it found `bash <<EOF` / `# note $(touch T)` / `EOF` allowed on the base; real bash writes T).
5. Known effects it reports: `$${x` with no `}` is refused (over-refusal); `grep x <<< y # it's` is now allowed (wider
   than the named F4 forms; it says real bash writes nothing); a fail-closed comparison over 136,925 commands, 11,117
   moved toward allow and none of them writes T or runs the lift form in real bash.
6. Pre-existing fail-opens it found in decide's unreadable fallback, unchanged: `bash <<< 'touch T'`,
   `xargs touch <<< T`, and `python3 -c "open('T','w')"; cat <<EOF` with no body. Confirm only that this change did
   not make them freer.

## What to judge
- F1 holds at the head (directly through `decide()`, and the acceptance file passes): each form in the cases and your
  own variants (nesting, quotes, `${x:-…}`, `${x/…/…}`, `${x%%…}`, inside `bash -c`, a `bash <<'EOF'` body, `$( )`,
  backticks, a `while read` loop) gives the write; `${#v}`, `${v#a}`, `$#` stay correct; a real comment stays a comment.
- F4 holds: the here-string forms are allowed when they write nothing, and their writes are judged; `bash <<<` and
  other runners of a here-string are not freer than on 692bc41bd.
- Departure 1 holds as decided and is unchanged by this change.
- DEC-409 holds (read DEC-409 by id in docs/DECISION_REGISTER.md): no form in which 692bc41bd found the lift form of
  `gov pause` (--off) is now free of it; its cases stay green (grep tests/ for `lift_refusal` and `DEC-409`).
- Fail closed over the change: no form that gave a write target, the unresolvable target or a refusal on 692bc41bd
  gives none after it, except the F4 forms decided above. Search for counterexamples, and run each form that moved
  toward allow in real bash under $TMPDIR to see whether it writes T. Judge claims 1 to 5: in scope or not, and does
  each fail open, lose work, or refuse ordinary work.
Report each finding with what you ran.

Verify lines for the verdict block (use these ids): HASH = F1's decision held; HSTR = F4's decision held;
DEP1 = departure 1 held; DEC409 = DEC-409's rule and cases held; FC = fail closed over the change.

The lead's runs at this head: `gov accept W2-42a` and the scoped set, in
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/apos2-accept.log and apos2-scoped.log (SCOPED_LINE).

## How to run
Every pytest through the heavy slot, TMPDIR your sandbox's own $TMPDIR, HOME an empty folder under it (mkdir -p $TMPDIR/empty-home first):

    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

Call `decide("Bash", {"command": cmd}, root, "engineer", "DAEO-03ub", cwd=root, flag="open")` (it returns
`(decision, why)`) from a script in your sandbox's $TMPDIR (PYTHONPATH as above; see
/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/r3/product_probe.py for a probe to copy); for the base,
export 692bc41bd's src with `git archive 692bc41bd src | tar -x -C $TMPDIR/base` and run it there; never check
anything out in the tree. Anything longer than one line goes in a script file under $TMPDIR, with a unique heredoc
delimiter if you write one. Search with Read and Grep; search again once in different words if the first does not
answer. Never open the evaluation sets' root or any hidden or memory-verdict folder; never print a secret. If
something is refused twice, stop and say so; never work around a refusal.

