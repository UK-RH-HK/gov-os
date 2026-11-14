"""Build docs/probes/DAEO-2bdu/PR-DAEO-2bdu.md: the lead's head (frontmatter, judgement, triage) + the checker's report unchanged."""
from pathlib import Path

LEAD = Path("/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead")
OUT = Path("/home/usain/gov-os-worktrees/W2-88/docs/probes/DAEO-2bdu/PR-DAEO-2bdu.md")
VERIFY = ("lead_verify (scoped, DEC-968) at 8f9571c7919d: RED, parallel 6,258 tests, 1 failed, 11 skipped, in 2,565 s; "
          "serial 3 passed (`.gov-runtime/scratch/lead/log/verify/parallel.xml`, `serial.xml`). The one failure is "
          "`tests/acceptance/W2-23/test_w2_23_space.py:94` (`context_watch.py` not in the settings' hook lines): a known "
          "red of the environment and integrate's, red in rounds 1 and 2 too, not this branch's (the CTO's, DEC-1156 (7)).")
head = (LEAD / "pr-nc-head.md").read_text(encoding="utf-8").replace("LEAD_VERIFY_LINE", VERIFY)
assert "LEAD_VERIFY_LINE" not in head
body = (LEAD / "log" / "nc-1.check.md").read_text(encoding="utf-8")
assert not OUT.exists(), OUT
OUT.write_text(head + body.rstrip("\n") + "\n", encoding="utf-8")
print(OUT, len(head) + len(body))
