# Brief: independent auditor, W2-42a (DAEO-03ub), FULL review (round 1 of at most 2)

Role: independent-auditor, read-only. Ticket DAEO-03ub (W2-42a), profile FULL, class C3.
Head to probe: w2/W2-42a at e9e4f7bacf416016d995ac5190d8e05b644dce80, in /home/usain/gov-os-worktrees/W2-42a (read it; write nothing in any tree).
What to judge: the ticket's 11 success lines (S1-S11) and 2 failure lines (F1, F2), in the ticket file
/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-03ub.md (each line with its Verify clause), against the
ticket's sources DEC-1040, DEC-1028, DEC-1027, DEC-958, DEC-953, DEC-1044 (read each by id in docs/DECISION_REGISTER.md)
and ACT-GUARD-FIX-3 section 7 (the eight parser lines).

The code under review (the ticket's own changes since its base, the merge base of HEAD and w2/integrate; diff limited to src, tests/unit and docs/changes):
- src/gov/guard/bash_writes.py (new, about 1,635 lines: the port of the reviewed .claude/hooks/bash_writes.py)
- src/gov/guard/decide.py (_extract_bash_write_targets), src/gov/guard/reads.py (_set_aside, _Judge.tool/command)
- tests/unit/guard/test_decide.py, tests/unit/guard/test_w2_42a_parser.py, tests/unit/guard/test_w2_42a_reads.py
- docs/changes/W2-42a-evidence.md (the measures, S9)

The acceptance tests are tests/acceptance/W2-42a/ (452 cases, an independent test designer's). This resume's lead
merged one test-design restore (49ea1fa10a69, merged at e9e4f7bac): 33 replay rows whose logged worktree was removed
after its ticket landed are replayed in a stand-in clone; and line 74 (judged true) refuses only with a placeholder in
the stand-in's hidden folders, because the hidden parts moved out of the trees (DEC-1070). Judge whether that restore
keeps S11 a real check (not vacuous), as part of S11.

The lead's runs at this head: acceptance `452 passed`; `gov accept W2-42a` passed 452, failed 0; the scoped set
(lead_verify, select_tests.py) on a11ddc51e: 6293 tests, only those 33 replay rows red (now restored), serial 5 passed;
the scoped run on e9e4f7bac: /home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/verify/verify.summary.

## What to look for, beyond the tests passing
- Fail-open first: any Bash write the new parser misses that the base parser (the merge base's decide.py) caught; any
  unknown or unparseable form that now yields no target and no `/<guard-unresolvable>` sentinel; any read the new read
  judge lets through (a secret, a hidden file, a run-time listing) that the base refused. A finding that would make
  the guard fail open in ordinary work is a blocker: name it first.
- Plant where the tests are thin: run the parser and the judge directly on your own commands (python3 with
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src, from a script in your sandbox's $TMPDIR). For the base, read
  the merge base's files from git history; never check anything out in the tree.
- The port: differences between src/gov/guard/bash_writes.py and the reviewed .claude/hooks/bash_writes.py that
  change a judgement.

## How to run
Every pytest through the heavy slot, TMPDIR your sandbox's $TMPDIR, HOME an empty folder under it (mkdir -p $TMPDIR/empty-home first):

    cd /home/usain/gov-os-worktrees/W2-42a && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
      PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a/src \
      bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
      python3 -m pytest tests/acceptance/W2-42a tests/unit/guard -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed

Anything longer than one line goes in a script file under $TMPDIR, run with bash or python3. Search with Read and
Grep; search again once in different words if the first does not answer. Never open the evaluation sets' root or any
hidden or memory-verdict folder; never print a secret. If something is refused twice, stop and say so; never work
around a refusal.

