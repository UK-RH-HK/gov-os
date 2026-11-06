# W2-92's engineer, re-pin window 4: the stated links into the product (S7 to S10; DEC-1074 (5))

You are W2-92's engineer (`DAEO-n0wb`), launched by `gov launch` under that ticket's id, so the guard keeps you from
the ticket's acceptance tests. The CTO acts as the ticket's lead (no lead runs, DEC-1051).

**Read first, whole:** `/home/usain/gov-os-worktrees/W2-92/.gov-runtime/scratch/brief/EMG-d4b-launched.md`
(its "Engineer" paragraph is your job's form), `/home/usain/gov-os-worktrees/W2-92/.gov-runtime/scratch/brief/EMG-common.md`,
`governance/project/orchestration/INTENT-DEC-1052.md`, and the ticket `.tickets/DAEO-n0wb.md`: its KPI lines S7 to
S10, the failure lines, `allowed_paths`, and the note "DEC-1074 (5) placed here" at its end.

**Your worktree:** `/home/usain/gov-os-worktrees/W2-92` (branch `w2/W2-92`, brought to today's `w2/integrate` by the
CTO). Write only the ticket's `allowed_paths`.

**What you build:** S7 to S10 as the ticket states them, into the product's own code. **The measured reference is the
prototype** on `w2/W2-92-proto` (`e884675b`, your ticket's own earlier work: `src/gov/store/loader.py`,
`src/gov/retrieval/graph_route.py`, `src/gov/retrieval/retrieve.py`, `docs/research/W2-92-proto-drift.py` and its two
unit-test files). Read it and carry it over (`git diff w2/integrate...w2/W2-92-proto`), then bring it up to the KPI
text where the two differ:
- S7: one function, `register_statements`, holding the census's patterns, which `gov links` will read too; the links
  in a table of their own outside the digest; `edges`, the closure and `gov dangling` unchanged.
- S8: one bounded hop, at most 12 records, after today's closure chunks; CITES, UNDER and OF_TASK followed outward,
  AMENDS and SUPERSEDES inward (from the changed decision to its changer); a partial supersession never drops its
  target from what is current.
- S9: every register chunk a bundle carries names its entry's status word and its changers; a PROPOSED, REJECTED,
  WITHDRAWN or SUPERSEDED entry is marked not in force. Put the mark on each evidence item, not as a new top-level key
  of the bundle, so the pinned "nothing else changes" cases stay meaningful.
- S10: `docs/research/W2-92-proto-drift.py` in your paths; the drift section of `docs/research/W2-92-memory-measure.md`
  holds the before and after counts by the census's definitions (the CTO runs it on this repository's store and fills
  in the figures).

**Your own unit tests** with stand-ins (the prototype's two files are a start). **Your evidence file**
`docs/changes/W2-92-evidence.md`: one row per KPI line, how it is verified, the command, the result, the commit.
**Stop when your unit tests pass**; the CTO merges the designer's tests (`w2/W2-92-tests`) and you then run
`gov accept W2-92` once, reading results only. Never read `tests/acceptance/W2-92/` or the W2-54 case your ticket's
designer revised.

**Runs:** through the heavy slot, as `EMG-d4b-launched.md` says. **Commits:** `Task: DAEO-n0wb`,
`Implements: DEC-1072, DEC-1073, DEC-1074`, `Role: engineer`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
**Return:** the sandbox and `ps` checks first, then the twelve labelled fields. Est.: 3 to 4 hours.
