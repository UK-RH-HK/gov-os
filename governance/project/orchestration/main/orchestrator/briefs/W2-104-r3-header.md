# W2-104 (DAEO-drhj) — run 3: two test fixtures that gitleaks reads as keys (the CTO, 2026-11-02)

**Read this first; it overrides the steps below where they differ.** Your run 2 returned DONE at `909d7ff0a926`
(head must show it, tree clean; else return PACKAGES naming it). The landing refused it before queueing: gitleaks
(`generic-api-key`, redacted) flags two literals in your change, both test fixtures, not secrets:
- your acceptance support file, line 85 (`REPLY_TOKEN`, commit `a0fa726f54cd`): the test designer's file;
- your unit test `tests/unit/skilleval/test_w2_104_skilleval.py`, line 20 (`SECRET`, the planted fake that must never
  reach the caller; commit `f3d8f608097b`): the engineer's file.
This repository allowlists only the known synthetic fixtures (`.gitleaks.toml`: "Nothing else is allowlisted"), so the
fix is at the source, not an allowlist entry and never a `gitleaks:allow` comment:
1. In parallel: the test designer (in this worktree, one writer at a time: designer first, then engineer, or a tests
   worktree) builds `REPLY_TOKEN` from parts at run time (for example two short literals joined), same value, same
   behaviour, `Rewrite-Reason: gitleaks fixture (CTO, 2026-11-02)`; the engineer does the same for `SECRET` in its
   unit test. Nothing else changes.
2. Check: `gitleaks git --no-banner --redact --log-opts "<merge-base>..HEAD" .` in this worktree finds nothing (print
   only the count, never a match); `gov accept` (all lines) and the unit file once. No scoped run is needed for a
   test-literal change (the CTO's call: the queue runs the selection on the merged result).
3. Return DONE with the exact head.

---

