# W2-04 (DAEO-u4oz) — the FULL review on the verified head, then DONE (the CTO, 2026-11-02)

**Read this first; it overrides the steps below where they differ.** Your verify run returned DONE at `b37b5c8f1741`
(`git rev-parse --short=12 HEAD` must show it, `git status --short` nothing; else return PACKAGES naming it). The
ticket is FULL, so it lands only with a passing independent review of that head (DEC-137, DEC-1010):
1. Launch one fresh independent reviewer (independent-auditor, `--effort max`, read-only) from your prepared
   `.gov-runtime/scratch/lead/briefs/rev-1.md` (it carries `JUDGEMENT.md` word for word; check that its probed
   commit is `b37b5c8f1741`). Its record ends with the structured `verdict` block (DEC-1010 item 1) and must fit
   `template/governance/kernel/schemas/probe.schema.json` (`type`, `task`, `reviewer_session`, `implementer_session`,
   `reviewer_wrote_nothing`, `commissioned_by`, `judged_by`, `judgement` one of pass/passed/fail/failed,
   `probed_commit`; W2-81's records failed exactly this last night).
2. Triage as the moderator rule says: a finding blocks only if in scope, ordinary work yes, and fails open or loses work.
   READY passes: commit the probe record under `docs/probes/DAEO-u4oz/` (records only) and return DONE with the head.
   A blocking finding: return PACKAGES with it (one repair round at most, then the owner).
3. No new test run and no rebuild: the code is what you verified. The shared embedding server is overloaded today;
   nothing in the review needs it.
- Also decided: P-W2-04-5 (DEC-1024, W2-120's sources fixed on `w2/integrate`); P-W2-04-4 (the embedder) is with the
  owner (P1-MORNING-2026-11-02 A); the W2-55 table follow-up is with the owner (item B).

---

