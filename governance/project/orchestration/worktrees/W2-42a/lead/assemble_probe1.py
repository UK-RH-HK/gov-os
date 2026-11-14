"""Round 1's probe record: the lead's judgement, then the reviewer's return as returned."""
R = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/a3-1.result.md"
OUT = "/home/usain/gov-os-worktrees/W2-42a/docs/probes/DAEO-03ub/PR-DAEO-03ub-round-1.md"
front = """---
type: probe
task: DAEO-03ub
reviewer_session: b4ed5672-cd89-4b89-a968-87b10525f0bf
implementer_session: not recorded (the engineer of 94c85f361 to ce03bb8b3, before the emergency's stop of 2026-11-02; its lead's logs were not kept)
reviewer_wrote_nothing: true
commissioned_by: orchestrator (W2-42a ticket lead, session w2-42a-f7)
judged_by: orchestrator (W2-42a ticket lead)
judgement: fail
probed_commit: e9e4f7bacf416016d995ac5190d8e05b644dce80
---

# Probe record: W2-42a (DAEO-03ub), FULL review, round 1 of at most 2 (DEC-1010)

## The lead's judgement

- **Who probed.** A fresh read-only independent auditor (Opus, high), launched by the ticket lead with
  `launch_worker.sh`; brief `.gov-runtime/scratch/lead/briefs/a3-1.md` (JUDGEMENT.md word for word); log
  `.gov-runtime/scratch/lead/log/a3-1.json`. Head `e9e4f7bac`: acceptance 452 passed, `gov accept` 452/0, the
  scoped set GREEN (6293 tests, 0 failed; serial 5 passed).
- **READY, by code.** The verdict block marks S1, S6 and failure line F1 fail, on finding F1: in scope, ordinary
  work yes, fails open. Not READY.
- **F1 (blocking).** `bash -euo pipefail <<'EOF'` and the other spellings that give the shell an option with a value
  read the heredoc body as data (`_kind`, `src/gov/guard/bash_writes.py:1116-1121`): no target, no sentinel, and the
  read judge drops the body; the base parser caught these writes. The finding went to the CTO at once (2026-11-13);
  the CTO confirmed one fix round for F1 only (DEC-802), with F4's `/dev/stdin` form riding along, and took the live
  hook's same gap by its own route.
- **Rows (DEC-801, DEC-808, DEC-1010).** F2, F3, F4, F5, F7 and F8 (ordinary work no, fails open) and F6 (ordinary
  work no, other: S11's listing rows and existing-root rows do not discriminate base from new since DEC-1070 moved
  the hidden parts out of the trees; the stand-in row 40 and the 155 planted cases do) are Wave 3 hardening rows,
  never a round.
- **Judgement: fail.** Round 2, the last, follows the F1 fix.

## The reviewer's record (as returned)

"""
open(OUT, "w").write(front + open(R).read().rstrip() + "\n")
print("written", OUT)
