# Brief: independent auditor, W2-42a (DAEO-03ub), FULL review round 2 (the last; DEC-1010)

Role: independent-auditor, read-only. Ticket DAEO-03ub (W2-42a), profile FULL, class C3.
Head to probe: w2/W2-42a at HEAD_FULL, in /home/usain/gov-os-worktrees/W2-42a (read it; write nothing in any tree).
What to judge: the ticket's 11 success lines (S1-S11) and 2 failure lines (F1, F2), in the ticket file
/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-03ub.md (each line with its Verify clause), against the
ticket's sources DEC-1040, DEC-1028, DEC-1027, DEC-958, DEC-953, DEC-1044 (read each by id in docs/DECISION_REGISTER.md)
and ACT-GUARD-FIX-3 section 7 (the eight parser lines). Return a verdict for every line.

## Round 1 and what changed since
Round 1 (probe record docs/probes/DAEO-03ub/PR-DAEO-03ub-round-1.md, head e9e4f7bac) failed S1, S6 and failure line F1
on one finding, F1: a `bash`/`sh` given an option with a value (`bash -euo pipefail <<'EOF'`, `-o pipefail`,
`-O extglob`, `--rcfile f`, also through `cat <<'EOF' | bash -o pipefail`) read its heredoc body as data, so the
parser gave no target and no sentinel and the read judge dropped the body (fail-open; the base caught these writes).
Its other findings F2 to F8 are recorded Wave 3 rows (ordinary work no), not this round's subject; do not re-raise
them unless the fix changed them.
Since then:
- an independent test designer added tests/acceptance/W2-42a/test_w2_42a_f1_shell_options.py and
  fixtures/f1_shell_options.json (F1's spellings and data controls; 2 hook-fixture cases are strict xfails naming
  ACT-GUARD-FIX-5: the live hook's own copy of the gap is the CTO's, outside this ticket);
- a fresh engineer changed `_kind` and `_script_words` in src/gov/guard/bash_writes.py (commits a4afc4166 and
  31201f0ad: option values skipped; /dev/stdin, /dev/fd/0 and /proc/self/fd/0 as standard input; the earlier shell
  reading kept as a floor, so a shell read as commands before is never data now), with unit cases in
  tests/unit/guard/test_w2_42a_parser.py and test_w2_42a_reads.py and a paragraph in docs/changes/W2-42a-evidence.md.
Judge first whether F1 is closed (all its spellings, directly and through a pipe, write side and read side) and
whether the fix fails closed everywhere (no form that gave a target or the sentinel before the fix gives neither
after it; no data body newly read as a write beyond the floor's kept over-reads). Then confirm the other lines still
hold at this head.

The lead's runs at this head: acceptance `491 passed, 2 xfailed`; `gov accept W2-42a` 491 passed, 0 failed, 2
skipped (the strict xfails); the scoped set: /home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/verify/verify.summary.

## How to run
Every pytest through the heavy slot, TMPDIR your sandbox's $TMPDIR, HOME an empty folder under it (mkdir -p $TMPDIR/empty-home first):

    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

Run the parser and judge directly from a script in your sandbox's $TMPDIR (PYTHONPATH as above); for the base and
for round 1's head, read the files from git history; never check anything out in the tree. Anything longer than one
line goes in a script file under $TMPDIR, with a unique heredoc delimiter if you write one. Search with Read and
Grep; search again once in different words if the first does not answer. Never open the evaluation sets' root or any
hidden or memory-verdict folder; never print a secret. If something is refused twice, stop and say so; never work
around a refusal.

