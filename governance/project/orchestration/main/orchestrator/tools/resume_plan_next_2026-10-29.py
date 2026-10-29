"""Replaces RESUME HERE's stale "Plan in force" and "Next" blocks (slip R17) with the state of 2026-10-29 13:40."""
import pathlib

CP = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CHECKPOINT.md")
NEW = """### Plan in force (DEC-933..DEC-939)
- **Merged, not closed (7):** W2-58 (re-close decided, DEC-939 item 3), W2-63, W2-07, W2-57 (re-probe run 4 after
  W2-68's merge), W2-67 r1 (rest held `d0140d4d`, probe stale), W2-75, W2-68 (batch off until W2-77). **Held, 10+ days
  stale:** W2-03, 05, 16, 20, 26, 37, 49, 51, 52 (merge-back each). W2-71 run 2 in flight (F1). Re-pin 3 = W2-68 + W2-71
  (+ W2-77 if ready); each judge improvement re-pinned as it lands (DEC-933).
- **Residual rows to file:** W2-72's F5-F8 etc.; W2-L452 (W2-58 review cases fail inside a Claude session); W2-68's
  F2-F6; W2-71's F2-F7; W2-57's P-1/P-2/P-R2-T1 for the digest.
- **Standing (summary):** full runs `-o tmp_path_retention_policy=failed` under `flock /tmp/gov-os-verify.lock`;
  rebuilds under `flock /tmp/gov-os-rebuild.lock` (DEC-939); tests/acceptance/ only by test designers (DEC-906);
  owner commits = ratchet, accepted_history, exemptions; remove returned leads' temp folders after a holder check.

### Next
1. **Queue end:** commit DEC-939 + DEC-940 (state request) + prompt v3.38 + LEAD-w2-common (rebuild lock, 01:00 cut-off,
   AND the guard's command-form rules: no $VAR write targets, heredocs, backticks, inline python with braces; slip S10)
   + rows + nightly folder (drafts/nightly-next2) + ACT-PUSHOVER-1; tk W2-76, W2-77; queue W2-58; leads W2-77, W2-76.
2. **STATE-OF-GOV-OS + re-plan + P-SCOPE-RECORDS-1 + P-TOOLS-REVIEW-1:** evidence in drafts/state/A..E; write the
   head (drafts/state/STATE-head.md); deliver in the first morning package after re-pin 3 (measured close times), at
   the latest 2026-11-01's.
3. ACT-REPIN-3, ACT-W2-57-LS-2, W2-67 merge-back + re-probe, then K4 (file W2-55, W2-61, W2-64; resume W2-03, W2-05,
   W2-37) and K3 (file W2-60, W2-56) leads in parallel up to the resource gate.
4. Next free: DEC-940; ticket W2-78; rows W2-M408, W2-L451 (drafted), W2-L452.
"""
lines = CP.read_text(encoding="utf-8").split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("### Plan in force"))
stop = next(i for i, l in enumerate(lines) if l.startswith("### Never"))
CP.write_text("\n".join(lines[:start] + NEW.split("\n") + lines[stop:]), encoding="utf-8")
print("replaced %d lines" % (stop - start))
