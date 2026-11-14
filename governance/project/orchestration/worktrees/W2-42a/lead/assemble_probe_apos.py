"""The narrow check's probe record: the lead's judgement, then the reviewer's return as returned."""
R = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/a4.result.md"
OUT = "/home/usain/gov-os-worktrees/W2-42a/docs/probes/DAEO-03ub/PR-DAEO-03ub-apos.md"
front = """---
type: probe
task: DAEO-03ub
reviewer_session: a84974e0-ecb1-4669-9d8d-39ecfbbd78cd
implementer_session: 5e9978c7-b620-45ea-8c22-c2ad2d95acc4
reviewer_wrote_nothing: true
commissioned_by: orchestrator (W2-42a ticket lead)
judged_by: orchestrator (W2-42a ticket lead)
judgement: fail
probed_commit: c1ee147bd61383cd29fcfd1998d2d2d514caceb8
decisions_applied: [DEC-1174, DEC-1164, DEC-409, DEC-1010, DEC-958, DEC-1028]
---

# Probe record: W2-42a (DAEO-03ub), the narrow independent check of the apostrophe fix (DEC-1164 (18), DEC-1174 (1))

## The lead's judgement

- **Who probed.** A fresh read-only independent auditor (Opus, high), launched by the ticket lead with
  `launch_worker.sh`; brief `.gov-runtime/scratch/lead/briefs/a4.md` (JUDGEMENT.md word for word); log
  `.gov-runtime/scratch/lead/log/a4.json`. It judged only the change bb464f2ca..c1ee147bd (the engineer's
  f16075e43, 669d87c91, c1ee147bd) against the cases' brief (a) to (d), the CTO's scope P-03ub-APOS-1 (A) and
  DEC-409. Its tripwire shows no change in W2-42a's trees; `git status` empty.
- **At this head:** `gov accept W2-42a` 803 passed, 0 failed, 2 skipped (the strict xfails); the scoped set
  (tests/unit/guard, tests/acceptance/W2-42a, tests/unit/hooks, DEC-409's cases in tests/unit/pause,
  tests/unit/containment/test_w1_50_freeze_flag.py, tests/acceptance/W1-50, W1-28, W2-16) 1809 passed, 2 xfailed,
  0 failed; with the opt-in tiers collected (GOV_TESTS_OPTIN=lifted,breadth) 3633 passed, 2 xfailed, 6 failed, the
  6 being W2-33's fixture copy (`tests/acceptance/W2-33/w2_33_support.py:376`, FileNotFoundError on the copied
  source's `template/governance/kernel/roles`), outside the guard and this change.
- **Not READY, by code.** The verdict block passes A, B, C, D, SCOPE and DEC409, and fails FC on F1: a `#` after a
  blank inside an unquoted `${…}` is taken for a comment and the write after it is dropped
  (`v='a # b'; echo ${v%% #*} > tests/acceptance/X/zz.py`: the base denies, the head allows, real bash writes);
  in scope, ordinary work yes, fails open. F2 (fails open, ordinary work no), F3, F4 and F5 (refuse work) are rows
  for triage; F6 (`bash <<< "…"`, pre-existing on the base) is out of scope.
- **Judgement: fail.** Returned to the CTO as a package (the triage and the options are in the lead's return).

## The reviewer's record (as returned)

"""
open(OUT, "w").write(front + open(R).read().rstrip() + "\n")
print("written", OUT)
