"""Draft of the failing probe record (DEC-733: only a passing record is committed). Hashes as 12 digits (DEC-911)."""
import json
import re
import sys
from pathlib import Path

log, out = sys.argv[1], Path(sys.argv[2])
text = open(log, encoding="utf-8").read()
dec = json.JSONDecoder()
last, i = None, 0
while True:
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = dec.raw_decode(text, j)
    except ValueError:
        i = j + 1
        continue
    if isinstance(obj, dict) and "result" in obj:
        last = obj
    i = end
body = last["result"]
body = body[body.index("Probed head"):]
body = re.sub(r"\b([0-9a-f]{12})[0-9a-f]{28}\b", r"\1", body)
front = "\n".join([
    "---",
    "type: probe",
    "task: DAEO-u4oz",
    f"reviewer_session: {last['session_id']}",
    "implementer_session: f5463fda-38ba-4f6d-babf-5f8ddfe97366",
    "reviewer_wrote_nothing: true",
    "commissioned_by: orchestrator",
    "judged_by: orchestrator",
    "judgement: fail",
    "probed_commit: b37b5c8f1741 (12 digits in this draft, DEC-911; the full id in a committed record)",
    "---",
    "",
    "# DRAFT, not committed: review 1 of W2-04 (DAEO-u4oz) at b37b5c8f1741, judgement fail (F1 blocks)",
    "",
    "READY by verdict.py: False (success-5: F1 blocks, in scope, ordinary work, fails open).",
    "The lead's triage (moderator rule, DEC-1010 item 1): F1 blocks (it is row W2-H034's own symptom, KPI 5);",
    "F2, F3, F6 in scope, other: rows (may ride with the repair, DEC-802); F4, F5 out of scope: rows / packages.",
    "",
])
out.write_text(front + body + "\n", encoding="utf-8")
print("draft", out, len(body))
