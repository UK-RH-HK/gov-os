# W2-92's independent test designer, re-pin window 4: S7 to S10, and W2-54's premise (DEC-1074 (5), (6))

You are W2-92's independent test designer (`DAEO-n0wb`), launched by `gov launch` under that ticket's id, so the guard
keeps you from the ticket's new code. The CTO acts as the ticket's lead (no lead runs, DEC-1051).

**Read first, whole:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/briefs/EMG-d4b-launched.md`
(the launched workers' rules: the sandbox check first, no `gov retrieve`, no real model, the pytest exclusions, the
commit form; its "Test designer" paragraph is your job's form), then `EMG-common.md` beside it,
`governance/project/orchestration/INTENT-DEC-1052.md`, and the ticket `.tickets/DAEO-n0wb.md` (its KPI lines S7 to
S10, the failure lines, and the note "DEC-1074 (5) placed here" at its end). For the register, grep the entries you need
(`### DEC-1071`, `### DEC-1072`, `### DEC-1073`, `### DEC-1074`; the file is 1.6 MB). For the kinds of stated link and
their forms, read `docs/research/D4B-link-census.md` (sections 0 to 2 and 4) and
`governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md` sections 2.2 and 6.1.

**Never read:** the branch `w2/W2-92-proto` or the worktree `~/gov-os-worktrees/W2-92-proto` (the engineer's
prototype), `w2/W2-92`'s new commits beyond integrate, and `docs/research/W2-92-proto-drift.py`. Write from the KPI
lines and the census, never from an implementation. The integrated code on `w2/integrate` is readable (DEC-963).

**Your worktree:** `/home/usain/gov-os-worktrees/W2-92-tests` (branch `w2/W2-92-tests`, today's `w2/integrate` merged
in by the CTO at `436a7520`). Write only `tests/acceptance/W2-92/**` and, for item 2, the one W2-54 case named there.

## 1. S7 to S10: acceptance tests from the KPI lines
- **The fixture:** extend `tests/acceptance/W2-92/`'s planted repository (its `conftest.py` and `w2_92_support.py`): a
  small register whose entries state each link kind S7 names in the census's forms (`**Under:**`, `**Changes:**`,
  `**Changed by:**`, `**Supersedes:**` with ids alone, `**Supersedes:**` naming a part, `**Amends:**`, a free-text
  "superseded by"), tickets with `sources:` and `closes:`, a checkpoint with `task:`, a close record with
  `decisions_applied:`, a spec with `decisions:`; its store built in a temporary folder with stand-in embedder and
  reranker, as the existing cases do. Never this repository's store.
- **S7:** each stated kind becomes its typed link (CITES, OF_TASK, UNDER, SUPERSEDES only for ids alone, AMENDS for
  the rest) in a table of its own; `edges`, the closure, `gov dangling` and the bundle's digest are unchanged by it.
  The KPI's "match the census's statements one for one on this repository's register" is the CTO's measured check
  (it needs this repository's store): name it in the README map as verified by the evidence file, not by a case.
- **S8:** a plain question that reaches a record by the record route or the closure also brings, within one hop and at
  most 12 records, the records it CITES, its UNDER and OF_TASK, and the changers of a changed decision (AMENDS and
  SUPERSEDES followed inward), after today's closure chunks; a question that reaches no record gets today's bundle. A
  partial supersession never drops its target from what is current (the new failure line). The adoption rule (the
  measure) is the CTO's: README map only.
- **S9:** every register chunk a bundle carries names its entry's status word and the entries that change it; a
  PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED entry is marked not in force; a register chunk without its status is the
  failure.
- **S10:** a measured record. A case may check only that `docs/research/W2-92-memory-measure.md` holds a drift section
  with both counts (before and after) in the census's definitions; or name it as verified by the evidence file.
- **Each case red on today's integrated code** (`w2/integrate`, the tree as merged), for the right reason; show it.
- **The README map** with full node ids, one line per KPI line, as the folder's existing map does.

## 2. W2-54's premise (DEC-1074 (6))
- `tests/acceptance/W2-54/test_w2_54_dropped_order.py::test_an_empty_retrieval_result_gives_one_packet` assumes a
  search finds nothing. Under S8, a ticket's title now legitimately brings its `sources:` records into a bundle, so the
  premise no longer holds once the links land.
- **Rewrite its premise only:** a question and a planted repository for which retrieval legitimately returns nothing
  both today and under S8 (for example, a question that names no record and matches no text). What the case asserts
  about the packet stays as it is.
- It must stay green on today's integrated code; show it. Commit it on its own, with `Task: DAEO-n0wb`,
  `Rewrite-Reason: DEC-1074 (6): a ticket's sources now legitimately bring a record (W2-92 S8)`, and `Role:
  independent-test-designer`.

## 3. Test runs
- Try each run through the heavy slot:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh pytest ...`.
  If the sandbox refuses the slot's lock, run only your own new or changed files directly, one file at a time, and say
  so; the CTO re-runs the folders through the heavy slot outside the sandbox.
- Always with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-92-tests/src`, `-o tmp_path_retention_policy=failed -p
  no:cacheprovider`, and the exclusions and empty `HOME` of `EMG-d4b-launched.md`.

## 4. Commits and return
- Commits: `Task: DAEO-n0wb`, `Implements: DEC-1074`, `Role: independent-test-designer`, `Co-Authored-By: Claude Opus
  5.5 <noreply@anthropic.com>`, with `-- <paths>`. Never merge, push, amend or rebase.
- Return: the sandbox check and the `ps` check first, then the twelve labelled fields. In `evidence`, each S line's
  cases with their red on integrate, W2-54's case green, and the commits. Then `TESTS-READY` text for the CTO.
- Est.: 2 to 3 hours. Keep to this scope; anything else goes in `discoveries`.
