# W2-66 (DAEO-c1uz) lead checkpoint

## State: STOPPED on the scratch budget (DEC-898), returned PACKAGES (run 1)
- Branch w2/W2-66, code head a384480a (eng-1), then the lead's checkpoint commit made at this stop (see git log).
- Base c2d539c6. Commits: td-1 14cd488a, 32cd885f (W1-30, Rewrite-Reason), 4c22e4aa, 6c45acd6, c05a31a5, 967f6205;
  lead 1475b46c (CP-0002); eng-1 388d5892, 117b6e64, 528013b3, a8bf29f8, a384480a.
- pytest-timeout 2.4.0 installed in ~/.local (user site), not yet in the tool registry.

## Why stopped
- After the lead's full parallel run (44 min, head a384480a), /tmp/gov-os-lead-W2-66/pytest-of-usain/pytest-1 holds
  5,306,769 files and folders, about 47 GB (budget 20 GB / 1,000,000). `rm -rf` of it needs approval in this
  session: not done, no other form tried. Package P-W2-66-S1.

## Verification so far (head a384480a)
- rebuild-1: exit 0 (lexical, semantic, codeintel recreated). gov.__file__ = /home/usain/gov-os-worktrees/W2-66/src/gov/__init__.py
- collect-only (DEC-868): "15912/15914 tests collected (2 deselected) in 10.41s", exit 0.
- gov check: exit 0, 17 families, no RED; YELLOW: authority/role limits (core-decision-citations, old commits), product traceability (openspec-validate: openspec not on PATH in my run).
- parallel run: 6 failed, 15613 passed, 30 skipped in 2648.76s (44:08). Failures:
  - W2-66 research x3 (report not written yet: eng-2's round, expected);
  - W1-42 x2 (accepted_reds in this branch; retired on w2/integrate by DEC-900);
  - W1-39 test_w1_39_copy.py::test_copy_creates_the_overlay: CAUSED by this ticket (template's test-map copy enters the overlay; the case holds DEC-493's list) -> package P-W2-66-T1.
- serial-only run: NOT run (stopped before it). Script ready: /tmp/gov-os-lead-W2-66/run-serial.sh (55 entries).

## Next (a resume)
1. When the orchestrator answers S1 (cleanup of pytest-1; verification form, e.g. `-o tmp_path_retention_policy=failed`):
2. td-2: W1-39 overlay case revision with Rewrite-Reason: DEC-896 item 2 (if T1 (a)).
3. eng-2: brief briefs/eng-2.md is written (old launch form, report + measurement); fill in the lead's full-run figures
   (parallel 44.1 min: 15613 passed, 6 failed, 30 skipped; serial: from the next run).
4. Full verification again (parallel + serial), gov check; review (A3, max, JUDGEMENT.md); fixture trial section; return DONE.
- Then run 2 (after W2-07 merges): merge w2/integrate back, re-verify, fresh FULL probe.

## Loop count
- 1 (eng-1)

## Workers
- td-1: gov launch, sandboxed, xhigh; DONE; 12 fields; no gov retrieve; refusals 0 read (2 other: compound approval, rm).
- eng-1: gov launch, sandboxed, high; DONE; 12 fields; no gov retrieve; 3 read refusals (DEC-820 (c), its own over-wide reads); rm not granted.

## Guard read refusals counted
- lead: 0 (two permission prompts on rm -rf at this stop, not guard read refusals); td-1: 0; eng-1: 3.
