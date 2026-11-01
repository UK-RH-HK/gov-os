"""Write review 3's probe record (DEC-733) from the reviewer's return: the fenced record, with the full probed commit
and the reviewer's session id alone, and the lead's judgement appended."""
import json
import subprocess
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-60a")
LOG = ROOT / ".gov-runtime/scratch/lead/log/b10-reviewer3.json"
OUT = ROOT / "docs/probes/DAEO-cv58/PR-DAEO-cv58.md"

text = LOG.read_text(encoding="utf-8")
result = None
for start in [i for i, ch in enumerate(text) if ch == "{"]:
    try:
        obj = json.loads(text[start:])
    except ValueError:
        continue
    result = obj.get("result")
    break
fence = "```\n---\ntype: probe"
begin = result.index(fence) + len("```\n")
end = result.index("\n```", begin)
record = result[begin:end] + "\n"
full = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "0e11b5db743d"], capture_output=True, text=True,
                      check=True).stdout.strip()
record = record.replace("probed_commit: 0e11b5db743d", f"probed_commit: {full}")
record = record.replace(
    "reviewer_session: 3c32abb2-c43a-41e3-96bd-43ac8f77e57b (from the CLI's session folder path; not stated in the "
    "environment)", "reviewer_session: 3c32abb2-c43a-41e3-96bd-43ac8f77e57b")
assert "probed_commit: " + full in record and "judgement: pass" in record
record += """
## The lead's judgement (JUDGEMENT.md)
- R3-1 and R3-2: "Ordinary work: no" with "fails open": rows for the Wave 3 hardening pass, never a round (DEC-801).
  R3-1 is an entry criterion (DEC-803) of any ticket that supports a gov project below its repository's git toplevel;
  R3-2 joins review 2's R4 (arguments on no refusal list; W2-56's refusal list).
- R3-3 and R3-4: "Ordinary work: yes" with "Consequence: other" (each fails closed): residuals.
- R3-5: "Ordinary work: no", "Consequence: other": a row.
- No finding has "yes" with "fails open" or "loses work": the probe passes. Review 3 was the ticket's last round
  (DEC-951 item 4).
"""
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(record, encoding="utf-8")
print(OUT, len(record))
