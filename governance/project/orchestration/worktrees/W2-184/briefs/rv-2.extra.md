## Round 1 and what changed since (judge these first, then the whole ticket again)
- Round 1's record: `docs/probes/DAEO-6f0s/PR-DAEO-6f0s-round-1.md` (judgement fail on F1; the lead's triage at its end).
- The fix round, given round 1's findings as described behaviours: the test designer's cases
  `tests/acceptance/W2-184/test_w2_184_r1_rows.py` (24bf5a363) and the engineer's commits fb4144730 and e064e2dd5:
  F1 hidden sets in the C3 rule; F8 `.claude/settings.local.json`, `governance/project/secrets.yaml`,
  `governance/project/indep-walls/*` in the C3 rule; F2 a review round 3 or more refused without `--owner-named`
  whatever its setting (interface 1.5 and 6.3, amended; below). The fix diff: commits fb4144730 and e064e2dd5 (`git
  show` each).
- Rows from round 1 left for the CTO (F3-F7, F9) and F10 (out of scope): do not re-raise them unless the fix changed
  them; a new finding is judged by the rules below like any other.
- This is the last round (DEC-1010): a finding that still blocks goes to the owner once, with options.
- Do not open, list or read anything under the evaluation sets' fixtures or any hidden folder: those paths appear only
  as strings in rules and tickets.
