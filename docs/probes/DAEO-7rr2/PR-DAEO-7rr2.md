---
type: probe
task: DAEO-7rr2
reviewer_session: ddd738a9-b979-4caf-a035-e94d3e084300
implementer_session: 08b55925-978d-4263-ac48-f061a9cf6693
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: c8d3fb308fd3178206a67ec8a842cdc2ae34089b
---

# Probe record: W2-53 (DAEO-7rr2), every later merge measured against git's own merge of its parents; DEC-757 item 2

- **What was probed.** The head `c8d3fb30` of `w2/W2-53`, read-only, on the worktree's own `src/` (DEC-732).
  - Suites run: W2-53's acceptance suite (57 passed), W2-01's suite with `tests/unit/close` (473 passed, 1 load-sensitive failure in an untouched file that passes alone), and W1-30's suite (512 passed).
  - 41 temporary repositories were built from scratch with the suite's support modules, and `gov close` was run in each. They cover:
    - later merges on the integration branch and inward: hand resolutions, conflicts inside and outside the probed paths, a mode change;
    - W2-L345, by hand and as a clean merge;
    - reopened tickets, including a round-one merge-back with a conflict;
    - non-merge commits under another ticket's task after the probe;
    - integration-side and other-side ticket-file edits, including changes to the profile and to wbs_id;
    - `accepted_reds`: non-owner, evil-merge, re-added, edited and forged entries, near ids, collection errors, crashes and teardown errors;
    - `load_sensitive`: prefix and parameter variants, setup errors, an entry on both lists.
- **What was found.**
  - Every case the KPI lines and DEC-757 item 2 hold behaves as stated. Every later merge holding the probed commit that is not git's own merge of its parents refuses, naming the merge, on the integration branch and inward. A conflicted merge is judged against the probed code. The ratchet's entry rules (R-2, R-3), the exact-id cover, the ratchet itself and the isolated re-run all hold.
  - W2-L345: a hand resolution to the integration side refuses. A clean merge that git resolves to the integration side closes, as P-5 (c) intends.
  - One KPI-3 case fails closed: a reopened ticket whose round-one merge-back git cannot merge cleanly cannot close, even though the head holds the final probed code.
  - Residuals, outside the KPI lines:
    - an integration-side ticket-file edit after the probe can change the profile (FULL to STANDARD) or the wbs_id, and so what is probed;
    - non-merge commits naming another ticket after the probe can delete or revert probed files or acceptance tests (DEC-490; the runtime guard and W1-50 at that ticket's close are the controls);
    - a ticket-file edit after the probe naming another ticket passes (P-3, untested);
    - `Role:` trailers are trusted as text at close (DEC-360; the runtime guard is the control);
    - a non-owner may edit an owner entry's reason and fixed_by;
    - R-2's file check is a substring test;
    - two cases fail closed: a listed red that also errors in teardown, and a test on both lists that fails alone.
- **Judgement.** pass. No finding loses work, lets an implementer change acceptance tests, or makes the guard or a gate fail open in a case the ticket's KPI lines or DEC-757 item 2 hold. The KPI-3 case fails closed. The residuals go to the list, and the change to probe scope through an integration-side edit goes to the owner as a package.
